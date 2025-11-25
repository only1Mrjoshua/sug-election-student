import sqlite3
import hashlib
from flask import request
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'election.db')

def init_db():
    """Initialize database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Voters table
        c.execute('''
            CREATE TABLE IF NOT EXISTS voters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                ip_hash TEXT UNIQUE NOT NULL,
                location_verified BOOLEAN DEFAULT FALSE,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Votes table
        c.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id INTEGER NOT NULL,
                candidate_id INTEGER NOT NULL,
                vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES voters (id)
            )
        ''')
        
        # Candidates table with sample data
        c.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT NOT NULL
            )
        ''')
        
        # Insert sample candidates if table is empty
        c.execute('SELECT COUNT(*) FROM candidates')
        if c.fetchone()[0] == 0:
            sample_candidates = [
                ('John Doe', 'President', 'Computer Science'),
                ('Jane Smith', 'President', 'Electrical Engineering'),
                ('Mike Johnson', 'Vice President', 'Mechanical Engineering'),
                ('Sarah Williams', 'Secretary', 'Business Administration'),
                ('David Brown', 'Treasurer', 'Accounting')
            ]
            c.executemany('INSERT INTO candidates (name, position, department) VALUES (?, ?, ?)', sample_candidates)
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized successfully at: {DATABASE}")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

def verify_location(ip_address):
    """
    Verify if IP location is within Etim Ekpo, Akwa Ibom area
    """
    try:
        # For testing, allow all IPs. In production, implement real location check
        print(f"Location verification for IP: {ip_address}")
        return True
        
    except Exception as e:
        print(f"Location verification error: {e}")
        return False

def get_client_ip():
    """Extract client IP address from request"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0]
    return request.remote_addr

def hash_ip(ip_address):
    """Hash IP address for privacy and duplicate checking"""
    return hashlib.sha256(ip_address.encode()).hexdigest()

def check_duplicate_ip(ip_hash):
    """Check if IP has already been used for registration"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id FROM voters WHERE ip_hash = ?', (ip_hash,))
    result = c.fetchone()
    conn.close()
    return result is not None