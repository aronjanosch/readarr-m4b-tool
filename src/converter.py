"""M4B conversion logic for ReadarrM4B"""

import asyncio
import logging
import shutil
import time
from pathlib import Path
from typing import Optional, Dict, Any

from config import Config


class M4BConverter:
    """Handles audiobook conversion to M4B format"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def convert_audiobook(self, book_path: Path, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Convert audiobook to M4B format
        
        Args:
            book_path: Path to the audiobook directory
            metadata: Optional metadata from Readarr
            
        Returns:
            True if conversion successful, False otherwise
        """
        if not book_path.exists():
            self.logger.error(f"Audiobook path does not exist: {book_path}")
            return False
        
        self.logger.info(f"Starting conversion for: {book_path}")
        
        # Check if already converted
        if self._has_m4b_files(book_path):
            self.logger.info("M4B file already exists, skipping conversion")
            return True
        
        # Check if we have MP3 files to convert
        mp3_files = list(book_path.glob("*.mp3"))
        if not mp3_files:
            self.logger.warning(f"No MP3 files found in {book_path}")
            return False
        
        # Wait for file stability (ensure download is complete)
        if not await self._wait_for_stability(book_path):
            self.logger.error("Files not stable, conversion aborted")
            return False
        
        # Generate output filename
        output_filename = self._generate_output_filename(book_path, metadata)
        output_path = book_path / output_filename
        
        # Run conversion
        success = await self._run_m4b_tool(book_path, output_path)
        
        if success:
            # Cleanup original files if configured
            if self.config.conversion.cleanup_originals:
                self._cleanup_originals(book_path, mp3_files)
            
            self.logger.info(f"Conversion completed successfully: {output_filename}")
            return True
        else:
            self.logger.error("Conversion failed")
            return False
    
    def _has_m4b_files(self, book_path: Path) -> bool:
        """Check if directory already contains M4B files"""
        return len(list(book_path.glob("*.m4b"))) > 0
    
    async def _wait_for_stability(self, book_path: Path) -> bool:
        """
        Wait for file stability to ensure download is complete
        
        Returns:
            True if files are stable, False if timeout
        """
        wait_time = self.config.conversion.stability_wait_seconds
        self.logger.info(f"Waiting {wait_time} seconds for file stability...")
        
        # Get initial file info
        initial_files = self._get_file_info(book_path)
        
        await asyncio.sleep(wait_time)
        
        # Check if files changed
        final_files = self._get_file_info(book_path)
        
        if initial_files == final_files:
            self.logger.info("Files are stable, proceeding with conversion")
            return True
        else:
            self.logger.warning("Files still changing, may be incomplete download")
            # Wait a bit more and check again
            await asyncio.sleep(wait_time)
            retry_files = self._get_file_info(book_path)
            
            if final_files == retry_files:
                self.logger.info("Files stable after retry")
                return True
            else:
                self.logger.error("Files still changing after retry")
                return False
    
    def _get_file_info(self, book_path: Path) -> Dict[str, int]:
        """Get file sizes for stability checking"""
        file_info = {}
        for file_path in book_path.glob("*.mp3"):
            try:
                file_info[file_path.name] = file_path.stat().st_size
            except OSError:
                # File might be being written to
                file_info[file_path.name] = -1
        return file_info
    
    def _generate_output_filename(self, book_path: Path, metadata: Optional[Dict[str, Any]]) -> str:
        """Generate output filename for M4B file"""
        if metadata:
            author = metadata.get('author_name', '')
            title = metadata.get('book_title', '')
            if author and title:
                # Clean up title (handle colons, etc.)
                title = title.replace(':', ' -').strip()
                return f"{author} - {title}.m4b"
        
        # Fallback to directory name
        return f"{book_path.name}.m4b"
    
    async def _run_m4b_tool(self, source_path: Path, output_path: Path) -> bool:
        """
        Run m4b-tool to convert the audiobook
        
        Args:
            source_path: Directory containing MP3 files
            output_path: Output M4B file path
            
        Returns:
            True if successful, False otherwise
        """
        # Check if m4b-tool is available
        if not shutil.which("m4b-tool"):
            self.logger.error("m4b-tool not found in PATH")
            return False
        
        # Build command
        cmd = [
            "m4b-tool",
            "merge",
            str(source_path),
            "--output-file", str(output_path)
        ]
        
        # Add configuration options
        cmd.extend(self.config.get_m4b_tool_args())
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=source_path
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.logger.info("m4b-tool completed successfully")
                if stdout:
                    self.logger.debug(f"m4b-tool stdout: {stdout.decode()}")
                return True
            else:
                self.logger.error(f"m4b-tool failed with return code {process.returncode}")
                if stderr:
                    self.logger.error(f"m4b-tool stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error running m4b-tool: {e}")
            return False
    
    def _cleanup_originals(self, book_path: Path, mp3_files: list) -> None:
        """Remove original MP3 files after successful conversion"""
        self.logger.info("Cleaning up original MP3 files...")
        
        for mp3_file in mp3_files:
            try:
                mp3_file.unlink()
                self.logger.debug(f"Removed: {mp3_file.name}")
            except Exception as e:
                self.logger.warning(f"Could not remove {mp3_file.name}: {e}")
        
        self.logger.info(f"Cleaned up {len(mp3_files)} MP3 files") 