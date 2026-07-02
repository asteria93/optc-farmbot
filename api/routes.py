"""
API routes for the bot
Endpoints for account management, farming control, and status monitoring
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from sqlalchemy.exc import IntegrityError

from models import db, Account, FarmSession, Log
from bot.services import (
    account_statistics,
    create_account_record,
    create_farm_session,
    farming_statistics,
    normalize_preferences,
    parse_mode,
    parse_strategy,
    stop_farm_session,
)
from tasks import enqueue_farm_session

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected',
    }), 200

# ============ ACCOUNT ENDPOINTS ============

@api_bp.route('/accounts', methods=['GET'])
def list_accounts():
    """Get all accounts"""
    accounts = [account.to_dict() for account in Account.query.order_by(Account.created_at.desc()).all()]
    return jsonify({'accounts': accounts, 'count': len(accounts)}), 200

@api_bp.route('/accounts', methods=['POST'])
def create_account():
    """Create a new account"""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not username or not email or not password:
        return jsonify({'error': 'username, email, and password required'}), 400

    try:
        account = create_account_record(
            username=username,
            email=email,
            password=password,
            preferences=normalize_preferences(data.get('preferences')),
        )
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'username or email already exists'}), 409

    logger.info('Account created: %s', username)
    return jsonify({
        'message': 'Account created successfully',
        'account': account.to_dict(),
    }), 201

@api_bp.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """Get account details"""
    account = db.session.get(Account, account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    recent_sessions = [
        session.to_dict()
        for session in FarmSession.query.filter_by(account_id=account.id).order_by(FarmSession.start_time.desc()).limit(5).all()
    ]
    return jsonify({'account': account.to_dict(), 'recent_sessions': recent_sessions}), 200

@api_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    """Delete an account"""
    account = db.session.get(Account, account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    if account.is_farming:
        return jsonify({'error': 'Stop farming before deleting this account'}), 409

    db.session.delete(account)
    db.session.commit()
    logger.info('Account deleted: %s', account_id)
    
    return jsonify({'message': 'Account deleted successfully'}), 200

# ============ FARMING ENDPOINTS ============

@api_bp.route('/farming/start', methods=['POST'])
def start_farming():
    """Start farming for an account"""
    data = request.get_json(silent=True) or {}
    account_id = data.get('account_id')
    mode = data.get('mode', 'all')
    strategy = data.get('strategy', 'moderate')

    account = db.session.get(Account, int(account_id)) if account_id else None
    if not account:
        return jsonify({'error': 'Account not found'}), 404

    if account.is_farming:
        return jsonify({'error': 'Account already has an active farming session'}), 409

    try:
        parse_mode(mode)
        parse_strategy(strategy)
    except ValueError:
        return jsonify({'error': 'Invalid farming mode or strategy'}), 400

    session = create_farm_session(account, mode, strategy)
    task_id, task_result = enqueue_farm_session(
        session.id,
        force_sync=bool(data.get('run_immediately')) or bool(request.args.get('sync')),
    )
    session.task_id = task_id
    db.session.commit()

    if task_result:
        session = db.session.get(FarmSession, session.id)

    logger.info('Farming started: %s - %s', account_id, mode)
    return jsonify({
        'message': 'Farming started',
        'session': session.to_dict(),
    }), 202

@api_bp.route('/farming/stop/<int:session_id>', methods=['POST'])
def stop_farming(session_id):
    """Stop farming session"""
    session = db.session.get(FarmSession, session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    if session.status in {'completed', 'failed', 'stopped'}:
        return jsonify({'error': f'Session already {session.status}'}), 409

    stop_farm_session(session)
    logger.info('Farming stopped: %s', session_id)
    
    return jsonify({
        'message': 'Farming stopped',
        'session': session.to_dict(),
    }), 200

@api_bp.route('/farming/status/<int:session_id>', methods=['GET'])
def get_farming_status(session_id):
    """Get farming session status"""
    session = db.session.get(FarmSession, session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    logs = [
        log.to_dict()
        for log in Log.query.filter_by(session_id=session.id).order_by(Log.timestamp.desc()).limit(10).all()
    ]
    
    return jsonify({
        'session': session.to_dict(),
        'account_stats': session.account.to_dict(),
        'logs': logs,
    }), 200

@api_bp.route('/farming/sessions', methods=['GET'])
def list_farming_sessions():
    """Get all farming sessions"""
    sessions = [
        session.to_dict()
        for session in FarmSession.query.order_by(FarmSession.start_time.desc()).all()
    ]
    return jsonify({
        'sessions': sessions,
        'count': len(sessions),
    }), 200

# ============ STATS ENDPOINTS ============

@api_bp.route('/stats/accounts', methods=['GET'])
def account_stats():
    """Get account statistics"""
    return jsonify(account_statistics()), 200

@api_bp.route('/stats/farming', methods=['GET'])
def farming_stats():
    """Get farming statistics"""
    return jsonify(farming_statistics()), 200


@api_bp.route('/logs', methods=['GET'])
def list_logs():
    """Get recent automation logs"""
    account_id = request.args.get('account_id', type=int)
    session_id = request.args.get('session_id', type=int)

    query = Log.query.order_by(Log.timestamp.desc())
    if account_id:
        query = query.filter_by(account_id=account_id)
    if session_id:
        query = query.filter_by(session_id=session_id)

    logs = [log.to_dict() for log in query.limit(50).all()]
    return jsonify({'logs': logs, 'count': len(logs)}), 200

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
