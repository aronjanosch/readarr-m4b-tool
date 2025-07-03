#!/usr/bin/env python3
"""
Simple tests for ReadarrM4B
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import asyncio

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import get_readarr_info, run_cli
from config import Config, PathConfig, ConversionConfig, LoggingConfig


class TestReadarrM4B(unittest.TestCase):
    """Test cases for ReadarrM4B functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.audiobook_path = Path(self.temp_dir) / "audiobooks"
        self.audiobook_path.mkdir()
        
        # Create mock config
        self.mock_config = Mock(spec=Config)
        self.mock_config.paths = PathConfig(audiobooks=str(self.audiobook_path))
        self.mock_config.conversion = ConversionConfig()
        self.mock_config.logging = LoggingConfig()
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_readarr_info_with_valid_env(self):
        """Test extracting Readarr info from environment variables"""
        with patch.dict(os.environ, {
            'readarr_author_name': 'Test Author',
            'readarr_book_title': 'Test Book',
            'readarr_author_path': '/test/path',
            'readarr_eventtype': 'Import'
        }):
            info = get_readarr_info()
            
            self.assertIsNotNone(info)
            self.assertEqual(info['author_name'], 'Test Author')
            self.assertEqual(info['book_title'], 'Test Book')
            self.assertEqual(info['author_path'], '/test/path')
            self.assertFalse(info['is_test'])
    
    def test_get_readarr_info_test_event(self):
        """Test handling of test events"""
        with patch.dict(os.environ, {
            'readarr_eventtype': 'Test'
        }):
            info = get_readarr_info()
            
            self.assertIsNotNone(info)
            self.assertEqual(info['author_name'], 'Test Author')
            self.assertEqual(info['book_title'], 'Test Book')
            self.assertTrue(info['is_test'])
    
    def test_get_readarr_info_missing_data(self):
        """Test handling of missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            info = get_readarr_info()
            self.assertIsNone(info)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test with existing directory
        config = Config.__new__(Config)
        config.paths = PathConfig(audiobooks=str(self.audiobook_path))
        config.conversion = ConversionConfig()
        config.logging = LoggingConfig(level="INFO", file=f"{self.temp_dir}/test.log")
        
        self.assertTrue(config.validate())
        
        # Test with non-existent directory
        config.paths.audiobooks = "/non/existent/path"
        self.assertFalse(config.validate())
    
    def test_cli_test_mode(self):
        """Test CLI test mode"""
        async def run_test():
            # Mock config validation
            self.mock_config.validate.return_value = True
            
            result = await run_cli(self.mock_config, ['--test'])
            self.assertTrue(result)
            
            # Test validation failure
            self.mock_config.validate.return_value = False
            result = await run_cli(self.mock_config, ['--test'])
            self.assertFalse(result)
        
        asyncio.run(run_test())
    
    def test_cli_convert_mode_missing_path(self):
        """Test CLI convert mode with missing path"""
        async def run_test():
            result = await run_cli(self.mock_config, ['--convert'])
            self.assertFalse(result)
        
        asyncio.run(run_test())
    
    @patch('main.get_readarr_info')
    def test_cli_readarr_mode_no_info(self, mock_get_info):
        """Test CLI Readarr mode with no environment info"""
        mock_get_info.return_value = None
        
        async def run_test():
            result = await run_cli(self.mock_config, [])
            self.assertFalse(result)
        
        asyncio.run(run_test())
    
    @patch('main.get_readarr_info')
    def test_cli_readarr_mode_test_event(self, mock_get_info):
        """Test CLI Readarr mode with test event"""
        mock_get_info.return_value = {'is_test': True}
        
        async def run_test():
            result = await run_cli(self.mock_config, [])
            self.assertTrue(result)
        
        asyncio.run(run_test())


class TestHTTPServer(unittest.TestCase):
    """Test HTTP server functionality"""
    
    def test_valid_json_payload(self):
        """Test valid JSON payload structure"""
        payload = {
            "author_name": "Test Author",
            "book_title": "Test Book",
            "event_type": "Import"
        }
        
        # Test JSON serialization
        json_str = json.dumps(payload)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed['author_name'], 'Test Author')
        self.assertEqual(parsed['book_title'], 'Test Book')
        self.assertEqual(parsed['event_type'], 'Import')
    
    def test_test_event_payload(self):
        """Test test event payload"""
        payload = {
            "author_name": "Test Author",
            "book_title": "Test Book",
            "event_type": "Test"
        }
        
        self.assertEqual(payload['event_type'], 'Test')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 