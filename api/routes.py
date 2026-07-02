"""
API routes for account management, farming control, and statistics.
"""
from datetime import datetime
import logging

from flask import Blueprint, jsonify, request
from sqlalchemy import case, func

from models import Account, FarmSession, FarmingConfig, Log, db
from tasks import launch_farming_task

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

VALID_PLATFORMS = {'ios', 'android'}
VALID_VERSIONS = {'jp', 'gb'}


def _get_payload():
    return request.get_json(silent=True) or {}


def _error(message, status=400):
    return jsonify({'error': message}), status


def _get_account_or_404(account_id):
    return db.session.get(Account, account_id)


def _ensure_config(account, payload=None):
    payload = payload or {}
    config = account.farming_config or FarmingConfig(account=account)
    config.auto_sell = payload.get('auto_sell', config.auto_sell if config.id else True)
    config.refill_strategy = payload.get('refill_strategy', config.refill_strategy if config.id else 'skip')
    config.farming_content = payload.get(
        'farming_content',
        config.farming_content if config.id else ['gifts', 'story', 'events', 'missions', 'auto_sell'],
    )
    db.session.add(config)
    return config


@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


@api_bp.route('/accounts', methods=['POST'])
def create_account():
    data = _get_payload()
    username = (data.get('username') or '').strip()
    password = data.get('password')
    platform = (data.get('platform') or 'android').lower()
    version = (data.get('version') or 'gb').lower()

    if not username or not password:
        return _error('username and password required')
    if platform not in VALID_PLATFORMS:
        return _error('platform must be ios or android')
    if version not in VALID_VERSIONS:
        return _error('version must be jp or gb')
    if Account.query.filter_by(username=username).first():
        return _error('username already exists', 409)

    account = Account(
        username=username,
        email=data.get('email'),
        platform=platform,
        version=version,
        farming_status='idle',
    )
    if data.get('device_id'):
        account.device_id = data.get('device_id')
    account.password = password
    db.session.add(account)
    db.session.flush()
    _ensure_config(account, data.get('farming_config') or {})
    db.session.add(Log(account_id=account.id, message='Account created', level='SUCCESS'))
    db.session.commit()

    return jsonify({'message': 'Account created successfully', 'account': account.to_dict()}), 201


@api_bp.route('/accounts', methods=['GET'])
def list_accounts():
    accounts = Account.query.order_by(Account.created_at.desc()).all()
    return jsonify({'accounts': [account.to_dict() for account in accounts], 'count': len(accounts)}), 200


@api_bp.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    active_session = FarmSession.query.filter(
        FarmSession.account_id == account.id,
        FarmSession.status.in_(['queued', 'running', 'stopping']),
    ).order_by(FarmSession.start_time.desc()).first()

    return jsonify({
        'account': account.to_dict(),
        'current_session': active_session.to_dict() if active_session else None,
        'recent_sessions': [session.to_dict() for session in account.sessions[:10]],
        'recent_logs': [log.to_dict() for log in account.logs[:20]],
    }), 200


@api_bp.route('/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    data = _get_payload()

    if 'username' in data:
        username = (data.get('username') or '').strip()
        if not username:
            return _error('username cannot be empty')
        existing = Account.query.filter(Account.username == username, Account.id != account.id).first()
        if existing:
            return _error('username already exists', 409)
        account.username = username

    if 'password' in data and data['password']:
        account.password = data['password']

    if 'platform' in data:
        platform = (data.get('platform') or '').lower()
        if platform not in VALID_PLATFORMS:
            return _error('platform must be ios or android')
        account.platform = platform

    if 'version' in data:
        version = (data.get('version') or '').lower()
        if version not in VALID_VERSIONS:
            return _error('version must be jp or gb')
        account.version = version

    for field in ('email', 'device_id', 'optc_id'):
        if field in data:
            setattr(account, field, data.get(field))

    if 'farming_config' in data:
        _ensure_config(account, data['farming_config'])

    db.session.add(Log(account_id=account.id, message='Account updated', level='INFO'))
    db.session.commit()
    return jsonify({'message': 'Account updated successfully', 'account': account.to_dict()}), 200


@api_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': 'Account deleted successfully'}), 200


@api_bp.route('/farming/start', methods=['POST'])
def start_farming():
    data = _get_payload()
    account_id = data.get('account_id')
    duration = data.get('duration', 1)
    farming_mode = (data.get('farming_mode') or 'balanced').lower()

    if account_id is None:
        return _error('account_id is required')

    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    active_session = FarmSession.query.filter(
        FarmSession.account_id == account.id,
        FarmSession.status.in_(['queued', 'running', 'stopping']),
    ).first()
    if active_session:
        return _error('Account already has an active farming session', 409)

    session = FarmSession(
        account_id=account.id,
        farming_mode=farming_mode,
        duration_hours=float(duration),
        status='queued',
    )
    account.is_farming = True
    account.farming_status = 'queued'
    account.farming_mode = farming_mode
    account.total_sessions += 1
    db.session.add(session)
    db.session.add(Log(account_id=account.id, message=f'Queued farming mode {farming_mode}', level='INFO'))
    db.session.commit()

    launch_result = launch_farming_task(account.id, duration, farming_mode, session.id)
    db.session.refresh(session)
    return jsonify({
        'message': 'Farming started',
        'session': session.to_dict(),
        'task': launch_result,
    }), 202


@api_bp.route('/farming/stop/<int:account_id>', methods=['POST'])
def stop_farming(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    session = FarmSession.query.filter(
        FarmSession.account_id == account.id,
        FarmSession.status.in_(['queued', 'running', 'stopping']),
    ).order_by(FarmSession.start_time.desc()).first()
    if not session:
        return _error('No active farming session found', 404)

    session.stop_requested = True
    session.status = 'stopping'
    account.farming_status = 'stopping'
    account.is_farming = True
    db.session.add(Log(account_id=account.id, message='Stop requested for farming session', level='INFO'))
    db.session.commit()

    return jsonify({'message': 'Stop requested', 'session': session.to_dict()}), 200


@api_bp.route('/farming/status/<int:account_id>', methods=['GET'])
def get_farming_status(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    session = FarmSession.query.filter(
        FarmSession.account_id == account.id,
    ).order_by(FarmSession.start_time.desc()).first()

    return jsonify({
        'account': account.to_dict(),
        'current_session': session.to_dict() if session else None,
    }), 200


@api_bp.route('/farming/sessions/<int:account_id>', methods=['GET'])
def get_farming_sessions(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    sessions = FarmSession.query.filter_by(account_id=account.id).order_by(FarmSession.start_time.desc()).all()
    return jsonify({'sessions': [session.to_dict() for session in sessions], 'count': len(sessions)}), 200


@api_bp.route('/farming/logs/<int:account_id>', methods=['GET'])
def get_farming_logs(account_id):
    account = _get_account_or_404(account_id)
    if not account:
        return _error('Account not found', 404)

    logs = Log.query.filter_by(account_id=account.id).order_by(Log.timestamp.desc()).all()
    return jsonify({'logs': [entry.to_dict() for entry in logs], 'count': len(logs)}), 200


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    totals = db.session.query(
        func.count(Account.id),
        func.sum(case((Account.is_farming.is_(True), 1), else_=0)),
        func.sum(Account.total_items_farmed),
        func.sum(Account.total_exp_gained),
    ).one()
    session_totals = db.session.query(
        func.count(FarmSession.id),
        func.sum(case((FarmSession.status.in_(['queued', 'running', 'stopping']), 1), else_=0)),
    ).one()

    stats = {
        'total_accounts': totals[0] or 0,
        'accounts_farming': totals[1] or 0,
        'total_items_collected': totals[2] or 0,
        'total_exp_gained': totals[3] or 0,
        'total_sessions': session_totals[0] or 0,
        'active_sessions': session_totals[1] or 0,
        'log_entries': Log.query.count(),
    }
    return jsonify(stats), 200


@api_bp.errorhandler(400)
def bad_request(_error_obj):
    return _error('Bad request', 400)


@api_bp.errorhandler(404)
def not_found(_error_obj):
    return _error('Not found', 404)


@api_bp.errorhandler(500)
def server_error(error):
    logger.error('Server error: %s', error)
    return _error('Internal server error', 500)
