from flask import Flask, request, jsonify
from shared_database import init_db, verify_location, get_client_ip, hash_ip, check_duplicate_ip
import sqlite3

app = Flask(__name__)
DATABASE = 'election.db'

# Initialize database
init_db()

@app.route('/')
def student_home():
    """Student portal home page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student Portal - Obong University SRC Elections</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2C8A45 0%, #1a5c2d 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: white;
                padding: 20px;
                border-radius: 15px 15px 0 0;
                margin-bottom: 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            
            .university-info h1 {
                color: #D13D39;
                font-size: 1.8rem;
                margin-bottom: 5px;
                font-weight: 700;
            }
            
            .university-info .subtitle {
                color: #2C8A45;
                font-size: 1.1rem;
                font-weight: 600;
            }
            
            .student-badge {
                background: #2C8A45;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9rem;
            }
            
            .card {
                background: white;
                border-radius: 0 0 15px 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            
            .tabs {
                display: flex;
                margin-bottom: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid #EBBF00;
            }
            
            .tab {
                flex: 1;
                padding: 15px;
                text-align: center;
                cursor: pointer;
                border-radius: 8px;
                transition: all 0.3s ease;
                font-weight: 600;
                color: #2C8A45;
            }
            
            .tab.active {
                background: #2C8A45;
                color: white;
            }
            
            .tab:hover:not(.active) {
                background: #EBBF00;
                color: black;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #2C8A45;
                font-size: 1rem;
            }
            
            input, select {
                width: 100%;
                padding: 14px;
                border: 2px solid #EBBF00;
                border-radius: 8px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: #f8f9fa;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #2C8A45;
                background: white;
                box-shadow: 0 0 0 3px rgba(44, 138, 69, 0.1);
            }
            
            .btn {
                background: linear-gradient(135deg, #2C8A45 0%, #3aa85c 100%);
                color: white;
                border: none;
                padding: 16px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(44, 138, 69, 0.4);
            }
            
            .alert {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
                border-left: 4px solid;
            }
            
            .alert-success {
                background: #d4edda;
                color: #155724;
                border-left-color: #2C8A45;
            }
            
            .alert-error {
                background: #f8d7da;
                color: #721c24;
                border-left-color: #D13D39;
            }
            
            .hidden {
                display: none;
            }
            
            .info-box {
                background: linear-gradient(135deg, #EBBF00 0%, #ffeb3b 100%);
                border: 2px solid #EBBF00;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                color: black;
            }
            
            .info-box strong {
                color: #2C8A45;
            }
            
            .footer {
                text-align: center;
                color: white;
                margin-top: 30px;
                padding: 20px;
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .header {
                    flex-direction: column;
                    text-align: center;
                    gap: 15px;
                }
                
                .tabs {
                    flex-direction: column;
                }
                
                .tab {
                    margin-bottom: 5px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="university-info">
                    <h1>OBONG UNIVERSITY</h1>
                    <div class="subtitle">Student Portal - SRC Elections 2024</div>
                </div>
                <div class="student-badge">🎓 STUDENT ACCESS</div>
            </div>
            
            <div class="card">
                <div class="tabs">
                    <div class="tab active" onclick="showTab('register')">📝 Register to Vote</div>
                    <div class="tab" onclick="showTab('vote')">🗳️ Cast Your Vote</div>
                </div>
                
                <!-- Registration Tab -->
                <div id="register-tab" class="tab-content">
                    <h2 style="color: #2C8A45; margin-bottom: 20px;">Student Registration</h2>
                    <p style="margin-bottom: 20px; color: #666;">
                        Register to participate in the SRC elections. Only verified Obong University students can register.
                    </p>
                    
                    <div class="info-box">
                        <strong>📍 Location Verification:</strong> Your IP address will be automatically verified to ensure you are within the Obong University campus network.
                    </div>
                    
                    <div id="register-alert" class="alert"></div>
                    
                    <form id="registration-form">
                        <div class="form-group">
                            <label for="student-id">🎓 Student ID Number</label>
                            <input type="text" id="student-id" name="student_id" required placeholder="e.g., OBU/2021/001">
                        </div>
                        
                        <div class="form-group">
                            <label for="name">👤 Full Name</label>
                            <input type="text" id="name" name="name" required placeholder="Enter your full name as registered">
                        </div>
                        
                        <div class="form-group">
                            <label for="email">📧 University Email</label>
                            <input type="email" id="email" name="email" required placeholder="your.email@obonguniversity.edu.ng">
                        </div>
                        
                        <button type="submit" class="btn">Register to Vote</button>
                    </form>
                </div>
                
                <!-- Voting Tab -->
                <div id="vote-tab" class="tab-content hidden">
                    <h2 style="color: #2C8A45; margin-bottom: 20px;">Cast Your Vote</h2>
                    <p style="margin-bottom: 20px; color: #666;">
                        Vote for your preferred SRC candidates. Remember, you can only vote once!
                    </p>
                    
                    <div id="vote-alert" class="alert"></div>
                    
                    <form id="voting-form">
                        <div class="form-group">
                            <label for="voter-student-id">🎓 Your Student ID</label>
                            <input type="text" id="voter-student-id" name="student_id" required placeholder="Enter your registered student ID">
                        </div>
                        
                        <div class="form-group">
                            <label for="candidate-select">🏆 Select Your Candidate</label>
                            <select id="candidate-select" name="candidate_id" required>
                                <option value="">Choose your preferred candidate...</option>
                            </select>
                        </div>
                        
                        <div class="info-box">
                            <strong>⚠️ Important:</strong> Once you submit your vote, it cannot be changed. Please review your selection carefully.
                        </div>
                        
                        <button type="submit" class="btn">Submit Your Vote</button>
                    </form>
                </div>
            </div>
            
            <div class="footer">
                <p>Obong University SRC Election System 2024 • Student Voting Portal</p>
                <p>For assistance, contact the SRC Electoral Committee</p>
            </div>
        </div>

        <script>
            const API_BASE = '/api';
            
            function showTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.add('hidden');
                });
                
                // Remove active class from all tabs
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(`${tabName}-tab`).classList.remove('hidden');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
                
                // Load data for specific tabs
                if (tabName === 'vote') {
                    loadCandidates();
                }
            }
            
            // Registration form handler
            document.getElementById('registration-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch(API_BASE + '/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const alert = document.getElementById('register-alert');
                    
                    if (result.success) {
                        alert.className = 'alert alert-success';
                        alert.textContent = '✅ ' + result.message;
                        alert.style.display = 'block';
                        e.target.reset();
                    } else {
                        alert.className = 'alert alert-error';
                        alert.textContent = '❌ ' + result.message;
                        alert.style.display = 'block';
                    }
                } catch (error) {
                    const alert = document.getElementById('register-alert');
                    alert.className = 'alert alert-error';
                    alert.textContent = '❌ Registration failed. Please try again.';
                    alert.style.display = 'block';
                }
            });
            
            // Load candidates for voting
            async function loadCandidates() {
                try {
                    const response = await fetch(API_BASE + '/candidates');
                    const result = await response.json();
                    
                    if (result.success) {
                        const select = document.getElementById('candidate-select');
                        select.innerHTML = '<option value="">Choose your preferred candidate...</option>';
                        
                        result.candidates.forEach(candidate => {
                            const option = document.createElement('option');
                            option.value = candidate.id;
                            option.textContent = `${candidate.name} - ${candidate.position} (${candidate.department})`;
                            select.appendChild(option);
                        });
                    }
                } catch (error) {
                    console.error('Error loading candidates:', error);
                }
            }
            
            // Voting form handler
            document.getElementById('voting-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch(API_BASE + '/vote', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    const alert = document.getElementById('vote-alert');
                    
                    if (result.success) {
                        alert.className = 'alert alert-success';
                        alert.textContent = '✅ ' + result.message;
                        alert.style.display = 'block';
                        e.target.reset();
                    } else {
                        alert.className = 'alert alert-error';
                        alert.textContent = '❌ ' + result.message;
                        alert.style.display = 'block';
                    }
                } catch (error) {
                    const alert = document.getElementById('vote-alert');
                    alert.className = 'alert alert-error';
                    alert.textContent = '❌ Voting failed. Please try again.';
                    alert.style.display = 'block';
                }
            });
            
            // Initialize the page
            document.addEventListener('DOMContentLoaded', () => {
                loadCandidates();
            });
        </script>
    </body>
    </html>
    '''

# Student API Routes
@app.route('/api/register', methods=['POST'])
def register_voter():
    """Register a new voter with IP verification"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        name = data.get('name')
        email = data.get('email')
        
        if not all([student_id, name, email]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Get client IP
        client_ip = get_client_ip()
        ip_hash = hash_ip(client_ip)
        
        print(f"Registration attempt from IP: {client_ip}")
        
        # Check for duplicate IP
        if check_duplicate_ip(ip_hash):
            return jsonify({
                'success': False,
                'message': 'This IP address has already been used for registration'
            }), 400
        
        # Verify location
        location_verified = verify_location(client_ip)
        
        if not location_verified:
            return jsonify({
                'success': False,
                'message': f'Registration only allowed from Obong University campus network',
                'detected_ip': client_ip
            }), 403
        
        # Register voter
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO voters (student_id, name, email, ip_hash, location_verified)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, name, email, ip_hash, location_verified))
            
            voter_id = c.lastrowid
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Voter registered successfully! Location verified.',
                'voter_id': voter_id,
                'location_verified': location_verified
            })
            
        except sqlite3.IntegrityError:
            return jsonify({
                'success': False,
                'message': 'Student ID already registered'
            }), 400
            
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get list of all candidates"""
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM candidates')
        candidates = c.fetchall()
        conn.close()
        
        candidates_list = []
        for candidate in candidates:
            candidates_list.append({
                'id': candidate[0],
                'name': candidate[1],
                'position': candidate[2],
                'department': candidate[3]
            })
        
        return jsonify({
            'success': True,
            'candidates': candidates_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching candidates: {str(e)}'
        }), 500

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    """Cast a vote for a candidate"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        candidate_id = data.get('candidate_id')
        
        if not all([student_id, candidate_id]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # Verify voter exists and location was verified
        c.execute('SELECT id FROM voters WHERE student_id = ? AND location_verified = 1', (student_id,))
        voter = c.fetchone()
        
        if not voter:
            return jsonify({
                'success': False,
                'message': 'Voter not found or location not verified'
            }), 404
        
        voter_id = voter[0]
        
        # Check if voter has already voted
        c.execute('SELECT id FROM votes WHERE voter_id = ?', (voter_id,))
        existing_vote = c.fetchone()
        
        if existing_vote:
            return jsonify({
                'success': False,
                'message': 'You have already voted'
            }), 400
        
        # Record the vote
        c.execute('INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)', (voter_id, candidate_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Vote cast successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Voting error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Student Portal - Obong University SRC Elections")
    print("✅ Database initialized successfully!")
    print("🌐 Student Portal running at: http://localhost:5001")
    print("🎓 Students can register and vote at this portal")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001)