#!/usr/bin/env python3
"""
ReadarrM4B - Unified Audiobook Converter
Supports both CLI and HTTP API modes
"""

import asyncio
import json
import logging
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

from config import Config
from converter import M4BConverter
from utils import setup_logging


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for audiobook conversion"""
    
    def do_POST(self):
        """Handle POST requests with audiobook conversion data"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            author_name = data.get('author_name')
            book_title = data.get('book_title')
            event_type = data.get('event_type', 'Import')
            
            self.server.logger.info(f"Received: {author_name} - {book_title}")
            
            # Handle test events
            if event_type == 'Test':
                self._send_json_response(200, {'status': 'success', 'message': 'Test successful'})
                return
            
            if not author_name or not book_title:
                self._send_json_response(400, {'error': 'Missing author_name or book_title'})
                return
            
            # Queue conversion
            metadata = {
                'author_name': author_name,
                'book_title': book_title,
                'author_path': data.get('author_path'),
                'is_test': False
            }
            
            asyncio.create_task(self._convert_audiobook(metadata))
            self._send_json_response(202, {'status': 'accepted', 'message': 'Conversion queued'})
            
        except Exception as e:
            self.server.logger.error(f"Request error: {e}")
            self._send_json_response(500, {'error': str(e)})
    
    def _send_json_response(self, status_code: int, data: dict):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    async def _convert_audiobook(self, metadata: dict):
        """Convert audiobook asynchronously"""
        try:
            book_path = Path(self.server.config.paths.audiobooks) / metadata['author_name'] / metadata['book_title']
            success = await self.server.converter.convert_audiobook(book_path, metadata)
            
            if success:
                self.server.logger.info(f"✅ Conversion completed: {book_path}")
            else:
                self.server.logger.error(f"❌ Conversion failed: {book_path}")
        except Exception as e:
            self.server.logger.error(f"Conversion error: {e}")
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        self.server.logger.info(format % args)


class ReadarrM4BServer(HTTPServer):
    """HTTP server with configuration and converter"""
    
    def __init__(self, server_address, handler_class, config: Config):
        super().__init__(server_address, handler_class)
        self.config = config
        self.converter = M4BConverter(config)
        self.logger = logging.getLogger(__name__)


def get_readarr_info() -> Optional[dict]:
    """Extract audiobook info from Readarr environment variables"""
    author_name = os.getenv('readarr_author_name')
    book_title = os.getenv('readarr_book_title')
    author_path = os.getenv('readarr_author_path')
    event_type = os.getenv('readarr_eventtype', 'Import')
    
    if event_type == 'Test':
        return {'author_name': 'Test Author', 'book_title': 'Test Book', 'is_test': True}
    
    if not author_name or not book_title:
        return None
        
    return {
        'author_name': author_name,
        'book_title': book_title,
        'author_path': author_path,
        'is_test': False
    }


async def run_server(config: Config):
    """Run HTTP server mode"""
    logger = logging.getLogger(__name__)
    port = int(os.getenv('WEBHOOK_PORT', 8080))
    
    server = ReadarrM4BServer(('0.0.0.0', port), WebhookHandler, config)
    logger.info(f"🚀 ReadarrM4B HTTP server started on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.server_close()


async def run_cli(config: Config, args: list):
    """Run CLI mode"""
    logger = logging.getLogger(__name__)
    converter = M4BConverter(config)
    
    if '--convert' in args:
        # Manual conversion
        try:
            path_index = args.index('--convert') + 1
            target_path = args[path_index] if path_index < len(args) else None
        except (IndexError, ValueError):
            target_path = None
            
        if not target_path:
            logger.error("--convert requires a path argument")
            return False
            
        book_path = Path(target_path)
        return await converter.convert_audiobook(book_path)
    
    elif '--test' in args:
        # Test configuration
        logger.info("Testing configuration...")
        return config.validate()
    
    else:
        # Readarr mode (environment variables)
        readarr_info = get_readarr_info()
        if not readarr_info:
            logger.error("No valid Readarr information found")
            return False
            
        if readarr_info['is_test']:
            logger.info("Readarr test event - OK")
            return True
            
        book_path = Path(config.paths.audiobooks) / readarr_info['author_name'] / readarr_info['book_title']
        logger.info(f"Processing: {readarr_info['author_name']} - {readarr_info['book_title']}")
        
        return await converter.convert_audiobook(book_path, readarr_info)


async def main():
    """Main entry point - unified CLI and HTTP server"""
    config = Config()
    setup_logging(config.logging.level, config.logging.file)
    logger = logging.getLogger(__name__)
    
    # Determine mode
    if '--server' in sys.argv or len(sys.argv) == 1:
        # HTTP server mode (default)
        await run_server(config)
    else:
        # CLI mode
        success = await run_cli(config, sys.argv)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main()) 