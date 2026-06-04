"""
API routes for the bot
Endpoints for account management, farming control, and status monitoring
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# In-memory storage for demo (replace with database)
accounts_store = {}
farming_sessions = {}

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
    }), 200

# ============ ACCOUNT ENDPOINTS ============

@api_bp.route('/accounts', methods=['GET'])
def list_accounts():
    """Get all accounts"""
    accounts = [
        {
            'id': acc_id,
            'username': acc.get('username'),
            'level': acc.get('level'),
            'status': acc.get('status'),
            'created_at': acc.get('created_at'),
        }
        for acc_id, acc in accounts_store.items()
    ]
    return jsonify({'accounts': accounts, 'count': len(accounts)}), 200

@api_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'username and password required'}), 400
    
    import uuid
    account_id = str(uuid.uuid4())
    
    account = {
        'id': account_id,
        'username': data.get('username'),
        'email': data.get('email', ''),
        'created_at': datetime.utcnow().isoformat(),
        'status': 'active',
        'level': 1,
        'berry': 0,
        'gold': 0,
        'experience': 0,
    }
    
    accounts_store[account_id] = account
    logger.info(f'Account created: {data.get("username")}')
    
    return jsonify({
        'message': 'Account created successfully',
        'account': account,
    }), 201

@api_bp.route('/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    """Get account details"""
    account = accounts_store.get(account_id)
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    return jsonify({'account': account}), 200

@api_bp.route('/accounts/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    if account_id not in accounts_store:
        return jsonify({'error': 'Account not found'}), 404
    
    del accounts_store[account_id]
    logger.info(f'Account deleted: {account_id}')
    
    return jsonify({'message': 'Account deleted successfully'}), 200

# ============ FARMING ENDPOINTS ============

@api_bp.route('/farming/start', methods=['POST'])
def start_farming():
    """Start farming for an account"""
    data = request.get_json()
    account_id = data.get('account_id')
    mode = data.get('mode', 'all')
    strategy = data.get('strategy', 'moderate')
    
    if not account_id or account_id not in accounts_store:
        return jsonify({'error': 'Account not found'}), 404
    
    import uuid
    session_id = str(uuid.uuid4())
    
    session = {
        'session_id': session_id,
        'account_id': account_id,
        'mode': mode,
        'strategy': strategy,
        'status': 'active',
        'start_time': datetime.utcnow().isoformat(),
        'runs': 0,
    }
    
    farming_sessions[session_id] = session
    logger.info(f'Farming started: {account_id} - {mode}')
    
    return jsonify({
        'message': 'Farming started',
        'session': session,
    }), 200

@api_bp.route('/farming/stop/<session_id>', methods=['POST'])
def stop_farming(session_id):
    """Stop farming session"""
    session = farming_sessions.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    session['status'] = 'stopped'
    session['end_time'] = datetime.utcnow().isoformat()
    
    logger.info(f'Farming stopped: {session_id}')
    
    return jsonify({
        'message': 'Farming stopped',
        'session': session,
    }), 200

@api_bp.route('/farming/status/<session_id>', methods=['GET'])
def get_farming_status(session_id):
    """Get farming session status"""
    session = farming_sessions.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    account = accounts_store.get(session['account_id'])
    
    return jsonify({
        'session': session,
        'account_stats': {
            'level': account.get('level'),
            'berry': account.get('berry'),
            'gold': account.get('gold'),
            'experience': account.get('experience'),
        }
    }), 200

@api_bp.route('/farming/sessions', methods=['GET'])
def list_farming_sessions():
    """Get all farming sessions"""
    sessions = list(farming_sessions.values())
    return jsonify({
        'sessions': sessions,
        'count': len(sessions),
    }), 200

# ============ STATS ENDPOINTS ============

@api_bp.route('/stats/accounts', methods=['GET'])
def account_stats():
    """Get account statistics"""
    total_accounts = len(accounts_store)
    active_accounts = sum(1 for acc in accounts_store.values() if acc.get('status') == 'active')
    total_level = sum(acc.get('level', 0) for acc in accounts_store.values())
    total_rewards = sum(acc.get('berry', 0) + acc.get('gold', 0) for acc in accounts_store.values())
    
    return jsonify({
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'average_level': total_level / total_accounts if total_accounts > 0 else 0,
        'total_rewards_earned': total_rewards,
    }), 200

@api_bp.route('/stats/farming', methods=['GET'])
def farming_stats():
    """Get farming statistics"""
    total_sessions = len(farming_sessions)
    active_sessions = sum(1 for s in farming_sessions.values() if s.get('status') == 'active')
    total_runs = sum(s.get('runs', 0) for s in farming_sessions.values())
    
    return jsonify({
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'total_runs': total_runs,
    }), 200

# ============ ERROR HANDLERS ============

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@api_bp.errorhandler(500)
def server_error(error):
    logger.error(f'Server error: {error}')
    return jsonify({'error': 'Internal server error'}), 500
