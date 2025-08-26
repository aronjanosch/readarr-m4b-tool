#!/usr/bin/env python3
"""
Simple webhook testing server to capture and log Readarr webhook data.
This helps understand the exact format of webhook payloads before implementing.
"""

import json
import logging
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path


class WebhookTestHandler(BaseHTTPRequestHandler):
    """Simple handler that logs all webhook data"""
    
    def do_POST(self):
        """Log POST request data"""
        try:
            # Get request info
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Log headers
            headers_info = dict(self.headers)
            
            # Try to parse JSON data
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                data_readable = json.dumps(json_data, indent=2)
            except json.JSONDecodeError:
                json_data = None
                data_readable = post_data.decode('utf-8', errors='replace')
            
            # Create log entry
            timestamp = datetime.now().isoformat()
            log_entry = f"""
=== WEBHOOK RECEIVED at {timestamp} ===
Path: {self.path}
Method: {self.command}
Headers: {json.dumps(headers_info, indent=2)}
Content-Length: {content_length}
Raw Data: {post_data.hex()}
Decoded Data:
{data_readable}
=======================================
"""
            
            # Log to console
            print(log_entry)
            
            # Log to file
            log_file = Path("webhook_test.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "received", "message": "Data logged successfully"}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error processing request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_GET(self):
        """Handle GET requests - show simple status"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        response = """
        <h1>Readarr Webhook Test Server</h1>
        <p>Server is running and ready to receive webhooks.</p>
        <p>POST requests will be logged to console and webhook_test.log</p>
        <p>Send webhooks to this server's address.</p>
        """
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override to reduce noise in console"""
        pass


def main():
    """Start the webhook test server"""
    port = 8080
    
    # Clear previous log
    log_file = Path("webhook_test.log")
    if log_file.exists():
        log_file.unlink()
    
    print(f"Starting Readarr webhook test server on port {port}")
    print(f"Webhook data will be logged to: {log_file.absolute()}")
    print("Configure Readarr webhook to point to: http://your-server:8080")
    print("Press Ctrl+C to stop\n")
    
    server = HTTPServer(('0.0.0.0', port), WebhookTestHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == '__main__':
    main()