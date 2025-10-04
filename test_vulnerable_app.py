#!/usr/bin/env python3
"""
Test Vulnerable Application
A simple Flask application with intentional vulnerabilities for testing AEGIS-X
"""

from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os
import argparse

app = Flask(__name__)

# Create a simple database
def init_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, email) VALUES (1, 'admin', 'password123', 'admin@test.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, email) VALUES (2, 'user', 'user123', 'user@test.com')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Test Vulnerable App</title></head>
    <body>
        <h1>Test Vulnerable Application</h1>
        <p>This application contains intentional vulnerabilities for testing.</p>
        
        <h2>Login Form</h2>
        <form action="/login" method="POST">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <input type="submit" value="Login">
        </form>
        
        <h2>Search Form</h2>
        <form action="/search" method="GET">
            <input type="text" name="q" placeholder="Search query"><br>
            <input type="submit" value="Search">
        </form>
        
        <h2>Comment Form</h2>
        <form action="/comment" method="POST">
            <input type="text" name="comment" placeholder="Your comment"><br>
            <input type="submit" value="Submit Comment">
        </form>
        
        <p><a href="/users">View Users</a></p>
        <p><a href="/admin">Admin Panel</a></p>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # Vulnerable SQL injection
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return f"<h1>Welcome {user[1]}!</h1><p>Login successful</p>"
        else:
            return "<h1>Login Failed</h1><p>Invalid credentials</p>"
    except Exception as e:
        conn.close()
        return f"<h1>Database Error</h1><p>{str(e)}</p>"

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # Vulnerable XSS
    return f'''
    <html>
    <head><title>Search Results</title></head>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {query}</p>
        <p>No results found.</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    '''

@app.route('/comment', methods=['POST'])
def comment():
    comment = request.form.get('comment', '')
    
    # Vulnerable XSS in comment display
    return f'''
    <html>
    <head><title>Comment Submitted</title></head>
    <body>
        <h1>Comment Submitted</h1>
        <p>Your comment: {comment}</p>
        <a href="/">Back to home</a>
    </body>
    </html>
    '''

@app.route('/users')
def users():
    user_id = request.args.get('id', '1')
    
    # Vulnerable SQL injection in parameter
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    try:
        cursor.execute(query)
        users = cursor.fetchall()
        conn.close()
        
        result = "<h1>Users</h1>"
        for user in users:
            result += f"<p>ID: {user[0]}, Username: {user[1]}, Email: {user[3]}</p>"
        
        return result
    except Exception as e:
        conn.close()
        return f"<h1>Database Error</h1><p>{str(e)}</p>"

@app.route('/admin')
def admin():
    # Missing authentication check
    return '''
    <html>
    <head><title>Admin Panel</title></head>
    <body>
        <h1>Admin Panel</h1>
        <p>Welcome to the admin panel!</p>
        <p>This should require authentication but doesn't.</p>
        <h2>Sensitive Information</h2>
        <p>Database password: super_secret_password</p>
        <p>API Key: sk-1234567890abcdef</p>
    </body>
    </html>
    '''

@app.route('/file')
def file_read():
    filename = request.args.get('file', 'default.txt')
    
    # Vulnerable LFI
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@app.route('/api/users/<int:user_id>')
def api_user(user_id):
    # Vulnerable IDOR
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[3]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vulnerable Test Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=12001, help='Port to bind to')
    args = parser.parse_args()
    
    init_db()
    app.run(host=args.host, port=args.port, debug=True)