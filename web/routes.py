"""
Web dashboard routes.
"""
from flask import Blueprint, redirect, render_template, request, url_for

from models import Account, FarmSession, Log
from tasks import launch_farming_task
from api.routes import _ensure_config
from models import db

web_bp = Blueprint('web', __name__)


@web_bp.route('/', methods=['GET'])
def dashboard():
    accounts = Account.query.order_by(Account.created_at.desc()).all()
    stats = {
        'total_accounts': len(accounts),
        'active_sessions': FarmSession.query.filter(FarmSession.status.in_(['queued', 'running', 'stopping'])).count(),
        'total_items': sum(account.total_items_farmed for account in accounts),
        'total_exp': sum(account.total_exp_gained for account in accounts),
    }
    recent_logs = Log.query.order_by(Log.timestamp.desc()).limit(20).all()
    return render_template('dashboard.html', accounts=accounts, stats=stats, recent_logs=recent_logs)


@web_bp.route('/account/<int:account_id>', methods=['GET'])
def account_details(account_id):
    account = Account.query.get_or_404(account_id)
    sessions = FarmSession.query.filter_by(account_id=account.id).order_by(FarmSession.start_time.desc()).all()
    logs = Log.query.filter_by(account_id=account.id).order_by(Log.timestamp.desc()).all()
    return render_template('account.html', account=account, sessions=sessions, logs=logs)


@web_bp.route('/account/create', methods=['POST'])
def create_account():
    platform = (request.form.get('platform') or 'android').lower()
    version = (request.form.get('version') or 'gb').lower()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        return redirect(url_for('web.dashboard'))
    if Account.query.filter_by(username=username).first():
        return redirect(url_for('web.dashboard'))

    account = Account(
        username=username,
        platform=platform,
        version=version,
        email=request.form.get('email') or None,
    )
    if request.form.get('device_id'):
        account.device_id = request.form.get('device_id')
    account.password = password
    db.session.add(account)
    db.session.flush()
    _ensure_config(account, {
        'auto_sell': request.form.get('auto_sell', 'true').lower() != 'false',
        'refill_strategy': request.form.get('refill_strategy') or 'skip',
        'farming_content': request.form.getlist('farming_content') or ['gifts', 'story', 'events', 'missions', 'auto_sell'],
    })
    db.session.add(Log(account_id=account.id, message='Account created from dashboard', level='SUCCESS'))
    db.session.commit()
    return redirect(url_for('web.account_details', account_id=account.id))


@web_bp.route('/account/<int:account_id>/start-farming', methods=['POST'])
def start_account_farming(account_id):
    account = Account.query.get_or_404(account_id)
    duration = float(request.form.get('duration', 1))
    farming_mode = (request.form.get('farming_mode') or 'balanced').lower()
    active_session = FarmSession.query.filter(
        FarmSession.account_id == account.id,
        FarmSession.status.in_(['queued', 'running', 'stopping']),
    ).first()
    if active_session:
        return redirect(url_for('web.account_details', account_id=account.id))

    session = FarmSession(
        account_id=account.id,
        farming_mode=farming_mode,
        duration_hours=duration,
        status='queued',
    )
    account.is_farming = True
    account.farming_status = 'queued'
    account.farming_mode = farming_mode
    account.total_sessions += 1
    db.session.add(session)
    db.session.add(Log(account_id=account.id, message=f'Started farming from dashboard ({farming_mode})', level='INFO'))
    db.session.commit()
    launch_farming_task(account.id, duration, farming_mode, session.id)
    return redirect(url_for('web.account_details', account_id=account.id))


@web_bp.route('/account/<int:account_id>/stop-farming', methods=['POST'])
def stop_account_farming(account_id):
    account = Account.query.get_or_404(account_id)
    session = FarmSession.query.filter(
        FarmSession.account_id == account.id,
        FarmSession.status.in_(['queued', 'running', 'stopping']),
    ).order_by(FarmSession.start_time.desc()).first()
    if session:
        session.stop_requested = True
        session.status = 'stopping'
        account.farming_status = 'stopping'
        db.session.add(Log(account_id=account.id, message='Stop requested from dashboard', level='INFO'))
        db.session.commit()
    return redirect(url_for('web.account_details', account_id=account.id))
