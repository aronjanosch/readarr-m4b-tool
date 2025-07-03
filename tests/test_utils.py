#!/usr/bin/env python3
"""
Tests for utility functions
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import sanitize_filename, format_duration, format_size, get_directory_size


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ("normal_filename.txt", "normal_filename.txt"),
            ("file:with:colons.txt", "file - with - colons.txt"),
            ("file/with/slashes.txt", "file-with-slashes.txt"),
            ("file<with>brackets.txt", "filewithbrackets.txt"),
            ("file|with|pipes.txt", "file-with-pipes.txt"),
            ("file?with?questions.txt", "filewithquestions.txt"),
            ("file*with*asterisks.txt", "filewithasterisks.txt"),
            ("file\"with\"quotes.txt", "filewithquotes.txt"),
            ("file\nwith\nnewlines.txt", "file with newlines.txt"),
            ("  spaced  file  .txt  ", "spaced file .txt"),
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = sanitize_filename(original)
                self.assertEqual(result, expected)
    
    def test_format_duration(self):
        """Test duration formatting"""
        test_cases = [
            (0, "0s"),
            (30, "30s"),
            (60, "1m 0s"),
            (90, "1m 30s"),
            (3600, "1h 0m 0s"),
            (3661, "1h 1m 1s"),
            (7323, "2h 2m 3s"),
        ]
        
        for seconds, expected in test_cases:
            with self.subTest(seconds=seconds):
                result = format_duration(seconds)
                self.assertEqual(result, expected)
    
    def test_format_size(self):
        """Test size formatting"""
        test_cases = [
            (0, "0 B"),
            (512, "512 B"),
            (1024, "1.0 KB"),
            (1536, "1.5 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
            (1099511627776, "1.0 TB"),
        ]
        
        for size_bytes, expected in test_cases:
            with self.subTest(size_bytes=size_bytes):
                result = format_size(size_bytes)
                self.assertEqual(result, expected)
    
    def test_get_directory_size(self):
        """Test directory size calculation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "file1.txt").write_text("Hello World")  # 11 bytes
            (temp_path / "file2.txt").write_text("Test")  # 4 bytes
            
            # Create subdirectory with file
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()
            (sub_dir / "file3.txt").write_text("Sub")  # 3 bytes
            
            total_size = get_directory_size(temp_path)
            
            # Should be at least 18 bytes (11 + 4 + 3)
            self.assertGreaterEqual(total_size, 18)
    
    def test_get_directory_size_empty(self):
        """Test directory size for empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            size = get_directory_size(temp_path)
            self.assertEqual(size, 0)
    
    def test_get_directory_size_nonexistent(self):
        """Test directory size for non-existent directory"""
        nonexistent_path = Path("/non/existent/path")
        size = get_directory_size(nonexistent_path)
        self.assertEqual(size, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2) 