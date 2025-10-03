#!/usr/bin/env python3
"""
Advanced Vulnerable Test Application for AEGIS-X Testing
Contains multiple real-world vulnerabilities for comprehensive testing
"""

from flask import Flask, request, render_template_string, redirect, session, jsonify, make_response
import sqlite3
import os
import subprocess
import pickle
import base64
import hashlib
import jwt
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging

app = Flask(__name__)
app.secret_key = "super_secret_key_123"  # Weak secret key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLite database with vulnerable schema
def init_db():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    # Vulnerable users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Insert test data
    cursor.execute("INSERT OR REPLACE INTO users VALUES (1, 'admin', 'password123', 'admin@test.com', 'admin')")
    cursor.execute("INSERT OR REPLACE INTO users VALUES (2, 'user', 'user123', 'user@test.com', 'user')")
    cursor.execute("INSERT OR REPLACE INTO users VALUES (3, 'guest', 'guest', 'guest@test.com', 'guest')")
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return '''
    <h1>Advanced Vulnerable Test Application</h1>
    <p>This application contains multiple vulnerabilities for testing:</p>
    <ul>
        <li><a href="/sql">SQL Injection</a></li>
        <li><a href="/xss">Cross-Site Scripting</a></li>
        <li><a href="/ssrf">Server-Side Request Forgery</a></li>
        <li><a href="/lfi">Local File Inclusion</a></li>
        <li><a href="/rce">Remote Code Execution</a></li>
        <li><a href="/xxe">XML External Entity</a></li>
        <li><a href="/deserialization">Insecure Deserialization</a></li>
        <li><a href="/jwt">JWT Vulnerabilities</a></li>
        <li><a href="/idor">Insecure Direct Object Reference</a></li>
        <li><a href="/csrf">Cross-Site Request Forgery</a></li>
        <li><a href="/upload">File Upload</a></li>
        <li><a href="/api/users">API Endpoints</a></li>
    </ul>
    '''

# SQL Injection Vulnerability
@app.route('/sql')
def sql_page():
    return '''
    <h2>SQL Injection Test</h2>
    <form action="/sql/search" method="GET">
        <input type="text" name="username" placeholder="Enter username">
        <input type="submit" value="Search">
    </form>
    '''

@app.route('/sql/search')
def sql_search():
    username = request.args.get('username', '')
    
    # Vulnerable SQL query - direct string concatenation
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM users WHERE username = '{username}'"
        logger.info(f"Executing query: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        
        response = "<h3>Search Results:</h3>"
        for row in results:
            response += f"<p>ID: {row[0]}, Username: {row[1]}, Email: {row[3]}, Role: {row[4]}</p>"
        
        return response
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        conn.close()

# XSS Vulnerability
@app.route('/xss')
def xss_page():
    return '''
    <h2>Cross-Site Scripting Test</h2>
    <form action="/xss/reflect" method="GET">
        <input type="text" name="message" placeholder="Enter message">
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/xss/reflect')
def xss_reflect():
    message = request.args.get('message', '')
    # Vulnerable - no sanitization
    return f"<h3>Your message: {message}</h3>"

# SSRF Vulnerability
@app.route('/ssrf')
def ssrf_page():
    return '''
    <h2>Server-Side Request Forgery Test</h2>
    <form action="/ssrf/fetch" method="POST">
        <input type="text" name="url" placeholder="Enter URL to fetch">
        <input type="submit" value="Fetch">
    </form>
    '''

@app.route('/ssrf/fetch', methods=['POST'])
def ssrf_fetch():
    url = request.form.get('url', '')
    
    try:
        import urllib.request
        # Vulnerable - no URL validation
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8')[:1000]  # Limit output
        return f"<h3>Response from {url}:</h3><pre>{content}</pre>"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

# Local File Inclusion
@app.route('/lfi')
def lfi_page():
    return '''
    <h2>Local File Inclusion Test</h2>
    <form action="/lfi/read" method="GET">
        <input type="text" name="file" placeholder="Enter filename">
        <input type="submit" value="Read File">
    </form>
    '''

@app.route('/lfi/read')
def lfi_read():
    filename = request.args.get('file', '')
    
    try:
        # Vulnerable - no path validation
        with open(filename, 'r') as f:
            content = f.read()[:1000]  # Limit output
        return f"<h3>File content:</h3><pre>{content}</pre>"
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Remote Code Execution
@app.route('/rce')
def rce_page():
    return '''
    <h2>Remote Code Execution Test</h2>
    <form action="/rce/execute" method="POST">
        <input type="text" name="command" placeholder="Enter command">
        <input type="submit" value="Execute">
    </form>
    '''

@app.route('/rce/execute', methods=['POST'])
def rce_execute():
    command = request.form.get('command', '')
    
    try:
        # Vulnerable - direct command execution
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return f"<h3>Command output:</h3><pre>{result.decode('utf-8')}</pre>"
    except Exception as e:
        return f"Error executing command: {str(e)}"

# XXE Vulnerability
@app.route('/xxe')
def xxe_page():
    return '''
    <h2>XML External Entity Test</h2>
    <form action="/xxe/parse" method="POST">
        <textarea name="xml" placeholder="Enter XML content"></textarea><br>
        <input type="submit" value="Parse XML">
    </form>
    '''

@app.route('/xxe/parse', methods=['POST'])
def xxe_parse():
    xml_content = request.form.get('xml', '')
    
    try:
        # Vulnerable - no XXE protection
        root = ET.fromstring(xml_content)
        return f"<h3>Parsed XML:</h3><pre>{ET.tostring(root, encoding='unicode')}</pre>"
    except Exception as e:
        return f"Error parsing XML: {str(e)}"

# Insecure Deserialization
@app.route('/deserialization')
def deserialization_page():
    return '''
    <h2>Insecure Deserialization Test</h2>
    <form action="/deserialization/load" method="POST">
        <input type="text" name="data" placeholder="Enter base64 encoded pickle data">
        <input type="submit" value="Deserialize">
    </form>
    '''

@app.route('/deserialization/load', methods=['POST'])
def deserialization_load():
    data = request.form.get('data', '')
    
    try:
        # Vulnerable - unsafe deserialization
        decoded_data = base64.b64decode(data)
        obj = pickle.loads(decoded_data)
        return f"<h3>Deserialized object:</h3><pre>{str(obj)}</pre>"
    except Exception as e:
        return f"Error deserializing data: {str(e)}"

# JWT Vulnerabilities
@app.route('/jwt')
def jwt_page():
    return '''
    <h2>JWT Vulnerabilities Test</h2>
    <form action="/jwt/login" method="POST">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/jwt/login', methods=['POST'])
def jwt_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # Weak JWT implementation
    if username and password:
        payload = {
            'username': username,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        # Vulnerable - weak secret, no algorithm specification
        token = jwt.encode(payload, 'weak_secret', algorithm='HS256')
        
        response = make_response(f"<h3>Login successful! Token: {token}</h3>")
        response.set_cookie('token', token)
        return response
    
    return "Invalid credentials"

# IDOR Vulnerability
@app.route('/idor')
def idor_page():
    return '''
    <h2>Insecure Direct Object Reference Test</h2>
    <form action="/idor/profile" method="GET">
        <input type="text" name="user_id" placeholder="Enter user ID">
        <input type="submit" value="View Profile">
    </form>
    '''

@app.route('/idor/profile')
def idor_profile():
    user_id = request.args.get('user_id', '')
    
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    try:
        # Vulnerable - no access control
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return f"<h3>User Profile:</h3><p>ID: {user[0]}<br>Username: {user[1]}<br>Email: {user[3]}<br>Role: {user[4]}</p>"
        else:
            return "User not found"
    finally:
        conn.close()

# API Endpoints with vulnerabilities
@app.route('/api/users')
def api_users():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            })
        
        return jsonify(user_list)
    finally:
        conn.close()

@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    try:
        # Vulnerable - no authentication required
        cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            })
        else:
            return jsonify({'error': 'User not found'}), 404
    finally:
        conn.close()

# File Upload Vulnerability
@app.route('/upload')
def upload_page():
    return '''
    <h2>File Upload Test</h2>
    <form action="/upload/file" method="POST" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    '''

@app.route('/upload/file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file selected"
    
    file = request.files['file']
    if file.filename == '':
        return "No file selected"
    
    # Vulnerable - no file type validation
    upload_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(upload_path)
    
    return f"File uploaded successfully: {file.filename}"

# Debug endpoint (should not exist in production)
@app.route('/debug')
def debug():
    return f'''
    <h2>Debug Information</h2>
    <p>Environment Variables:</p>
    <pre>{os.environ}</pre>
    <p>Current Directory: {os.getcwd()}</p>
    <p>Files: {os.listdir('.')}</p>
    '''

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    # Run on all interfaces for testing
    app.run(host='0.0.0.0', port=12002, debug=True)