#!/usr/bin/env python3
"""
Tests for configuration module
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config, PathConfig, ConversionConfig, LoggingConfig


class TestConfig(unittest.TestCase):
    """Test configuration functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.yaml"
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_path_config_defaults(self):
        """Test PathConfig with defaults"""
        config = PathConfig(audiobooks="/test/audiobooks")
        
        self.assertEqual(config.audiobooks, "/test/audiobooks")
        self.assertEqual(config.temp_dir, "/tmp/readarr-m4b")
    
    def test_conversion_config_defaults(self):
        """Test ConversionConfig with defaults"""
        config = ConversionConfig()
        
        self.assertEqual(config.audio_codec, "libfdk_aac")
        self.assertEqual(config.jobs, 4)
        self.assertTrue(config.use_filenames_as_chapters)
        self.assertTrue(config.cleanup_originals)
        self.assertEqual(config.stability_wait_seconds, 30)
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig with defaults"""
        config = LoggingConfig()
        
        self.assertEqual(config.level, "INFO")
        self.assertEqual(config.file, "/var/log/readarr-m4b.log")
    
    def test_config_file_loading(self):
        """Test loading configuration from YAML file"""
        # Create test config file
        config_content = """
paths:
  audiobooks: "/test/audiobooks"
  temp_dir: "/test/temp"

conversion:
  audio_codec: "aac"
  jobs: 2
  cleanup_originals: false

logging:
  level: "DEBUG"
  file: "/test/log.log"
"""
        
        with open(self.config_file, 'w') as f:
            f.write(config_content)
        
        config = Config(str(self.config_file))
        
        self.assertEqual(config.paths.audiobooks, "/test/audiobooks")
        self.assertEqual(config.paths.temp_dir, "/test/temp")
        self.assertEqual(config.conversion.audio_codec, "aac")
        self.assertEqual(config.conversion.jobs, 2)
        self.assertFalse(config.conversion.cleanup_originals)
        self.assertEqual(config.logging.level, "DEBUG")
        self.assertEqual(config.logging.file, "/test/log.log")
    
    def test_config_file_not_found(self):
        """Test handling of missing config file"""
        with self.assertRaises(FileNotFoundError):
            Config("/non/existent/config.yaml")
    
    def test_m4b_tool_args_generation(self):
        """Test m4b-tool command arguments generation"""
        config = Config.__new__(Config)
        config.conversion = ConversionConfig()
        
        args = config.get_m4b_tool_args()
        
        self.assertIn("--audio-codec", args)
        self.assertIn("libfdk_aac", args)
        self.assertIn("--jobs", args)
        self.assertIn("4", args)
        self.assertIn("-n", args)
        self.assertIn("-v", args)
        self.assertIn("--use-filenames-as-chapters", args)
        self.assertIn("--no-chapter-reindexing", args)
    
    def test_environment_variable_expansion(self):
        """Test environment variable expansion in paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['TEST_AUDIOBOOKS_PATH'] = temp_dir
            
            config = PathConfig(audiobooks="$TEST_AUDIOBOOKS_PATH")
            self.assertEqual(config.audiobooks, temp_dir)
            
            # Clean up
            del os.environ['TEST_AUDIOBOOKS_PATH']


if __name__ == '__main__':
    unittest.main(verbosity=2) 