#!/usr/bin/env python3
"""
Simple Vulnerable Application for AEGIS-X Testing
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import sqlite3
import os
import argparse

class VulnerableHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <html>
            <head><title>Vulnerable Test App</title></head>
            <body>
                <h1>Welcome to Vulnerable Test App</h1>
                <p>This app has intentional vulnerabilities for testing.</p>
                <ul>
                    <li><a href="/search?q=test">Search (XSS vulnerable)</a></li>
                    <li><a href="/user?id=1">User Profile (SQL Injection)</a></li>
                    <li><a href="/file?name=test.txt">File Read (LFI)</a></li>
                    <li><a href="/admin">Admin Panel (IDOR)</a></li>
                </ul>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            
        elif path == '/search':
            # XSS vulnerability
            q = query.get('q', [''])[0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f'''
            <html>
            <head><title>Search Results</title></head>
            <body>
                <h1>Search Results for: {q}</h1>
                <p>No results found for "{q}"</p>
                <script>alert('XSS: {q}')</script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            
        elif path == '/user':
            # SQL Injection vulnerability
            user_id = query.get('id', ['1'])[0]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Simulate vulnerable SQL query
            response = {
                'user_id': user_id,
                'username': f'user_{user_id}',
                'email': f'user_{user_id}@example.com',
                'sql_query': f"SELECT * FROM users WHERE id = {user_id}",
                'vulnerability': 'SQL Injection possible'
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/file':
            # Local File Inclusion vulnerability
            filename = query.get('name', ['test.txt'])[0]
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            try:
                # Vulnerable file read
                with open(filename, 'r') as f:
                    content = f.read()
                self.wfile.write(content.encode())
            except Exception as e:
                self.wfile.write(f"Error reading file {filename}: {str(e)}".encode())
                
        elif path == '/admin':
            # IDOR vulnerability
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <html>
            <head><title>Admin Panel</title></head>
            <body>
                <h1>Admin Panel</h1>
                <p>Welcome to the admin panel!</p>
                <p>This should require authentication but doesn't.</p>
                <h2>Sensitive Information</h2>
                <p>Database password: super_secret_password</p>
                <p>API Key: sk-1234567890abcdef</p>
                <p>Admin Token: admin_token_12345</p>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 Not Found</h1>')
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if self.path == '/login':
            # Command injection vulnerability
            try:
                data = json.loads(post_data.decode())
                username = data.get('username', '')
                password = data.get('password', '')
                
                # Vulnerable command execution
                import subprocess
                result = subprocess.run(f"echo 'Login attempt: {username}'", shell=True, capture_output=True, text=True)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'message': f'Login processed for {username}',
                    'command_output': result.stdout,
                    'vulnerability': 'Command injection possible'
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 Not Found</h1>')

def run_server(host='0.0.0.0', port=12005):
    server_address = (host, port)
    httpd = HTTPServer(server_address, VulnerableHandler)
    print(f"Starting vulnerable server on {host}:{port}")
    print(f"Visit http://{host}:{port} to access the vulnerable application")
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Vulnerable Test Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=12005, help='Port to bind to')
    args = parser.parse_args()
    
    run_server(args.host, args.port)