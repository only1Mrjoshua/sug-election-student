from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from bson.objectid import ObjectId
from flask_cors import CORS
import logging

# Import the separated data files
from student_voters import get_sample_voters
from student_candidates import get_sample_candidates

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

def initialize_database():
    """Initialize database with sample data from separate files if empty"""
    try:
        # Check if voters exist
        if voters_collection.count_documents({}) == 0:
            sample_voters = get_sample_voters()
            voters_collection.insert_many(sample_voters)
            logger.info(f"✅ {len(sample_voters)} sample voters added to database from file")
        
        # Check if candidates exist
        if candidates_collection.count_documents({}) == 0:
            real_candidates = get_sample_candidates()
            candidates_collection.insert_many(real_candidates)
            logger.info(f"✅ {len(real_candidates)} test candidates added to database from file")
        
        # Initialize election settings
        if election_settings_collection.count_documents({}) == 0:
            election_settings_collection.insert_one({
                'election_status': 'ongoing',
                'updated_at': datetime.utcnow()
            })
            logger.info("✅ Election settings initialized")
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

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

@app.route('/api/verify-voter', methods=['POST'])
def verify_voter():
    """Verify voter ID and return voter status"""
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
        voter_id = data.get('voter_id')
        
        logger.info(f"🔍 Voter verification attempt - Voter ID: {voter_id}, Election Status: {election_status}")
        
        if not voter_id:
            return jsonify({
                'success': False,
                'message': 'Voter ID is required'
            }), 400
        
        voter_id_upper = voter_id.upper()
        
        # Find voter by voter_id
        voter = voters_collection.find_one({'voter_id': voter_id_upper})
        
        if not voter:
            return jsonify({
                'success': False,
                'verified': False,
                'message': 'Invalid Voter ID. Please check your Voter ID and try again.'
            }), 404
        
        if voter.get('has_voted', False):
            return jsonify({
                'success': True,
                'verified': True,
                'can_vote': False,
                'message': 'This Voter ID has already voted. Each voter can only vote once.',
                'has_voted': True,
                'voter_name': voter.get('full_name', '')
            })
        else:
            return jsonify({
                'success': True,
                'verified': True,
                'can_vote': True,
                'message': 'Voter ID verified successfully. You can now vote.',
                'has_voted': False,
                'voter_name': voter.get('full_name', ''),
                'voter_id': voter_id_upper
            })
            
    except Exception as e:
        logger.error(f"❌ Voter verification exception - {e}")
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
        voter_id = data.get('voter_id')
        voter_name = data.get('voter_name')
        votes = data.get('votes')
        
        logger.info(f"🔍 Vote attempt received - Voter ID: {voter_id}, Voter: {voter_name}, Votes: {len(votes)} positions, Election Status: {election_status}")
        
        if not all([voter_id, voter_name, votes]) or len(votes) == 0:
            logger.error("❌ Missing required fields or no votes")
            return jsonify({
                'success': False,
                'message': 'Missing required fields or no votes selected'
            }), 400
        
        voter = voters_collection.find_one({'voter_id': voter_id.upper()})
        
        if not voter:
            logger.error(f"❌ Voter not found - Voter ID: {voter_id}")
            return jsonify({
                'success': False,
                'message': 'Voter not found. Please verify your Voter ID first.'
            }), 404
        
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
                        'voter_name': voter_name,
                        'candidate_id': candidate_id,
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