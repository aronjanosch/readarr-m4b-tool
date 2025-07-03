#!/usr/bin/env python3
"""
ReadarrM4B - Simple Audiobook Converter
Drop-in replacement for readarr.sh and related scripts
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional

from config import Config
from converter import M4BConverter
from utils import setup_logging


def get_readarr_info() -> Optional[dict]:
    """Extract audiobook info from Readarr environment variables"""
    author_name = os.getenv('readarr_author_name')
    book_title = os.getenv('readarr_book_title')
    author_path = os.getenv('readarr_author_path')
    event_type = os.getenv('readarr_eventtype', 'Import')
    
    # Handle test events
    if event_type == 'Test':
        return {
            'author_name': 'Test Author',
            'book_title': 'Test Book',
            'author_path': '/test/path',
            'is_test': True
        }
    
    if not author_name or not book_title:
        return None
        
    return {
        'author_name': author_name,
        'book_title': book_title,
        'author_path': author_path,
        'is_test': False
    }


async def main():
    """Main entry point - can be called directly by Readarr"""
    
    # Parse command line arguments
    mode = 'readarr'  # Default mode for Readarr integration
    target_path = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--mode':
            mode = sys.argv[2] if len(sys.argv) > 2 else 'readarr'
        elif sys.argv[1] == '--convert':
            mode = 'convert'
            target_path = sys.argv[2] if len(sys.argv) > 2 else None
        elif sys.argv[1] == '--test':
            mode = 'test'
    
    # Load configuration
    config = Config()
    setup_logging(config.logging.level, config.logging.file)
    logger = logging.getLogger(__name__)
    
    # Initialize converter
    converter = M4BConverter(config)
    
    if mode == 'readarr':
        # Called by Readarr - process environment variables
        readarr_info = get_readarr_info()
        if not readarr_info:
            logger.error("No valid Readarr information found in environment variables")
            sys.exit(1)
            
        if readarr_info['is_test']:
            logger.info("Readarr test event - configuration OK")
            sys.exit(0)
            
        # Build the audiobook path
        book_path = Path(config.paths.audiobooks) / readarr_info['author_name'] / readarr_info['book_title']
        
        logger.info(f"Processing audiobook: {readarr_info['author_name']} - {readarr_info['book_title']}")
        logger.info(f"Source path: {book_path}")
        
        # Convert the audiobook
        success = await converter.convert_audiobook(book_path, readarr_info)
        sys.exit(0 if success else 1)
        
    elif mode == 'convert':
        # Manual conversion mode
        if not target_path:
            logger.error("--convert requires a path argument")
            sys.exit(1)
            
        book_path = Path(target_path)
        success = await converter.convert_audiobook(book_path)
        sys.exit(0 if success else 1)
        
    elif mode == 'test':
        # Test configuration
        logger.info("Testing configuration...")
        if config.validate():
            logger.info("Configuration is valid")
            sys.exit(0)
        else:
            logger.error("Configuration is invalid")
            sys.exit(1)
    
    else:
        logger.error(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main()) 