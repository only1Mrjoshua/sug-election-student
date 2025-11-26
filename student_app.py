from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from bson.objectid import ObjectId
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB configuration
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://only1MrJoshua:LovuLord2025@cluster0.9jqnavg.mongodb.net/election_db?retryWrites=true&w=majority")
DATABASE_NAME = "election_db"

# Initialize MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    logger.info("✅ Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"❌ Failed to connect to MongoDB: {e}")
    raise e

# Collections
voters_collection = db['voters']
candidates_collection = db['candidates']
votes_collection = db['votes']
election_settings_collection = db['election_settings']

# Valid matric numbers database
VALID_MATRIC_NUMBERS = {
    "U20241001", "U20241002", "U20241003", "U20241004", "U20241005",
    "U20241006", "U20241007", "U20241008", "U20241009", "U20241010",
    "U20241011", "U20241012", "U20241013", "U20241014", "U20241015",
    "U20241016", "U20241017", "U20241018", "U20241019", "U20241020",
    "U20241021", "U20241022", "U20241023", "U20241024", "U20241025",
    "U20242001", "U20242002", "U20242003", "U20242004", "U20242005",
    "U20242006", "U20242007", "U20242008", "U20242009", "U20242010",
    "U20242011", "U20242012", "U20242013", "U20242014", "U20242015",
    "U20242016", "U20242017", "U20242018", "U20242019", "U20242020",
    "U20242021", "U20242022", "U20242023", "U20242024", "U20242025",
    "U20243001", "U20243002", "U20243003", "U20243004", "U20243005",
    "U20243006", "U20243007", "U20243008", "U20243009", "U20243010",
    "U20243011", "U20243012", "U20243013", "U20243014", "U20243015",
    "U20243016", "U20243017", "U20243018", "U20243019", "U20243020",
    "U20243021", "U20243022", "U20243023", "U20243024", "U20243025",
    "U20244001", "U20244002", "U20244003", "U20244004", "U20244005",
    "U20244006", "U20244007", "U20244008", "U20244009", "U20244010",
    "U20244011", "U20244012", "U20244013", "U20244014", "U20244015",
    "U20244016", "U20244017", "U20244018", "U20244019", "U20244020",
    "U20244021", "U20244022", "U20244023", "U20244024", "U20244025"
}

def initialize_database():
    """Initialize database with sample data if empty"""
    try:
        # Check if candidates exist
        if candidates_collection.count_documents({}) == 0:
            test_candidates = [
                {
                    'name': 'John Chukwuma',
                    'position': 'SRC President',
                    'faculty': 'Faculty of Natural and Applied Sciences'
                },
                {
                    'name': 'Sarah Johnson', 
                    'position': 'SRC President',
                    'faculty': 'Faculty of Social Sciences'
                },
                {
                    'name': 'Michael Adebayo',
                    'position': 'SRC Vice President',
                    'faculty': 'Faculty of Management Sciences'
                },
                {
                    'name': 'Grace Okafor',
                    'position': 'SRC Secretary',
                    'faculty': 'Faculty of Arts and Education'
                },
                {
                    'name': 'David Mensah',
                    'position': 'SRC Treasurer', 
                    'faculty': 'Faculty of Natural and Applied Sciences'
                },
                {
                    'name': 'Peace Eze',
                    'position': 'SRC Treasurer',
                    'faculty': 'Faculty of Social Sciences'
                }
            ]
            candidates_collection.insert_many(test_candidates)
            logger.info("✅ Test candidates added to database")
        
        # Initialize election settings
        if election_settings_collection.count_documents({}) == 0:
            election_settings_collection.insert_one({
                'election_status': 'ongoing',
                'updated_at': datetime.utcnow()
            })
            logger.info("✅ Election settings initialized")
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

def validate_matric_number(matric_number):
    """Validate matric number format"""
    if not matric_number:
        return False
        
    matric_upper = matric_number.upper()
    
    if not matric_upper.startswith('U'):
        return False
    
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
        logger.error(f"❌ Error getting election status: {e}")
        return 'not_started'

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Obong University SRC Election API is running',
        'timestamp': datetime.utcnow().isoformat()
    })

# Student API Routes
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
        
        logger.info(f"🔍 Matric verification attempt - Matric: {matric_number}, Election Status: {election_status}")
        
        if not matric_number:
            return jsonify({
                'success': False,
                'message': 'Matric number is required'
            }), 400
        
        matric_upper = matric_number.upper()
        if not validate_matric_number(matric_number):
            return jsonify({
                'success': False,
                'message': 'Invalid matric number format. Must start with U and be exactly 8, 9 or 10 characters total'
            }), 400
        
        if not is_valid_matric(matric_number):
            return jsonify({
                'success': False,
                'verified': False,
                'message': 'Invalid matric number. Please check your matric number and try again.'
            })
        
        voter = voters_collection.find_one({'matric_number': matric_upper})
        
        if voter:
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
            try:
                voter_data = {
                    'matric_number': matric_upper,
                    'registration_date': datetime.utcnow(),
                    'has_voted': False
                }
                
                result = voters_collection.insert_one(voter_data)
                voter_id = str(result.inserted_id)
                
                logger.info(f"✅ Voter auto-registered - Matric: {matric_upper}")
                
                return jsonify({
                    'success': True,
                    'verified': True,
                    'can_vote': True,
                    'message': 'Matric number verified successfully. You can now vote.',
                    'has_voted': False
                })
                
            except Exception as e:
                logger.error(f"❌ Auto-registration error - {e}")
                if "duplicate key" in str(e):
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
        logger.error(f"❌ Matric verification exception - {e}")
        return jsonify({
            'success': False,
            'message': f'Verification error: {str(e)}'
        }), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get list of all candidates"""
    try:
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
        votes = data.get('votes')
        
        logger.info(f"🔍 Vote attempt received - Matric: {matric_number}, Votes: {len(votes)} positions, Election Status: {election_status}")
        
        if not all([matric_number, votes]) or len(votes) == 0:
            logger.error("❌ Missing required fields or no votes")
            return jsonify({
                'success': False,
                'message': 'Missing required fields or no votes selected'
            }), 400
        
        voter = voters_collection.find_one({'matric_number': matric_number.upper()})
        
        if not voter:
            logger.error(f"❌ Voter not found - Matric: {matric_number}")
            return jsonify({
                'success': False,
                'message': 'Voter not found. Please verify your matric number first.'
            }), 404
        
        voter_id = str(voter['_id'])
        
        if voter.get('has_voted', False):
            logger.error(f"❌ Voter already voted - Voter ID: {voter_id}")
            return jsonify({
                'success': False,
                'message': 'You have already voted'
            }), 400
        
        vote_ids = []
        
        with client.start_session() as session:
            with session.start_transaction():
                for position, candidate_data in votes.items():
                    candidate_id = candidate_data.get('id')
                    candidate_name = candidate_data.get('name')
                    
                    try:
                        candidate_object_id = ObjectId(candidate_id)
                    except:
                        session.abort_transaction()
                        logger.error(f"❌ Invalid candidate ID format - Candidate ID: {candidate_id}")
                        return jsonify({
                            'success': False,
                            'message': f'Invalid candidate ID for {position}'
                        }), 400
                    
                    candidate = candidates_collection.find_one({'_id': candidate_object_id})
                    
                    if not candidate:
                        session.abort_transaction()
                        logger.error(f"❌ Candidate not found - Candidate ID: {candidate_id}")
                        return jsonify({
                            'success': False,
                            'message': f'Candidate not found for {position}'
                        }), 404
                    
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
                            logger.error(f"❌ Duplicate vote for position - Position: {position}")
                            return jsonify({
                                'success': False,
                                'message': f'You have already voted for {position}'
                            }), 400
                        else:
                            raise e
                
                voters_collection.update_one(
                    {'_id': voter['_id']},
                    {'$set': {'has_voted': True}},
                    session=session
                )
                
                session.commit_transaction()
        
        logger.info(f"✅ All votes successfully recorded - Vote IDs: {vote_ids}")
        return jsonify({
            'success': True,
            'message': f'All {len(votes)} votes cast successfully!',
            'vote_ids': vote_ids
        })
        
    except Exception as e:
        logger.error(f"❌ Exception in cast_vote: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Voting error: {str(e)}'
        }), 500

# Initialize database when app starts
initialize_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"🚀 Starting Student Portal API - Obong University SRC Elections on port {port}")
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port)