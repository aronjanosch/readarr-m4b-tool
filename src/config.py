"""Configuration management for ReadarrM4B"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PathConfig:
    """Path configuration"""
    audiobooks: str
    temp_dir: str = "/tmp/readarr-m4b"
    
    def __post_init__(self):
        """Expand environment variables in paths"""
        self.audiobooks = os.path.expandvars(self.audiobooks)
        self.temp_dir = os.path.expandvars(self.temp_dir)


@dataclass
class ConversionConfig:
    """Conversion settings"""
    audio_codec: str = "libfdk_aac"
    jobs: int = 4
    use_filenames_as_chapters: bool = True
    no_chapter_reindexing: bool = True
    skip_cover: bool = False
    stability_wait_seconds: int = 30
    cleanup_originals: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "/var/log/readarr-m4b.log"
    
    def __post_init__(self):
        """Expand environment variables in file path"""
        self.file = os.path.expandvars(self.file)


class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            # Default config file location
            config_file = Path(__file__).parent.parent / "config" / "config.yaml"
        
        self.config_file = Path(config_file)
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Load configuration sections
        self.paths = PathConfig(**config_data.get('paths', {}))
        self.conversion = ConversionConfig(**config_data.get('conversion', {}))
        self.logging = LoggingConfig(**config_data.get('logging', {}))
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check if audiobooks path exists
        audiobooks_path = Path(self.paths.audiobooks)
        if not audiobooks_path.exists():
            errors.append(f"Audiobooks directory does not exist: {self.paths.audiobooks}")
        
        # Check if audiobooks path is writable
        if audiobooks_path.exists() and not os.access(audiobooks_path, os.W_OK):
            errors.append(f"Audiobooks directory is not writable: {self.paths.audiobooks}")
        
        # Check temp directory
        temp_path = Path(self.paths.temp_dir)
        try:
            temp_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            errors.append(f"Cannot create temp directory: {self.paths.temp_dir}")
        
        # Validate logging configuration
        if self.logging.level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            errors.append(f"Invalid logging level: {self.logging.level}")
        
        # Check if log directory is writable
        log_file = Path(self.logging.file)
        log_dir = log_file.parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                errors.append(f"Cannot create log directory: {log_dir}")
        
        if errors:
            for error in errors:
                print(f"Configuration error: {error}")
            return False
        
        return True
    
    def get_m4b_tool_args(self) -> list:
        """Get m4b-tool command arguments from configuration"""
        args = [
            "--audio-codec", self.conversion.audio_codec,
            "--jobs", str(self.conversion.jobs),
            "-n",  # no interaction
            "-v"   # verbose
        ]
        
        if self.conversion.use_filenames_as_chapters:
            args.append("--use-filenames-as-chapters")
        
        if self.conversion.no_chapter_reindexing:
            args.append("--no-chapter-reindexing")
        
        if self.conversion.skip_cover:
            args.append("--skip-cover")
        
        return args 