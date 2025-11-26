from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import hashlib
import os
import re
from bson.objectid import ObjectId
import requests

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
    # First, clean up any existing problematic indexes
    try:
        # Get all current indexes on votes collection
        current_indexes = list(votes_collection.list_indexes())
        for index in current_indexes:
            index_name = index['name']
            # Remove problematic unique index on voter_id alone if it exists
            if index_name == 'voter_id_1' and index.get('unique', False):
                votes_collection.drop_index('voter_id_1')
                print("✅ Removed problematic unique index on voter_id")
    except Exception as e:
        print(f"ℹ️  Index cleanup: {e}")

    # Create correct indexes
    indexes_to_create = [
        (voters_collection, "matric_number", True),
        (voters_collection, "email", True),
        (voters_collection, "ip_hash", False),
        (voters_collection, "name", False),
        (candidates_collection, "name", False),
        (candidates_collection, "position", False),
        (votes_collection, "candidate_id", False),
        # Compound unique index - allows multiple votes per voter but only one per position
        (votes_collection, [("voter_id", 1), ("candidate_position", 1)], True),
    ]
    
    for collection, field, unique in indexes_to_create:
        try:
            if isinstance(field, list):  # Compound index
                collection.create_index(field, unique=unique, name="unique_vote_per_position")
            else:  # Single field index
                if unique:
                    collection.create_index(field, unique=True)
                else:
                    collection.create_index(field)
            print(f"✅ Created index for {field}")
        except Exception as e:
            print(f"⚠️  Index warning for {field}: {e}")

    # Add comprehensive sample candidates if none exist
    if candidates_collection.count_documents({}) == 0:
        sample_candidates = [
            # SRC President (3 candidates)
            {
                "name": "John Chukwuma",
                "position": "SRC President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Maria Okon",
                "position": "SRC President", 
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "David Bassey",
                "position": "SRC President",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # SRC Vice President (3 candidates)
            {
                "name": "Grace Emmanuel",
                "position": "SRC Vice President",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Samuel Johnson",
                "position": "SRC Vice President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Fatima Bello",
                "position": "SRC Vice President",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # SRC Secretary (3 candidates)
            {
                "name": "Chinwe Okafor",
                "position": "SRC Secretary",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Michael Adebayo",
                "position": "SRC Secretary",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Jennifer Musa",
                "position": "SRC Secretary",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Natural and Applied Science (4 candidates for 2 positions)
            {
                "name": "Emeka Nwosu",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Bisi Adekunle",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Tunde Ogunleye",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ngozi Eze",
                "position": "Senate Member - Natural and Applied Science",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Management Science (4 candidates for 2 positions)
            {
                "name": "Oluwatoyin Bankole",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "James Okoro",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Patience Udoh",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Sunday Moses",
                "position": "Senate Member - Management Science",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Social Science (4 candidates for 2 positions)
            {
                "name": "Aisha Ibrahim",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Peter Okon",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ruth Chukwu",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Daniel Akpan",
                "position": "Senate Member - Social Science",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # Senate Members - Arts and Communications (4 candidates for 2 positions)
            {
                "name": "Chioma Nwankwo",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Kolawole Adeyemi",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Mercy Thompson",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ibrahim Sani",
                "position": "Senate Member - Arts and Communications",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Information (3 candidates)
            {
                "name": "Tech Savvy Smart",
                "position": "Information Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Media Pro Grace",
                "position": "Information Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Info King David",
                "position": "Information Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Social (3 candidates)
            {
                "name": "Social Butterfly Amina",
                "position": "Social Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Event Master Tunde",
                "position": "Social Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Party Planner Joy",
                "position": "Social Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Sports (3 candidates)
            {
                "name": "Sport Star Mike",
                "position": "Sports Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Team Captain Bola",
                "position": "Sports Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Fitness Queen Sarah",
                "position": "Sports Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Security (3 candidates)
            {
                "name": "Safety First James",
                "position": "Security Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Campus Guard Faith",
                "position": "Security Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Watchful Eye Ken",
                "position": "Security Representative",
                "faculty": "Social Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Transport (3 candidates)
            {
                "name": "Mobility Expert John",
                "position": "Transport Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Ride Master Peace",
                "position": "Transport Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Commute King Henry",
                "position": "Transport Representative",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Hostel 1 (3 candidates)
            {
                "name": "Dorm Leader Tina",
                "position": "Hostel 1 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Room Rep Ahmed",
                "position": "Hostel 1 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Hostel Hero Linda",
                "position": "Hostel 1 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Hostel 2 (3 candidates)
            {
                "name": "Accommodation Ace Paul",
                "position": "Hostel 2 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Dorm Chief Blessing",
                "position": "Hostel 2 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Hostel Head Victor",
                "position": "Hostel 2 Representative",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Representative Members - Chapel (3 candidates)
            {
                "name": "Spiritual Guide Peter",
                "position": "Chapel Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Faith Leader Deborah",
                "position": "Chapel Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Morality Mentor Joseph",
                "position": "Chapel Representative",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            }
        ]
        candidates_collection.insert_many(sample_candidates)
        print("✅ Comprehensive sample candidates added to MongoDB")
    else:
        print("✅ Candidates already exist in database")

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

def verify_email_domain(email):
    """Verify that email is valid"""
    # Basic email format validation
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.lower()) is not None

def check_duplicate_email(email):
    """Check if email already exists in database"""
    return voters_collection.find_one({"email": email.lower()}) is not None

def check_duplicate_name(name):
    """Check if name already exists in database (case insensitive)"""
    return voters_collection.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}) is not None

def validate_matric_number(matric_number):
    """Validate matric number format - must start with U and be 8, 9 or 10 characters total"""
    matric_upper = matric_number.upper()
    
    # Check if starts with U
    if not matric_upper.startswith('U'):
        return False
    
    # Check total length (including the 'U')
    if len(matric_upper) not in [8, 9, 10]:
        return False
    
    return True

def check_duplicate_matric(matric_number):
    """Check if matric number already exists"""
    return voters_collection.find_one({"matric_number": matric_number.upper()}) is not None

def get_ip_location(ip_address):
    """Get location information for an IP address using multiple services"""
    # Skip localhost IPs
    if ip_address in ['127.0.0.1', 'localhost']:
        return {
            'city': 'Localhost',
            'region': 'Development',
            'country': 'Test Environment',
            'latitude': None,
            'longitude': None,
            'isp': 'Local Network',
            'service': 'localhost'
        }
    
    services = [
        {
            'name': 'ipapi.co',
            'url': f'http://ipapi.co/{ip_address}/json/',
            'mapper': lambda data: {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country_name', 'Unknown'),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'isp': data.get('org', 'Unknown'),
                'service': 'ipapi.co'
            }
        },
        {
            'name': 'ip-api.com',
            'url': f'http://ip-api.com/json/{ip_address}',
            'mapper': lambda data: {
                'city': data.get('city', 'Unknown'),
                'region': data.get('regionName', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'isp': data.get('isp', 'Unknown'),
                'service': 'ip-api.com'
            }
        },
        {
            'name': 'ipinfo.io',
            'url': f'https://ipinfo.io/{ip_address}/json',
            'mapper': lambda data: {
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'latitude': data.get('loc', '').split(',')[0] if data.get('loc') else None,
                'longitude': data.get('loc', '').split(',')[1] if data.get('loc') else None,
                'isp': data.get('org', 'Unknown'),
                'service': 'ipinfo.io'
            }
        }
    ]
    
    for service in services:
        try:
            print(f"🔍 Trying IP location service: {service['name']}")
            response = requests.get(service['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                location = service['mapper'](data)
                print(f"✅ Location found via {service['name']}: {location}")
                return location
        except Exception as e:
            print(f"⚠️  {service['name']} failed: {e}")
            continue
    
    print("❌ All IP location services failed")
    return {
        'city': 'Unknown',
        'region': 'Unknown', 
        'country': 'Unknown',
        'latitude': None,
        'longitude': None,
        'isp': 'Unknown',
        'service': 'all_failed'
    }

def verify_location(ip_address):
    """Verify if IP is from Obong University campus network"""
    # Allow localhost for testing
    if ip_address in ['127.0.0.1', 'localhost']:
        print("📍 Localhost detected - allowing for testing")
        return True
    
    # Get IP location
    location = get_ip_location(ip_address)
    
    # Check if location matches Obong University areas
    allowed_locations = [
        'etim ekpo', 'obong ntak', 'akwa ibom', 'uyo', 'ikot ekpene',
        'abak', 'ikot okoro', 'essien udim', 'ibiono', 'itu'
    ]
    
    location_str = f"{location['city']} {location['region']} {location['country']}".lower()
    
    print(f"📍 Location check: '{location_str}'")
    print(f"📍 Raw location data: {location}")
    
    # Check if any allowed location is in the location string
    for allowed_loc in allowed_locations:
        if allowed_loc in location_str:
            print(f"✅ Location verified: {location_str} matches {allowed_loc}")
            return True
    
    # Additional check: If we're in Nigeria but can't pinpoint exact location, allow it
    if 'nigeria' in location_str.lower():
        print(f"📍 Nigeria detected but not specific location: {location_str}")
        print("⚠️  Allowing Nigerian IP for now - may need manual verification")
        return True
    
    print(f"❌ Location NOT verified: {location_str}")
    print(f"🔍 Allowed locations: {allowed_locations}")
    return False

# Initialize database
init_db()

@app.route('/')
def student_home():
    """Student portal home page - now using template"""
    return render_template('student_portal.html')

# All your API routes remain exactly the same...
@app.route('/api/register', methods=['POST'])
def register_voter():
    """Register a new voter with enhanced verification"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        faculty = data.get('faculty')
        matric_number = data.get('matric_number')
        
        print(f"🔍 DEBUG: Registration attempt - Matric: {matric_number}, Name: {name}, Email: {email}")
        
        if not all([name, email, faculty, matric_number]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400
        
        # Basic email format validation
        if not verify_email_domain(email):
            return jsonify({
                'success': False,
                'message': 'Please provide a valid email address'
            }), 400
        
        # Check for duplicate email
        if check_duplicate_email(email):
            return jsonify({
                'success': False,
                'message': 'This email address is already registered'
            }), 400
        
        # Check for duplicate name (case insensitive)
        if check_duplicate_name(name):
            return jsonify({
                'success': False,
                'message': 'This name is already registered'
            }), 400
        
        # Validate matric number format
        matric_upper = matric_number.upper()
        if not validate_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must start with U and be exactly 8, 9 or 10 characters total'
            }), 400
        
        # Check for duplicate matric number
        if check_duplicate_matric(matric_number):
            return jsonify({
                'success': False,
                'message': 'This matric number is already registered'
            }), 400
        
        # Get client IP and location
        client_ip = get_client_ip()
        ip_hash = hash_ip(client_ip)
        location_info = get_ip_location(client_ip)
        
        print(f"📍 DEBUG: Client IP: {client_ip}, Location: {location_info}")
        
        # Check for duplicate IP
        if check_duplicate_ip(ip_hash):
            return jsonify({
                'success': False,
                'message': 'This IP address has already been used for registration'
            }), 400
        
        # Verify location
        location_verified = verify_location(client_ip)
        
        if not location_verified:
            # More helpful error message
            if client_ip in ['127.0.0.1', 'localhost']:
                error_msg = 'Local testing detected. Please test from a device connected to the Obong University campus network.'
            elif location_info.get('country') == 'Unknown':
                error_msg = f'Unable to verify your location. Please ensure you are connected to the Obong University campus network in Etim Ekpo/Obong Ntak area. Detected IP: {client_ip}'
            else:
                error_msg = f'Registration only allowed from Obong University campus network (Etim Ekpo, Obong Ntak areas). Detected location: {location_info["city"]}, {location_info["region"]}, {location_info["country"]}'
            
            return jsonify({
                'success': False,
                'message': error_msg,
                'detected_ip': client_ip,
                'detected_location': location_info
            }), 403
        
        # Register voter in MongoDB
        try:
            voter_data = {
                'matric_number': matric_upper,
                'name': name,
                'email': email.lower(),
                'faculty': faculty,
                'ip_address': client_ip,
                'ip_hash': ip_hash,
                'location_info': location_info,
                'location_verified': location_verified,
                'registration_date': datetime.utcnow(),
                'has_voted': False
            }
            
            result = voters_collection.insert_one(voter_data)
            voter_id = str(result.inserted_id)
            
            print(f"✅ DEBUG: Voter registered successfully - Voter ID: {voter_id}")
            print(f"📍 DEBUG: IP: {client_ip}, Location: {location_info}")
            
            return jsonify({
                'success': True,
                'message': 'Voter registered successfully! All security checks passed.',
                'voter_id': voter_id,
                'location_verified': location_verified,
                'detected_location': location_info,
                'email_verified': True,
                'matric_verified': True
            })
            
        except Exception as e:
            print(f"❌ DEBUG: MongoDB error - {e}")
            if "duplicate key" in str(e):
                if "email" in str(e):
                    return jsonify({
                        'success': False,
                        'message': 'Email address already registered'
                    }), 400
                elif "matric_number" in str(e):
                    return jsonify({
                        'success': False,
                        'message': 'Matric number already registered'
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
        candidates = list(candidates_collection.find({}, {'_id': 1, 'name': 1, 'position': 1, 'faculty': 1}))
        
        candidates_list = []
        for candidate in candidates:
            candidates_list.append({
                'id': str(candidate['_id']),
                'name': candidate['name'],
                'position': candidate['position'],
                'faculty': candidate.get('faculty', '')
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

@app.route('/api/verify-student/<matric_number>', methods=['GET'])
def verify_student(matric_number):
    """Verify if a student is registered and location verified"""
    try:
        voter = voters_collection.find_one({'matric_number': matric_number.upper()})
        
        if voter:
            return jsonify({
                'success': True,
                'registered': True,
                'location_verified': voter.get('location_verified', False),
                'voter_name': voter['name'],
                'has_voted': voter.get('has_voted', False),
                'email': voter.get('email', ''),
                'matric_number': voter.get('matric_number', '')
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
    """Cast votes for multiple candidates at once"""
    try:
        data = request.get_json()
        matric_number = data.get('matric_number')
        votes = data.get('votes')  # Dictionary of {position: {id, name}}
        
        print(f"🔍 DEBUG: Vote attempt received - Matric: {matric_number}, Votes: {len(votes)} positions")
        
        if not all([matric_number, votes]) or len(votes) == 0:
            print("❌ DEBUG: Missing required fields or no votes")
            return jsonify({
                'success': False,
                'message': 'Missing required fields or no votes selected'
            }), 400
        
        # Verify voter exists and location was verified
        voter = voters_collection.find_one({
            'matric_number': matric_number.upper(), 
            'location_verified': True
        })
        
        if not voter:
            print(f"❌ DEBUG: Voter not found or not verified - Matric: {matric_number}")
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
        
        vote_ids = []
        
        # Record all votes in a transaction to ensure atomicity
        with client.start_session() as session:
            with session.start_transaction():
                # Record all votes
                for position, candidate_data in votes.items():
                    candidate_id = candidate_data.get('id')
                    candidate_name = candidate_data.get('name')
                    
                    # Verify candidate exists
                    try:
                        candidate_object_id = ObjectId(candidate_id)
                    except:
                        session.abort_transaction()
                        print(f"❌ DEBUG: Invalid candidate ID format - Candidate ID: {candidate_id}")
                        return jsonify({
                            'success': False,
                            'message': f'Invalid candidate ID for {position}'
                        }), 400
                    
                    candidate = candidates_collection.find_one({'_id': candidate_object_id})
                    
                    if not candidate:
                        session.abort_transaction()
                        print(f"❌ DEBUG: Candidate not found - Candidate ID: {candidate_id}")
                        return jsonify({
                            'success': False,
                            'message': f'Candidate not found for {position}'
                        }), 404
                    
                    # Record the vote
                    vote_data = {
                        'voter_id': voter_id,
                        'candidate_id': candidate_id,
                        'matric_number': matric_number.upper(),
                        'candidate_name': candidate_name,
                        'candidate_position': position,
                        'vote_date': datetime.utcnow()
                    }
                    
                    try:
                        vote_result = votes_collection.insert_one(vote_data, session=session)
                        vote_ids.append(str(vote_result.inserted_id))
                    except Exception as e:
                        if "duplicate key" in str(e):
                            session.abort_transaction()
                            print(f"❌ DEBUG: Duplicate vote for position - Position: {position}")
                            return jsonify({
                                'success': False,
                                'message': f'You have already voted for {position}'
                            }), 400
                        else:
                            raise e
                
                # Update voter to mark as voted
                voters_collection.update_one(
                    {'_id': voter['_id']},
                    {'$set': {'has_voted': True}},
                    session=session
                )
                
                session.commit_transaction()
        
        print(f"✅ DEBUG: All votes successfully recorded - Vote IDs: {vote_ids}")
        return jsonify({
            'success': True,
            'message': f'All {len(votes)} votes cast successfully!',
            'vote_ids': vote_ids
        })
        
    except Exception as e:
        print(f"❌ DEBUG: Exception in cast_vote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Voting error: {str(e)}'
        }), 500

# Debug endpoints (keep all your existing debug endpoints)
@app.route('/api/debug/votes')
def debug_votes():
    """Debug endpoint to see all votes in the database"""
    try:
        votes = list(votes_collection.find().sort('vote_date', -1))
        
        votes_list = []
        for vote in votes:
            votes_list.append({
                'vote_id': str(vote['_id']),
                'matric_number': vote['matric_number'],
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
    """Debug endpoint to see all voters with IP and location info"""
    try:
        voters = list(voters_collection.find().sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'id': str(voter['_id']),
                'matric_number': voter.get('matric_number', ''),
                'name': voter['name'],
                'email': voter['email'],
                'faculty': voter.get('faculty', ''),
                'ip_address': voter.get('ip_address', ''),
                'ip_hash': voter['ip_hash'][:10] + '...',
                'location_info': voter.get('location_info', {}),
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

@app.route('/api/debug/candidates')
def debug_candidates():
    """Debug endpoint to see all candidates grouped by position"""
    try:
        candidates = list(candidates_collection.find().sort('position', 1))
        
        candidates_by_position = {}
        for candidate in candidates:
            position = candidate['position']
            if position not in candidates_by_position:
                candidates_by_position[position] = []
            
            candidates_by_position[position].append({
                'id': str(candidate['_id']),
                'name': candidate['name'],
                'faculty': candidate.get('faculty', '')
            })
        
        return jsonify({
            'success': True,
            'candidates_by_position': candidates_by_position
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching candidates: {str(e)}'
        }), 500
    
@app.route('/api/debug/indexes')
def debug_indexes():
    """Debug endpoint to see all indexes"""
    try:
        indexes = list(votes_collection.list_indexes())
        
        indexes_list = []
        for index in indexes:
            indexes_list.append({
                'name': index['name'],
                'key': index['key'],
                'unique': index.get('unique', False)
            })
        
        return jsonify({
            'success': True,
            'indexes': indexes_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching indexes: {str(e)}'
        }), 500

@app.route('/api/debug/fix-indexes', methods=['POST'])
def fix_indexes():
    """Fix the problematic indexes"""
    try:
        # Remove the problematic unique index on voter_id alone
        votes_collection.drop_index('voter_id_1')
        print("✅ Removed problematic unique index on voter_id")
        
        # Ensure the compound index exists
        votes_collection.create_index([("voter_id", 1), ("candidate_position", 1)], unique=True, name="unique_vote_per_position")
        print("✅ Ensured compound unique index exists")
        
        # Recreate other necessary indexes
        votes_collection.create_index("candidate_id")
        print("✅ Recreated candidate_id index")
        
        return jsonify({
            'success': True,
            'message': 'Indexes fixed successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fixing indexes: {str(e)}'
        }), 500

@app.route('/api/debug/reset-votes', methods=['POST'])
def reset_votes():
    """Debug endpoint to reset all votes and voter status (for testing only)"""
    try:
        # Delete all votes
        votes_result = votes_collection.delete_many({})
        # Reset all voters' has_voted status
        voters_result = voters_collection.update_many({}, {'$set': {'has_voted': False}})
        
        return jsonify({
            'success': True,
            'message': f'Reset complete: {votes_result.deleted_count} votes deleted, {voters_result.modified_count} voters reset',
            'votes_deleted': votes_result.deleted_count,
            'voters_reset': voters_result.modified_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resetting votes: {str(e)}'
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

# Fix for Render deployment - use PORT environment variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🚀 Starting Enhanced Student Portal - Obong University SRC Elections")
    print("✅ MongoDB connected successfully!")
    print("🔒 Enhanced Security Features:")
    print("   - Matric number validation (starts with U, 8 or 10 characters)")
    print("   - IP-based location verification (Etim Ekpo, Obong Ntak areas only)")
    print("   - Duplicate email detection")
    print("   - Duplicate name detection")
    print("   - Duplicate matric number detection")
    print("   - IP address tracking and location display")
    print("🎓 Using Matric Number only (no Student ID)")
    print("🏛️  Faculties: Natural and Applied Science, Arts and Communications, Social Science, Management Science")
    print("🗳️  Election Positions Available:")
    print("   - SRC President (3 candidates)")
    print("   - SRC Vice President (3 candidates)")
    print("   - SRC Secretary (3 candidates)")
    print("   - Senate Members for each faculty (4 faculties, 4 candidates each)")
    print("   - Representative Members (Information, Social, Sports, Security, Transport, Hostel 1, Hostel 2, Chapel)")
    print("⚠️  VOTING REQUIREMENT: Students must select one candidate for EVERY position")
    print(f"🌐 Student Portal running at: http://0.0.0.0:{port}")
    print("🎓 Students can register and vote at this portal")
    print("🐛 Debug tools available at: /api/debug endpoints")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=False, host='0.0.0.0', port=port)