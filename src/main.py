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
            
            # Log full request to dedicated webhook log file
            webhook_log_file = Path(self.server.config.webhook_log_file)
            with open(webhook_log_file, "a") as f:
                f.write(f"\n=== WEBHOOK RECEIVED {self._get_timestamp()} ===\n")
                f.write(f"Headers: {dict(self.headers)}\n")
                f.write(f"Data: {json.dumps(data, indent=2)}\n")
                f.write("=" * 50 + "\n")
            
            # Also save JSON for debugging
            webhook_json_file = Path(self.server.config.webhook_json_file)
            with open(webhook_json_file, "w") as f:
                json.dump(data, f, indent=2)
            
            self.server.webhook_logger.info(f"Full webhook data saved to: {webhook_json_file}")
            
            # Extract data from Readarr webhook format
            author_data = data.get('author', {})
            book_data = data.get('book', {})
            event_type = data.get('eventType', 'Import')
            
            author_name = author_data.get('name')
            author_path = author_data.get('path')
            book_title = book_data.get('title')
            
            self.server.webhook_logger.info(f"Received webhook - Author: {author_name}, Book: {book_title}, Event: {event_type}")
            
            # Handle test events
            if event_type == 'Test':
                self._send_json_response(200, {'status': 'success', 'message': 'Test successful'})
                return
            
            if not author_name or not book_title:
                self._send_json_response(400, {'error': 'Missing author name or book title in webhook'})
                return
            
            # Get the directory path from the first book file
            book_files = data.get('bookFiles', [])
            book_directory = None
            if book_files:
                first_file_path = book_files[0].get('path', '')
                if first_file_path:
                    book_directory = str(Path(first_file_path).parent)
            
            if not book_directory:
                self._send_json_response(400, {'error': 'Could not determine book directory from bookFiles'})
                return
            
            # Queue conversion
            metadata = {
                'author_name': author_name,
                'book_title': book_title,
                'author_path': author_path,
                'book_directory': book_directory,
                'is_test': False
            }
            
            self.server.webhook_logger.info(f"Queueing conversion for directory: {book_directory}")
            asyncio.create_task(self._convert_audiobook(metadata))
            self._send_json_response(202, {'status': 'accepted', 'message': 'Conversion queued'})
            
        except Exception as e:
            self.server.webhook_logger.error(f"Request error: {e}")
            self._send_json_response(500, {'error': str(e)})
    
    def _get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _send_json_response(self, status_code: int, data: dict):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    async def _convert_audiobook(self, metadata: dict):
        """Convert audiobook asynchronously"""
        try:
            book_path = Path(metadata['book_directory'])
            self.server.webhook_logger.info(f"Starting conversion for: {book_path}")
            success = await self.server.converter.convert_audiobook(book_path, metadata)
            
            if success:
                self.server.webhook_logger.info(f"✅ Conversion completed: {book_path}")
            else:
                self.server.webhook_logger.error(f"❌ Conversion failed: {book_path}")
        except Exception as e:
            self.server.webhook_logger.error(f"Conversion error: {e}")
    
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
        
        # Setup dedicated webhook logger
        self.webhook_logger = logging.getLogger('webhook')
        webhook_handler = logging.FileHandler(config.webhook_log_file)
        webhook_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.webhook_logger.addHandler(webhook_handler)
        self.webhook_logger.setLevel(logging.INFO)




async def run_server(config: Config):
    """Run HTTP server mode"""
    logger = logging.getLogger(__name__)
    
    server = ReadarrM4BServer((config.webhook_host, config.webhook_port), WebhookHandler, config)
    logger.info(f"🚀 ReadarrM4B HTTP server started on {config.webhook_host}:{config.webhook_port}")
    
    try:
        # Run server in a thread to not block the asyncio event loop
        import threading
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Keep the main coroutine running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.server_close()


async def run_cli(config: Config, args: list):
    """Run CLI mode for testing and manual conversion"""
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
        logger.error("Invalid CLI usage. Use --server for webhook mode, --test for config validation, or --convert <path> for manual conversion.")
        return False


async def main():
    """Main entry point - webhook server focused"""
    config = Config()
    setup_logging(config.log_level, config.log_file)
    logger = logging.getLogger(__name__)
    
    # Determine mode
    if '--server' in sys.argv or len(sys.argv) == 1:
        # HTTP server mode (default - webhook focused)
        await run_server(config)
    else:
        # CLI mode (testing and manual conversion only)
        success = await run_cli(config, sys.argv)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main()) 