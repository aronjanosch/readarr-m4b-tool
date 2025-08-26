"""Simple configuration management for ReadarrM4B"""

import os
import yaml
from pathlib import Path


class Config:
    """Simple configuration class"""
    
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "config.yaml"
        
        self.config_file = Path(config_file)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Paths
        self.audiobooks_path = os.path.expandvars(config['paths']['audiobooks'])
        self.temp_dir = os.path.expandvars(config['paths'].get('temp_dir', '/tmp/readarr-m4b'))
        
        # Conversion settings
        conversion = config.get('conversion', {})
        self.audio_codec = conversion.get('audio_codec', None)  # Use m4b-tool default
        self.jobs = conversion.get('jobs', 4)
        self.use_filenames_as_chapters = conversion.get('use_filenames_as_chapters', True)
        self.no_chapter_reindexing = conversion.get('no_chapter_reindexing', True)
        self.skip_cover = conversion.get('skip_cover', False)
        self.stability_wait_seconds = conversion.get('stability_wait_seconds', 30)
        self.cleanup_originals = conversion.get('cleanup_originals', True)
        
        # Logging
        logging = config.get('logging', {})
        self.log_level = logging.get('level', 'INFO')
        self.log_file = os.path.expandvars(logging.get('file', './readarr-m4b.log'))
        
        # Webhook
        webhook = config.get('webhook', {})
        self.webhook_port = webhook.get('port', 8080)
        self.webhook_host = webhook.get('host', '0.0.0.0')
        self.webhook_log_file = os.path.expandvars(webhook.get('log_file', './webhook_requests.log'))
        self.webhook_json_file = os.path.expandvars(webhook.get('json_file', './webhook_received.json'))
    
    def validate(self):
        """Validate configuration"""
        errors = []
        
        # Check audiobooks path
        if not Path(self.audiobooks_path).exists():
            errors.append(f"Audiobooks directory does not exist: {self.audiobooks_path}")
        
        # Create temp directory if needed
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        
        # Check log level
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            errors.append(f"Invalid logging level: {self.log_level}")
        
        if errors:
            for error in errors:
                print(f"Configuration error: {error}")
            return False
        
        print("✅ Configuration is valid")
        return True
    
    def get_m4b_tool_args(self):
        """Get m4b-tool command arguments"""
        args = [
            "--jobs", str(self.jobs),
            "-n", "-v"  # no interaction, verbose
        ]
        
        # Only add audio codec if specified
        if self.audio_codec:
            args.extend(["--audio-codec", self.audio_codec])
        
        if self.use_filenames_as_chapters:
            args.append("--use-filenames-as-chapters")
        
        if self.no_chapter_reindexing:
            args.append("--no-chapter-reindexing")
        
        if self.skip_cover:
            args.append("--skip-cover")
        
        return args