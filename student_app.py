from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import hashlib
import os
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = "mongodb+srv://only1MrJoshua:LovuLord2025@cluster0.9jqnavg.mongodb.net/election_db?retryWrites=true&w=majority"
DATABASE_NAME = "election_db"

# Initialize MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Collections
voters_collection = db['voters']
candidates_collection = db['candidates']
votes_collection = db['votes']

def init_db():
    """Initialize database with sample data if needed"""
    # Create indexes for better performance
    voters_collection.create_index("student_id", unique=True)
    voters_collection.create_index("ip_hash")
    candidates_collection.create_index("name")
    votes_collection.create_index("voter_id", unique=True)
    votes_collection.create_index("candidate_id")
    
    # Add sample candidates if none exist
    if candidates_collection.count_documents({}) == 0:
        sample_candidates = [
            {
                "name": "John Chukwuma",
                "position": "SRC President",
                "department": "Computer Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Maria Okon",
                "position": "SRC President", 
                "department": "Business Administration",
                "created_at": datetime.utcnow()
            },
            {
                "name": "David Bassey",
                "position": "SRC Secretary",
                "department": "Political Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Grace Emmanuel",
                "position": "SRC Treasurer",
                "department": "Accounting",
                "created_at": datetime.utcnow()
            }
        ]
        candidates_collection.insert_many(sample_candidates)
        print("✅ Sample candidates added to MongoDB")

def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
    return ip

def hash_ip(ip_address):
    """Hash IP address for privacy"""
    return hashlib.sha256(ip_address.encode()).hexdigest()

def check_duplicate_ip(ip_hash):
    """Check if IP has already been used for registration"""
    return voters_collection.find_one({"ip_hash": ip_hash}) is not None

def verify_location(ip_address):
    """Verify if IP is from Obong University campus network"""
    # For demo purposes, we'll allow all IPs
    # In production, you would check against known university IP ranges
    university_ip_ranges = [
        '192.168.1.',  # Example university network
        '10.0.0.',     # Another example
        '172.16.0.',   # And another
    ]
    
    # Check if IP matches any university range
    for ip_range in university_ip_ranges:
        if ip_address.startswith(ip_range):
            return True
    
    # For demo, allow localhost and common private IPs
    if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith(('192.168.', '10.0.', '172.16.')):
        return True
    
    # In production, return False for non-university IPs
    # For now, we'll return True to allow testing
    return True

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
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-red: #D13D39;
            --primary-green: #2C8A45;
            --primary-yellow: #EBBF00;
            --dark-red: #b32b2b;
            --dark-green: #1a5c2d;
            --light-red: #f8e6e5;
            --light-green: #e8f5e9;
            --light-yellow: #fff9e6;
            --dark-gray: #333;
            --medium-gray: #666;
            --light-gray: #f5f5f5;
            --white: #ffffff;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            --radius: 12px;
            --transition: all 0.3s ease;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--dark-gray);
            line-height: 1.6;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--white);
            padding: 25px 30px;
            border-radius: var(--radius) var(--radius) 0 0;
            margin-bottom: 0;
            box-shadow: var(--shadow);
            border-bottom: 4px solid var(--primary-red);
        }
        
        .university-info h1 {
            color: var(--primary-red);
            font-size: 2.2rem;
            margin-bottom: 8px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }
        
        .university-info .subtitle {
            color: var(--primary-green);
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .student-badge {
            background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
            color: var(--white);
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 8px rgba(44, 138, 69, 0.3);
        }
        
        .main-content {
            background: var(--white);
            border-radius: 0 0 var(--radius) var(--radius);
            padding: 30px;
            box-shadow: var(--shadow);
            min-height: 500px;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 30px;
            background: var(--light-gray);
            border-radius: 10px;
            padding: 5px;
            border: 2px solid var(--primary-yellow);
        }
        
        .tab {
            flex: 1;
            padding: 18px;
            text-align: center;
            cursor: pointer;
            border-radius: 8px;
            transition: var(--transition);
            font-weight: 600;
            color: var(--primary-green);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .tab.active {
            background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
            color: var(--white);
            box-shadow: 0 4px 8px rgba(44, 138, 69, 0.3);
        }
        
        .tab:hover:not(.active) {
            background: var(--primary-yellow);
            color: var(--dark-gray);
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .page-header {
            margin-bottom: 25px;
        }
        
        .page-title {
            color: var(--primary-green);
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .page-description {
            color: var(--medium-gray);
            font-size: 1.1rem;
        }
        
        .form-container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: var(--primary-green);
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        input, select {
            width: 100%;
            padding: 16px;
            border: 2px solid var(--light-gray);
            border-radius: 8px;
            font-size: 16px;
            transition: var(--transition);
            background: var(--light-gray);
            font-family: inherit;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--primary-green);
            background: var(--white);
            box-shadow: 0 0 0 3px rgba(44, 138, 69, 0.1);
        }
        
        .btn {
            background: linear-gradient(135deg, var(--primary-green) 0%, var(--dark-green) 100%);
            color: var(--white);
            border: none;
            padding: 18px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 4px 8px rgba(44, 138, 69, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(44, 138, 69, 0.4);
        }
        
        .btn:disabled {
            background: var(--medium-gray);
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn:disabled:hover {
            transform: none;
            box-shadow: none;
        }
        
        .alert {
            padding: 18px 25px;
            border-radius: var(--radius);
            margin-bottom: 25px;
            display: none;
            border-left: 5px solid;
            align-items: center;
            gap: 15px;
        }
        
        .alert-success {
            background: var(--light-green);
            color: var(--primary-green);
            border-left-color: var(--primary-green);
        }
        
        .alert-error {
            background: var(--light-red);
            color: var(--primary-red);
            border-left-color: var(--primary-red);
        }
        
        .alert-warning {
            background: var(--light-yellow);
            color: #b38f00;
            border-left-color: var(--primary-yellow);
        }
        
        .info-box {
            background: var(--light-yellow);
            border: 2px solid var(--primary-yellow);
            border-radius: var(--radius);
            padding: 20px;
            margin: 25px 0;
            color: var(--dark-gray);
        }
        
        .info-box strong {
            color: var(--primary-green);
        }
        
        .verification-status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        .verification-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .badge-verified {
            background: var(--light-green);
            color: var(--primary-green);
        }
        
        .badge-pending {
            background: var(--light-yellow);
            color: #b38f00;
        }
        
        .candidate-card {
            background: var(--white);
            border: 2px solid var(--light-gray);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 15px;
            transition: var(--transition);
            cursor: pointer;
        }
        
        .candidate-card:hover {
            border-color: var(--primary-green);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        .candidate-card.selected {
            border-color: var(--primary-green);
            background: var(--light-green);
        }
        
        .candidate-name {
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 5px;
            color: var(--primary-green);
        }
        
        .candidate-position {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .candidate-department {
            color: var(--medium-gray);
            font-size: 0.9rem;
        }
        
        .vote-confirmation {
            text-align: center;
            padding: 40px 20px;
        }
        
        .confirmation-icon {
            font-size: 4rem;
            color: var(--primary-green);
            margin-bottom: 20px;
        }
        
        .confirmation-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: var(--primary-green);
        }
        
        .confirmation-message {
            color: var(--medium-gray);
            margin-bottom: 30px;
            font-size: 1.1rem;
        }
        
        .footer {
            text-align: center;
            color: var(--white);
            margin-top: 40px;
            padding: 25px;
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            color: var(--medium-gray);
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid var(--light-gray);
            border-top: 4px solid var(--primary-green);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header {
                flex-direction: column;
                text-align: center;
                gap: 20px;
            }
            
            .tabs {
                flex-direction: column;
            }
            
            .tab {
                margin-bottom: 5px;
            }
            
            .main-content {
                padding: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .header {
                padding: 20px;
            }
            
            .university-info h1 {
                font-size: 1.8rem;
            }
            
            .page-title {
                font-size: 1.5rem;
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
            <div class="student-badge">
                <i class="fas fa-graduation-cap"></i>
                STUDENT ACCESS
            </div>
        </div>
        
        <div class="main-content">
            <div class="tabs">
                <div class="tab active" data-tab="register">
                    <i class="fas fa-user-plus"></i>
                    Register to Vote
                </div>
                <div class="tab" data-tab="vote">
                    <i class="fas fa-vote-yea"></i>
                    Cast Your Vote
                </div>
            </div>
            
            <!-- Registration Tab -->
            <div id="register-tab" class="tab-content active">
                <div class="page-header">
                    <h2 class="page-title">Student Registration</h2>
                    <p class="page-description">
                        Register to participate in the SRC elections. Only verified Obong University students can register.
                    </p>
                </div>
                
                <div class="info-box">
                    <i class="fas fa-info-circle"></i>
                    <strong>Location Verification:</strong> Your IP address will be automatically verified to ensure you are within the Obong University campus network.
                </div>
                
                <div id="register-alert" class="alert"></div>
                
                <div class="form-container">
                    <form id="registration-form">
                        <div class="form-group">
                            <label for="student-id">
                                <i class="fas fa-id-card"></i>
                                Student ID Number
                            </label>
                            <input type="text" id="student-id" name="student_id" required placeholder="e.g., U*******">
                        </div>
                        
                        <div class="form-group">
                            <label for="name">
                                <i class="fas fa-user"></i>
                                Full Name
                            </label>
                            <input type="text" id="name" name="name" required placeholder="Enter your full name as registered">
                        </div>
                        
                        <div class="form-group">
                            <label for="email">
                                <i class="fas fa-envelope"></i>
                                University Email
                            </label>
                            <input type="email" id="email" name="email" required placeholder="your.email@obonguniversity.edu.ng">
                        </div>
                        
                        <div class="form-group">
                            <label for="department">
                                <i class="fas fa-building"></i>
                                Department
                            </label>
                            <select id="department" name="department" required>
                                <option value="">Select your department</option>
                                <option value="Computer Science">Computer Science</option>
                                <option value="Business Administration">Business Administration</option>
                                <option value="Political Science">Political Science</option>
                                <option value="Microbiology">Microbiology</option>
                                <option value="Biochemistry">Biochemistry</option>
                                <option value="Economics">Economics</option>
                                <option value="Mass Communication">Mass Communication</option>
                                <option value="Accounting">Accounting</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn" id="register-btn">
                            <i class="fas fa-user-check"></i>
                            Register to Vote
                        </button>
                    </form>
                </div>
            </div>
            
            <!-- Voting Tab -->
            <div id="vote-tab" class="tab-content">
                <div class="page-header">
                    <h2 class="page-title">Cast Your Vote</h2>
                    <p class="page-description">
                        Vote for your preferred SRC candidates. Remember, you can only vote once!
                    </p>
                </div>
                
                <div id="vote-alert" class="alert"></div>
                
                <div id="voting-section">
                    <div class="form-container">
                        <form id="voting-form">
                            <div class="form-group">
                                <label for="voter-student-id">
                                    <i class="fas fa-id-card"></i>
                                    Your Student ID
                                </label>
                                <input type="text" id="voter-student-id" name="student_id" required placeholder="Enter your registered student ID">
                                <div class="verification-status">
                                    <span id="verification-text">Verification status: </span>
                                    <span id="verification-badge" class="verification-badge badge-pending">Not Verified</span>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label>
                                    <i class="fas fa-users"></i>
                                    Select Your Candidate
                                </label>
                                <div id="candidates-container">
                                    <div class="loading">
                                        <div class="loading-spinner"></div>
                                        <p>Loading candidates...</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="info-box">
                                <i class="fas fa-exclamation-triangle"></i>
                                <strong>Important:</strong> Once you submit your vote, it cannot be changed. Please review your selection carefully.
                            </div>
                            
                            <button type="submit" class="btn" id="vote-btn" disabled>
                                <i class="fas fa-paper-plane"></i>
                                Submit Your Vote
                            </button>
                        </form>
                    </div>
                </div>
                
                <div id="vote-confirmation" class="vote-confirmation" style="display: none;">
                    <div class="confirmation-icon">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h3 class="confirmation-title">Vote Submitted Successfully!</h3>
                    <p class="confirmation-message">
                        Thank you for participating in the Obong University SRC Elections 2024. 
                        Your vote has been recorded and will be counted.
                    </p>
                    <button class="btn" onclick="showTab('register')">
                        <i class="fas fa-home"></i>
                        Return to Home
                    </button>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Obong University SRC Election System &copy; 2024 | Secure Student Portal</p>
            <p>For assistance, contact the SRC Election Committee</p>
        </div>
    </div>

    <script>
        const API_BASE = '/api';
        let selectedCandidateId = null;
        let isStudentVerified = false;
        
        // Tab navigation
        document.querySelectorAll('.tab').forEach(item => {
            item.addEventListener('click', function() {
                // Remove active class from all items
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Hide all tab content
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab content
                const tabId = this.getAttribute('data-tab') + '-tab';
                document.getElementById(tabId).classList.add('active');
                
                // Load data for specific tabs
                if (this.getAttribute('data-tab') === 'vote') {
                    loadCandidates();
                    resetVotingForm();
                }
            });
        });
        
        // Function to show a specific tab
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
                if (tab.getAttribute('data-tab') === tabName) {
                    tab.classList.add('active');
                }
            });
            
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            if (tabName === 'vote') {
                loadCandidates();
                resetVotingForm();
            }
        }
        
        // Reset voting form
        function resetVotingForm() {
            document.getElementById('voter-student-id').value = '';
            document.getElementById('verification-badge').className = 'verification-badge badge-pending';
            document.getElementById('verification-badge').textContent = 'Not Verified';
            document.getElementById('verification-text').textContent = 'Verification status: ';
            document.getElementById('vote-btn').disabled = true;
            isStudentVerified = false;
            selectedCandidateId = null;
            
            // Reset candidate selection
            document.querySelectorAll('.candidate-card').forEach(card => {
                card.classList.remove('selected');
            });
            
            // Show voting form, hide confirmation
            document.getElementById('voting-section').style.display = 'block';
            document.getElementById('vote-confirmation').style.display = 'none';
        }
        
        // Registration form handler
        document.getElementById('registration-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            const registerBtn = document.getElementById('register-btn');
            const originalText = registerBtn.innerHTML;
            
            try {
                // Show loading state
                registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registering...';
                registerBtn.disabled = true;
                
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
                    alert.innerHTML = `<i class="fas fa-check-circle"></i> ${result.message}`;
                    alert.style.display = 'flex';
                    
                    // Clear form
                    e.target.reset();
                    
                    // Automatically switch to voting tab after successful registration
                    setTimeout(() => {
                        showTab('vote');
                    }, 2000);
                } else {
                    alert.className = 'alert alert-error';
                    alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
                    alert.style.display = 'flex';
                }
            } catch (error) {
                const alert = document.getElementById('register-alert');
                alert.className = 'alert alert-error';
                alert.innerHTML = '<i class="fas fa-exclamation-circle"></i> Registration failed. Please check your connection and try again.';
                alert.style.display = 'flex';
            } finally {
                // Restore button state
                registerBtn.innerHTML = originalText;
                registerBtn.disabled = false;
            }
        });
        
        // Verify student registration when ID is entered
        document.getElementById('voter-student-id').addEventListener('blur', async function() {
            const studentId = this.value.trim();
            
            if (!studentId) {
                document.getElementById('verification-badge').className = 'verification-badge badge-pending';
                document.getElementById('verification-badge').textContent = 'Not Verified';
                document.getElementById('vote-btn').disabled = true;
                isStudentVerified = false;
                return;
            }
            
            try {
                document.getElementById('verification-badge').className = 'verification-badge badge-pending';
                document.getElementById('verification-badge').textContent = 'Verifying...';
                
                const response = await fetch(`${API_BASE}/verify-student/${studentId}`);
                const result = await response.json();
                
                if (result.success && result.registered) {
                    document.getElementById('verification-badge').className = 'verification-badge badge-verified';
                    document.getElementById('verification-badge').textContent = 'Verified';
                    document.getElementById('vote-btn').disabled = false;
                    isStudentVerified = true;
                    
                    // Show success message
                    const alert = document.getElementById('vote-alert');
                    alert.className = 'alert alert-success';
                    alert.innerHTML = `<i class="fas fa-check-circle"></i> Student verification successful. You can now cast your vote.`;
                    alert.style.display = 'flex';
                    
                    // Hide alert after 3 seconds
                    setTimeout(() => {
                        alert.style.display = 'none';
                    }, 3000);
                } else {
                    document.getElementById('verification-badge').className = 'verification-badge badge-pending';
                    document.getElementById('verification-badge').textContent = 'Not Registered';
                    document.getElementById('vote-btn').disabled = true;
                    isStudentVerified = false;
                    
                    // Show error message
                    const alert = document.getElementById('vote-alert');
                    alert.className = 'alert alert-error';
                    alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Student ID not found. Please register first.`;
                    alert.style.display = 'flex';
                }
            } catch (error) {
                document.getElementById('verification-badge').className = 'verification-badge badge-pending';
                document.getElementById('verification-badge').textContent = 'Verification Failed';
                document.getElementById('vote-btn').disabled = true;
                isStudentVerified = false;
                
                // Show error message
                const alert = document.getElementById('vote-alert');
                alert.className = 'alert alert-error';
                alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Verification failed. Please try again.`;
                alert.style.display = 'flex';
            }
        });
        
        // Load candidates for voting
        async function loadCandidates() {
            const container = document.getElementById('candidates-container');
            
            try {
                container.innerHTML = `
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        <p>Loading candidates...</p>
                    </div>
                `;
                
                const response = await fetch(API_BASE + '/candidates');
                const result = await response.json();
                
                if (result.success) {
                    container.innerHTML = '';
                    
                    if (result.candidates && result.candidates.length > 0) {
                        // Group candidates by position
                        const positions = {};
                        result.candidates.forEach(candidate => {
                            if (!positions[candidate.position]) {
                                positions[candidate.position] = [];
                            }
                            positions[candidate.position].push(candidate);
                        });
                        
                        // Create candidate cards for each position
                        for (const [position, candidates] of Object.entries(positions)) {
                            const positionHeader = document.createElement('h3');
                            positionHeader.style.cssText = 'color: var(--primary-green); margin: 25px 0 15px 0; font-size: 1.3rem; font-weight: 700;';
                            positionHeader.textContent = position;
                            container.appendChild(positionHeader);
                            
                            candidates.forEach(candidate => {
                                const candidateCard = document.createElement('div');
                                candidateCard.className = 'candidate-card';
                                candidateCard.dataset.candidateId = candidate.id;
                                candidateCard.innerHTML = `
                                    <div class="candidate-name">${candidate.name}</div>
                                    <div class="candidate-department">${candidate.department || 'No department specified'}</div>
                                `;
                                
                                candidateCard.addEventListener('click', function() {
                                    if (!isStudentVerified) {
                                        const alert = document.getElementById('vote-alert');
                                        alert.className = 'alert alert-error';
                                        alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Please verify your student ID first.`;
                                        alert.style.display = 'flex';
                                        return;
                                    }
                                    
                                    // Deselect all candidates
                                    document.querySelectorAll('.candidate-card').forEach(card => {
                                        card.classList.remove('selected');
                                    });
                                    
                                    // Select this candidate
                                    this.classList.add('selected');
                                    selectedCandidateId = candidate.id;
                                });
                                
                                container.appendChild(candidateCard);
                            });
                        }
                    } else {
                        container.innerHTML = `
                            <div class="loading">
                                <i class="fas fa-users" style="font-size: 3rem; margin-bottom: 20px; opacity: 0.5;"></i>
                                <h3>No Candidates Available</h3>
                                <p>Candidates will appear here once they are registered.</p>
                            </div>
                        `;
                    }
                } else {
                    throw new Error(result.message || 'Failed to load candidates');
                }
            } catch (error) {
                container.innerHTML = `
                    <div class="loading">
                        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px; color: var(--primary-red);"></i>
                        <h3>Unable to Load Candidates</h3>
                        <p>There was a problem fetching the candidate list. Please try again.</p>
                        <button class="btn" style="margin-top: 20px;" onclick="loadCandidates()">
                            <i class="fas fa-redo"></i>
                            Try Again
                        </button>
                    </div>
                `;
            }
        }
        
        // Voting form handler
        document.getElementById('voting-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!isStudentVerified) {
                const alert = document.getElementById('vote-alert');
                alert.className = 'alert alert-error';
                alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Please verify your student ID first.`;
                alert.style.display = 'flex';
                return;
            }
            
            if (!selectedCandidateId) {
                const alert = document.getElementById('vote-alert');
                alert.className = 'alert alert-error';
                alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> Please select a candidate to vote for.`;
                alert.style.display = 'flex';
                return;
            }
            
            const studentId = document.getElementById('voter-student-id').value;
            const voteBtn = document.getElementById('vote-btn');
            const originalText = voteBtn.innerHTML;
            
            try {
                // Show loading state
                voteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting Vote...';
                voteBtn.disabled = true;
                
                const response = await fetch(API_BASE + '/vote', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        student_id: studentId,
                        candidate_id: selectedCandidateId
                    })
                });
                
                const result = await response.json();
                const alert = document.getElementById('vote-alert');
                
                if (result.success) {
                    // Hide voting form, show confirmation
                    document.getElementById('voting-section').style.display = 'none';
                    document.getElementById('vote-confirmation').style.display = 'block';
                } else {
                    alert.className = 'alert alert-error';
                    alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${result.message}`;
                    alert.style.display = 'flex';
                    
                    // Restore button state
                    voteBtn.innerHTML = originalText;
                    voteBtn.disabled = false;
                }
            } catch (error) {
                const alert = document.getElementById('vote-alert');
                alert.className = 'alert alert-error';
                alert.innerHTML = '<i class="fas fa-exclamation-circle"></i> Voting failed. Please check your connection and try again.';
                alert.style.display = 'flex';
                
                // Restore button state
                voteBtn.innerHTML = originalText;
                voteBtn.disabled = false;
            }
        });
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', () => {
            // Any initialization code if needed
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
        department = data.get('department')
        
        print(f"🔍 DEBUG: Registration attempt - Student ID: {student_id}, Name: {name}")
        
        if not all([student_id, name, email, department]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Get client IP
        client_ip = get_client_ip()
        ip_hash = hash_ip(client_ip)
        
        print(f"📍 DEBUG: Client IP: {client_ip}, Hash: {ip_hash[:10]}...")
        
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
        
        # Register voter in MongoDB
        try:
            voter_data = {
                'student_id': student_id,
                'name': name,
                'email': email,
                'department': department,
                'ip_hash': ip_hash,
                'location_verified': location_verified,
                'registration_date': datetime.utcnow(),
                'has_voted': False
            }
            
            result = voters_collection.insert_one(voter_data)
            voter_id = str(result.inserted_id)
            
            print(f"✅ DEBUG: Voter registered successfully - Voter ID: {voter_id}")
            
            return jsonify({
                'success': True,
                'message': 'Voter registered successfully! Location verified.',
                'voter_id': voter_id,
                'location_verified': location_verified
            })
            
        except Exception as e:
            print(f"❌ DEBUG: MongoDB error - {e}")
            if "duplicate key" in str(e):
                return jsonify({
                    'success': False,
                    'message': 'Student ID already registered'
                }), 400
            else:
                raise e
            
    except Exception as e:
        print(f"❌ DEBUG: Registration exception - {e}")
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get list of all candidates"""
    try:
        candidates = list(candidates_collection.find({}, {'_id': 1, 'name': 1, 'position': 1, 'department': 1}))
        
        candidates_list = []
        for candidate in candidates:
            candidates_list.append({
                'id': str(candidate['_id']),
                'name': candidate['name'],
                'position': candidate['position'],
                'department': candidate.get('department', '')
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

@app.route('/api/verify-student/<student_id>', methods=['GET'])
def verify_student(student_id):
    """Verify if a student is registered and location verified"""
    try:
        voter = voters_collection.find_one({'student_id': student_id})
        
        if voter:
            return jsonify({
                'success': True,
                'registered': True,
                'location_verified': voter.get('location_verified', False),
                'voter_name': voter['name'],
                'has_voted': voter.get('has_voted', False)
            })
        else:
            return jsonify({
                'success': True,
                'registered': False
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error verifying student: {str(e)}'
        }), 500

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    """Cast a vote for a candidate"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        candidate_id = data.get('candidate_id')
        
        print(f"🔍 DEBUG: Vote attempt received - Student ID: {student_id}, Candidate ID: {candidate_id}")
        
        if not all([student_id, candidate_id]):
            print("❌ DEBUG: Missing required fields")
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
        
        # Verify voter exists and location was verified
        voter = voters_collection.find_one({
            'student_id': student_id, 
            'location_verified': True
        })
        
        if not voter:
            print(f"❌ DEBUG: Voter not found or not verified - Student ID: {student_id}")
            return jsonify({
                'success': False,
                'message': 'Voter not found or location not verified. Please register first.'
            }), 404
        
        voter_id = str(voter['_id'])
        voter_name = voter['name']
        
        # Check if voter has already voted
        if voter.get('has_voted', False):
            print(f"❌ DEBUG: Voter already voted - Voter ID: {voter_id}")
            return jsonify({
                'success': False,
                'message': 'You have already voted'
            }), 400
        
        # Verify candidate exists
        try:
            candidate_object_id = ObjectId(candidate_id)
        except:
            print(f"❌ DEBUG: Invalid candidate ID format - Candidate ID: {candidate_id}")
            return jsonify({
                'success': False,
                'message': 'Invalid candidate ID'
            }), 400
        
        candidate = candidates_collection.find_one({'_id': candidate_object_id})
        
        if not candidate:
            print(f"❌ DEBUG: Candidate not found - Candidate ID: {candidate_id}")
            return jsonify({
                'success': False,
                'message': 'Candidate not found'
            }), 404
        
        candidate_name = candidate['name']
        candidate_position = candidate['position']
        print(f"✅ DEBUG: Candidate found - Name: {candidate_name}, Position: {candidate_position}")
        
        # Record the vote
        vote_data = {
            'voter_id': voter_id,
            'candidate_id': candidate_id,
            'student_id': student_id,
            'candidate_name': candidate_name,
            'candidate_position': candidate_position,
            'vote_date': datetime.utcnow()
        }
        
        vote_result = votes_collection.insert_one(vote_data)
        vote_id = str(vote_result.inserted_id)
        
        # Update voter to mark as voted
        voters_collection.update_one(
            {'_id': voter['_id']},
            {'$set': {'has_voted': True}}
        )
        
        print(f"✅ DEBUG: Vote successfully recorded - Vote ID: {vote_id}")
        return jsonify({
            'success': True,
            'message': 'Vote cast successfully!',
            'vote_id': vote_id
        })
        
    except Exception as e:
        print(f"❌ DEBUG: Exception in cast_vote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Voting error: {str(e)}'
        }), 500

# Debug endpoints
@app.route('/api/debug/votes')
def debug_votes():
    """Debug endpoint to see all votes in the database"""
    try:
        votes = list(votes_collection.find().sort('vote_date', -1))
        
        votes_list = []
        for vote in votes:
            votes_list.append({
                'vote_id': str(vote['_id']),
                'student_id': vote['student_id'],
                'candidate_name': vote.get('candidate_name', 'Unknown'),
                'position': vote.get('candidate_position', 'Unknown'),
                'vote_date': vote['vote_date'].isoformat() if 'vote_date' in vote else 'Unknown'
            })
        
        return jsonify({
            'success': True,
            'total_votes': len(votes_list),
            'votes': votes_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching votes: {str(e)}'
        }), 500

@app.route('/api/debug/voters')
def debug_voters():
    """Debug endpoint to see all voters"""
    try:
        voters = list(voters_collection.find().sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'id': str(voter['_id']),
                'student_id': voter['student_id'],
                'name': voter['name'],
                'email': voter['email'],
                'department': voter['department'],
                'ip_hash': voter['ip_hash'][:10] + '...',
                'location_verified': voter.get('location_verified', False),
                'has_voted': voter.get('has_voted', False),
                'registration_date': voter['registration_date'].isoformat() if 'registration_date' in voter else 'Unknown'
            })
        
        return jsonify({
            'success': True,
            'total_voters': len(voters_list),
            'voters': voters_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching voters: {str(e)}'
        }), 500

@app.route('/api/debug/database')
def debug_database():
    """Debug endpoint to check database status"""
    try:
        # Get collection counts
        voters_count = voters_collection.count_documents({})
        candidates_count = candidates_collection.count_documents({})
        votes_count = votes_collection.count_documents({})
        
        # Get database info
        database_info = {
            'database_name': DATABASE_NAME,
            'mongo_uri': MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI,  # Hide credentials
            'collections': ['voters', 'candidates', 'votes'],
            'record_counts': {
                'voters': voters_count,
                'candidates': candidates_count,
                'votes': votes_count
            }
        }
        
        return jsonify({
            'success': True,
            'database_info': database_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error checking database: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Student Portal - Obong University SRC Elections")
    print("✅ MongoDB connected successfully!")
    print("🌐 Student Portal running at: http://localhost:5001")
    print("🎓 Students can register and vote at this portal")
    print("🐛 Debug tools available at: http://localhost:5001/api/debug endpoints")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001)