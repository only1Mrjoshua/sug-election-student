from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
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
election_settings_collection = db['election_settings']

# Valid matric numbers database (100 mock matric numbers)
VALID_MATRIC_NUMBERS = {
    # Natural and Applied Science (25 students)
    "U20241001", "U20241002", "U20241003", "U20241004", "U20241005",
    "U20241006", "U20241007", "U20241008", "U20241009", "U20241010",
    "U20241011", "U20241012", "U20241013", "U20241014", "U20241015",
    "U20241016", "U20241017", "U20241018", "U20241019", "U20241020",
    "U20241021", "U20241022", "U20241023", "U20241024", "U20241025",
    
    # Arts and Communications (25 students)
    "U20242001", "U20242002", "U20242003", "U20242004", "U20242005",
    "U20242006", "U20242007", "U20242008", "U20242009", "U20242010",
    "U20242011", "U20242012", "U20242013", "U20242014", "U20242015",
    "U20242016", "U20242017", "U20242018", "U20242019", "U20242020",
    "U20242021", "U20242022", "U20242023", "U20242024", "U20242025",
    
    # Social Science (25 students)
    "U20243001", "U20243002", "U20243003", "U20243004", "U20243005",
    "U20243006", "U20243007", "U20243008", "U20243009", "U20243010",
    "U20243011", "U20243012", "U20243013", "U20243014", "U20243015",
    "U20243016", "U20243017", "U20243018", "U20243019", "U20243020",
    "U20243021", "U20243022", "U20243023", "U20243024", "U20243025",
    
    # Management Science (25 students)
    "U20244001", "U20244002", "U20244003", "U20244004", "U20244005",
    "U20244006", "U20244007", "U20244008", "U20244009", "U20244010",
    "U20244011", "U20244012", "U20244013", "U20244014", "U20244015",
    "U20244016", "U20244017", "U20244018", "U20244019", "U20244020",
    "U20244021", "U20244022", "U20244023", "U20244024", "U20244025"
}

def init_db():
    """Initialize database with sample data if needed"""
    # Clean up any existing problematic indexes
    try:
        # Clean up voters collection indexes
        current_voter_indexes = list(voters_collection.list_indexes())
        for index in current_voter_indexes:
            index_name = index['name']
            # Remove any email indexes
            if index_name == 'email_1':
                voters_collection.drop_index('email_1')
                print("✅ Removed email index from voters collection")
        
        # Clean up votes collection indexes  
        current_vote_indexes = list(votes_collection.list_indexes())
        for index in current_vote_indexes:
            index_name = index['name']
            if index_name == 'voter_id_1' and index.get('unique', False):
                votes_collection.drop_index('voter_id_1')
                print("✅ Removed problematic unique index on voter_id")
    except Exception as e:
        print(f"ℹ️  Index cleanup: {e}")

    # Create correct indexes - MATRIC NUMBER ONLY
    indexes_to_create = [
        (voters_collection, "matric_number", True),  # Only unique index we need
        (votes_collection, "candidate_id", False),
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

    # Initialize election settings if not exists
    if election_settings_collection.count_documents({}) == 0:
        election_settings_collection.insert_one({
            'election_status': 'not_started',
            'start_time': None,
            'end_time': None,
            'updated_at': datetime.utcnow()
        })
        print("✅ Election settings initialized")

    # Add REAL candidates if none exist
    if candidates_collection.count_documents({}) == 0:
        real_candidates = [
            # President (3 candidates)
            {
                "name": "Olukunle Tomiwa Covenant",
                "position": "President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Kennedy Solomon", 
                "position": "President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Jeremiah Gideon Emmanuel",
                "position": "President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Vice President (2 candidates)
            {
                "name": "Onwuoha Confidence Daberechi",
                "position": "Vice President",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Babade Beatrice Jonathan",
                "position": "Vice President",
                "faculty": "Arts and Communications",
                "created_at": datetime.utcnow()
            },
            
            # Financial Secretary (1 candidate)
            {
                "name": "Dimkpa Raymond Baribeebi",
                "position": "Financial Secretary",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Director of Transport (1 candidate)
            {
                "name": "Mbang Donnoble Godwin",
                "position": "Director of Transport",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Director of Socials (2 candidates)
            {
                "name": "Olukunle Titilola Oyindamola",
                "position": "Director of Socials",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Alasy Clinton Ebubechukwu",
                "position": "Director of Socials",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            
            # Director of Sports (3 candidates)
            {
                "name": "Collins Jacob",
                "position": "Director of Sports",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Chisom Ejims",
                "position": "Director of Sports",
                "faculty": "Management Science",
                "created_at": datetime.utcnow()
            },
            {
                "name": "Davidson Lawrence",
                "position": "Director of Sports",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Director of Information (1 candidate)
            {
                "name": "Meshach Efioke",
                "position": "Director of Information",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            },
            
            # Student Chaplain (1 candidate)
            {
                "name": "Abraham Raymond",
                "position": "Student Chaplain",
                "faculty": "Natural and Applied Science",
                "created_at": datetime.utcnow()
            }
        ]
        candidates_collection.insert_many(real_candidates)
        print("✅ REAL candidates added to MongoDB")
        print("📋 Candidate Positions Summary:")
        print("   - President: 3 candidates")
        print("   - Vice President: 2 candidates") 
        print("   - Financial Secretary: 1 candidate")
        print("   - Director of Transport: 1 candidate")
        print("   - Director of Socials: 2 candidates")
        print("   - Director of Sports: 3 candidates")
        print("   - Director of Information: 1 candidate")
        print("   - Student Chaplain: 1 candidate")
    else:
        print("✅ Candidates already exist in database")

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

def is_valid_matric(matric_number):
    """Check if matric number is in our valid list"""
    return matric_number.upper() in VALID_MATRIC_NUMBERS

def get_election_status():
    """Get current election status from database"""
    try:
        election_settings = election_settings_collection.find_one({})
        if election_settings:
            return election_settings.get('election_status', 'not_started')
        return 'not_started'
    except Exception as e:
        print(f"❌ Error getting election status: {e}")
        return 'not_started'

# Initialize database
init_db()

@app.route('/')
def student_home():
    """Student portal home page"""
    return render_template('student_portal.html')

@app.route('/api/election-status', methods=['GET'])
def get_election_status_api():
    """Get current election status"""
    try:
        election_status = get_election_status()
        return jsonify({
            'success': True,
            'election_status': election_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting election status: {str(e)}'
        }), 500

@app.route('/api/verify-matric', methods=['POST'])
def verify_matric():
    """Verify matric number and return student status"""
    try:
        # Check election status first
        election_status = get_election_status()
        
        if election_status == 'not_started':
            return jsonify({
                'success': False,
                'message': 'Voting has not started yet. Please wait for the election to begin.'
            }), 400
        elif election_status == 'paused':
            return jsonify({
                'success': False,
                'message': 'Voting has been temporarily paused. Please try again later.'
            }), 400
        elif election_status == 'ended':
            return jsonify({
                'success': False,
                'message': 'Voting has ended. You can no longer cast your vote.'
            }), 400
        
        data = request.get_json()
        matric_number = data.get('matric_number')
        
        print(f"🔍 DEBUG: Matric verification attempt - Matric: {matric_number}, Election Status: {election_status}")
        
        if not matric_number:
            return jsonify({
                'success': False,
                'message': 'Matric number is required'
            }), 400
        
        # Validate matric number format
        matric_upper = matric_number.upper()
        if not validate_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must start with U and be exactly 8, 9 or 10 characters total'
            }), 400
        
        # Check if matric number is valid
        if not is_valid_matric(matric_number):
            return jsonify({
                'success': False,
                'verified': False,
                'message': 'Invalid matric number. Please check your matric number and try again.'
            })
        
        # Check if student is already registered/voted
        voter = voters_collection.find_one({'matric_number': matric_upper})
        
        if voter:
            # Student is registered, check if they can vote
            if voter.get('has_voted', False):
                return jsonify({
                    'success': True,
                    'verified': True,
                    'can_vote': False,
                    'message': 'This matric number has already voted. Each student can only vote once.',
                    'has_voted': True
                })
            else:
                return jsonify({
                    'success': True,
                    'verified': True,
                    'can_vote': True,
                    'message': 'Matric number verified successfully. You can now vote.',
                    'has_voted': False
                })
        else:
            # Valid matric number but not registered yet - auto register
            try:
                voter_data = {
                    'matric_number': matric_upper,
                    'registration_date': datetime.utcnow(),
                    'has_voted': False
                }
                
                result = voters_collection.insert_one(voter_data)
                voter_id = str(result.inserted_id)
                
                print(f"✅ DEBUG: Voter auto-registered - Matric: {matric_upper}")
                
                return jsonify({
                    'success': True,
                    'verified': True,
                    'can_vote': True,
                    'message': 'Matric number verified successfully. You can now vote.',
                    'has_voted': False
                })
                
            except Exception as e:
                print(f"❌ DEBUG: Auto-registration error - {e}")
                if "duplicate key" in str(e):
                    # This should rarely happen now, but handle it gracefully
                    existing_voter = voters_collection.find_one({'matric_number': matric_upper})
                    if existing_voter:
                        return jsonify({
                            'success': False,
                            'message': 'Matric number already exists in system'
                        }), 400
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'Registration error. Please try again.'
                        }), 400
                else:
                    raise e
            
    except Exception as e:
        print(f"❌ DEBUG: Matric verification exception - {e}")
        return jsonify({
            'success': False,
            'message': f'Verification error: {str(e)}'
        }), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get list of all candidates"""
    try:
        # Check election status
        election_status = get_election_status()
        
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
            'candidates': candidates_list,
            'election_status': election_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching candidates: {str(e)}'
        }), 500

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    """Cast votes for multiple candidates at once"""
    try:
        # Check election status first
        election_status = get_election_status()
        
        if election_status == 'not_started':
            return jsonify({
                'success': False,
                'message': 'Voting has not started yet. Please wait for the election to begin.'
            }), 400
        elif election_status == 'paused':
            return jsonify({
                'success': False,
                'message': 'Voting has been temporarily paused. Please try again later.'
            }), 400
        elif election_status == 'ended':
            return jsonify({
                'success': False,
                'message': 'Voting has ended. You can no longer cast your vote.'
            }), 400
        
        data = request.get_json()
        matric_number = data.get('matric_number')
        votes = data.get('votes')  # Dictionary of {position: {id, name}}
        
        print(f"🔍 DEBUG: Vote attempt received - Matric: {matric_number}, Votes: {len(votes)} positions, Election Status: {election_status}")
        
        if not all([matric_number, votes]) or len(votes) == 0:
            print("❌ DEBUG: Missing required fields or no votes")
            return jsonify({
                'success': False,
                'message': 'Missing required fields or no votes selected'
            }), 400
        
        # Verify voter exists and is valid
        voter = voters_collection.find_one({'matric_number': matric_number.upper()})
        
        if not voter:
            print(f"❌ DEBUG: Voter not found - Matric: {matric_number}")
            return jsonify({
                'success': False,
                'message': 'Voter not found. Please verify your matric number first.'
            }), 404
        
        voter_id = str(voter['_id'])
        
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
    """Debug endpoint to see all voters"""
    try:
        voters = list(voters_collection.find().sort('registration_date', -1))
        
        voters_list = []
        for voter in voters:
            voters_list.append({
                'id': str(voter['_id']),
                'matric_number': voter.get('matric_number', ''),
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

@app.route('/api/debug/delete-database', methods=['POST'])
def delete_database():
    """DEBUG: Completely delete the database"""
    try:
        client.drop_database(DATABASE_NAME)
        return jsonify({
            'success': True,
            'message': 'Database deleted successfully. Restart the app to recreate it.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting database: {str(e)}'
        }), 500

@app.route('/api/debug/valid-matrics')
def debug_valid_matrics():
    """Debug endpoint to see all valid matric numbers"""
    return jsonify({
        'success': True,
        'valid_matric_numbers': list(VALID_MATRIC_NUMBERS),
        'total_valid': len(VALID_MATRIC_NUMBERS)
    })

# Fix for Render deployment - use PORT environment variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🚀 Starting Simplified Student Portal - Obong University SRC Elections")
    print("✅ MongoDB connected successfully!")
    print("🎓 Using Matric Number Verification Only")
    print(f"📋 Total Valid Matric Numbers: {len(VALID_MATRIC_NUMBERS)}")
    print("🔒 Security Features:")
    print("   - Matric number validation (100 pre-approved numbers)")
    print("   - One vote per student")
    print("   - One vote per position per student")
    print("   - Election status control (not started, ongoing, paused, ended)")
    print("🗳️  REAL ELECTION CANDIDATES:")
    print("   - President: 3 candidates")
    print("   - Vice President: 2 candidates")
    print("   - Financial Secretary: 1 candidate")
    print("   - Director of Transport: 1 candidate")
    print("   - Director of Socials: 2 candidates")
    print("   - Director of Sports: 3 candidates")
    print("   - Director of Information: 1 candidate")
    print("   - Student Chaplain: 1 candidate")
    print("⚠️  VOTING REQUIREMENT: Students must select one candidate for EVERY position")
    print(f"🌐 Student Portal running at: http://0.0.0.0:{port}")
    print("🎓 Students can verify matric number and vote at this portal")
    print("🐛 Debug tools available at: /api/debug endpoints")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=False, host='0.0.0.0', port=port)