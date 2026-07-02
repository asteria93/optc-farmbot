import logging
import time
from datetime import datetime, timedelta, timezone
from threading import Thread

from flask import current_app

from bot.account_manager import AccountAuthenticator
from bot.farmer import Farmer, FarmingMode, FarmingStrategy
from celery_app import celery
from models import Account, FarmSession, FarmingConfig, Log, db

logger = logging.getLogger(__name__)

_BACKGROUND_THREADS = {}


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _log(account_id, message, level='INFO', session=None):
    entry = Log(account_id=account_id, message=message, level=level)
    db.session.add(entry)
    if session is not None:
        session.last_message = message
    db.session.commit()
    return entry


def _get_or_create_config(account):
    if account.farming_config:
        return account.farming_config

    config = FarmingConfig(
        account=account,
        farming_content=['gifts', 'story', 'events', 'missions', 'auto_sell'],
    )
    db.session.add(config)
    db.session.commit()
    return config


def _check_for_stop(session):
    db.session.refresh(session)
    return session.stop_requested


def _apply_rewards(account, session, rewards):
    berries = rewards.get('berries', 0)
    gold = rewards.get('gold', 0)
    experience = rewards.get('experience', 0)
    items = max(1, berries // 50) if any(rewards.values()) else 0

    account.total_berry += berries
    account.total_gold += gold
    account.total_exp_gained += experience
    account.total_items_farmed += items
    account.last_farmed = _now()

    session.items_collected += items
    session.exp_gained += experience
    db.session.commit()
    return {'items': items, 'experience': experience}


def _build_farmer(account):
    account_data = {
        'id': str(account.id),
        'username': account.username,
        'level': 1,
        'berry': account.total_berry,
        'gold': account.total_gold,
        'experience': account.total_exp_gained,
        'farming_stats': {
            'story_chapters': 0,
            'events_completed': 0,
            'missions_completed': 0,
            'total_runs': 0,
        },
    }
    return Farmer(str(account.id), account_data)


def accept_gifts_impl(account_id, session_id=None):
    account = db.session.get(Account, account_id)
    session = db.session.get(FarmSession, session_id) if session_id else None
    _log(account.id, 'Accepting gifts from mailbox')
    session and db.session.refresh(session)
    reward = {'berries': 40, 'gold': 15, 'experience': 10}
    return _apply_rewards(account, session, reward)


def auto_sell_cards_impl(account_id, session_id=None):
    account = db.session.get(Account, account_id)
    session = db.session.get(FarmSession, session_id) if session_id else None
    _log(account.id, 'Auto-selling low rarity cards', 'SUCCESS')
    reward = {'berries': 15, 'gold': 25, 'experience': 0}
    return _apply_rewards(account, session, reward)


def farm_story_mode_impl(account_id, session_id=None):
    account = db.session.get(Account, account_id)
    session = db.session.get(FarmSession, session_id) if session_id else None
    farmer = _build_farmer(account)
    rewards = farmer.farm_story(1)
    _log(account.id, 'Completed unfinished story quest', 'SUCCESS')
    return _apply_rewards(account, session, rewards)


def farm_events_impl(account_id, session_id=None):
    account = db.session.get(Account, account_id)
    session = db.session.get(FarmSession, session_id) if session_id else None
    farmer = _build_farmer(account)
    rewards = farmer.farm_event('daily-event')
    _log(account.id, 'Farmed available daily/weekly event', 'SUCCESS')
    return _apply_rewards(account, session, rewards)


def farm_missions_impl(account_id, session_id=None):
    account = db.session.get(Account, account_id)
    session = db.session.get(FarmSession, session_id) if session_id else None
    farmer = _build_farmer(account)
    rewards = farmer.farm_mission('mission-board')
    _log(account.id, 'Completed available missions', 'SUCCESS')
    return _apply_rewards(account, session, rewards)


def _authenticate_account(account):
    authenticator = AccountAuthenticator()
    for attempt in range(1, 4):
        token = authenticator.authenticate(account.username, account.password)
        if token:
            _log(account.id, f'Login successful on attempt {attempt}', 'SUCCESS')
            return token
        _log(account.id, f'Login failed on attempt {attempt}', 'ERROR')
    raise RuntimeError('Unable to authenticate account')


def _update_running_state(account, session, status):
    account.is_farming = status in {'queued', 'running', 'stopping'}
    account.farming_status = status
    account.farming_mode = session.farming_mode if session else account.farming_mode
    session.status = status
    db.session.commit()


def _finalize_session(account, session, status, message=None):
    session.status = status
    session.end_time = _now()
    session.last_message = message or session.last_message
    account.is_farming = False
    account.farming_status = 'idle' if status in {'completed', 'stopped'} else 'error'
    if status == 'failed':
        account.last_error = message
    db.session.commit()


def _run_farming_loop(account_id, duration, farming_mode='balanced', session_id=None):
    account = db.session.get(Account, account_id)
    session = db.session.get(FarmSession, session_id) if session_id else None
    if not account or not session:
        return {'status': 'missing'}

    config = _get_or_create_config(account)
    try:
        _update_running_state(account, session, 'running')
        _authenticate_account(account)
        _log(account.id, 'Farming loop started')

        try:
            duration = max(float(duration or 0), 0)
        except (TypeError, ValueError) as exc:
            raise ValueError('duration must be a valid number') from exc
        end_time = _now() + timedelta(hours=duration)
        cycle_count = 0

        while True:
            if _check_for_stop(session):
                _log(account.id, 'Stop requested, shutting down farming loop')
                _finalize_session(account, session, 'stopped', 'Stopped by user')
                return session.to_dict()

            if cycle_count > 0 and duration == 0:
                break

            if duration > 0 and _now() >= end_time:
                break

            _log(account.id, 'Checking stamina and refill strategy')
            if config.refill_strategy != 'skip':
                _log(account.id, f'Using refill strategy: {config.refill_strategy}')

            contents = set(config.farming_content or [])
            if not contents:
                contents = {'gifts', 'story', 'events', 'missions', 'auto_sell'}

            if 'gifts' in contents:
                accept_gifts_impl(account.id, session.id)
            if 'story' in contents and farming_mode in {'story', 'all', 'balanced'}:
                farm_story_mode_impl(account.id, session.id)
            if 'events' in contents and farming_mode in {'events', 'all', 'balanced'}:
                farm_events_impl(account.id, session.id)
            if 'missions' in contents and farming_mode in {'missions', 'all', 'balanced'}:
                farm_missions_impl(account.id, session.id)
            if config.auto_sell and 'auto_sell' in contents:
                auto_sell_cards_impl(account.id, session.id)

            cycle_count += 1
            session.last_message = f'Completed farming cycle {cycle_count}'
            db.session.commit()
            if duration > 0:
                sleep_seconds = max(float(current_app.config.get('FARMING_LOOP_SLEEP_SECONDS', 0)), 0)
                if sleep_seconds:
                    time.sleep(sleep_seconds)

        _log(account.id, f'Farming loop completed after {cycle_count} cycle(s)', 'SUCCESS')
        _finalize_session(account, session, 'completed', 'Farming finished')
        return session.to_dict()
    except Exception as exc:
        logger.exception('Farming loop failed for account %s', account_id)
        _log(account.id, f'Farming loop failed: {exc}', 'ERROR')
        _finalize_session(account, session, 'failed', str(exc))
        raise


if celery:
    @celery.task(name='tasks.farm_story_mode')
    def farm_story_mode(account_id, session_id=None):
        return farm_story_mode_impl(account_id, session_id)

    @celery.task(name='tasks.farm_events')
    def farm_events(account_id, session_id=None):
        return farm_events_impl(account_id, session_id)

    @celery.task(name='tasks.farm_missions')
    def farm_missions(account_id, session_id=None):
        return farm_missions_impl(account_id, session_id)

    @celery.task(name='tasks.auto_sell_cards')
    def auto_sell_cards(account_id, session_id=None):
        return auto_sell_cards_impl(account_id, session_id)

    @celery.task(name='tasks.accept_gifts')
    def accept_gifts(account_id, session_id=None):
        return accept_gifts_impl(account_id, session_id)

    @celery.task(name='tasks.farming_loop')
    def farming_loop(account_id, duration, farming_mode='balanced', session_id=None):
        return _run_farming_loop(account_id, duration, farming_mode, session_id)
else:  # pragma: no cover - exercised when Celery is unavailable
    def farm_story_mode(account_id, session_id=None):
        return farm_story_mode_impl(account_id, session_id)

    def farm_events(account_id, session_id=None):
        return farm_events_impl(account_id, session_id)

    def farm_missions(account_id, session_id=None):
        return farm_missions_impl(account_id, session_id)

    def auto_sell_cards(account_id, session_id=None):
        return auto_sell_cards_impl(account_id, session_id)

    def accept_gifts(account_id, session_id=None):
        return accept_gifts_impl(account_id, session_id)

    def farming_loop(account_id, duration, farming_mode='balanced', session_id=None):
        return _run_farming_loop(account_id, duration, farming_mode, session_id)


def _thread_runner(app, account_id, duration, farming_mode, session_id):
    with app.app_context():
        _run_farming_loop(account_id, duration, farming_mode, session_id)


def launch_farming_task(account_id, duration, farming_mode, session_id):
    app = current_app._get_current_object()
    task_mode = app.config.get('FARMING_TASK_MODE', 'thread')

    if task_mode == 'inline':
        try:
            return _run_farming_loop(account_id, duration, farming_mode, session_id)
        except Exception as exc:
            return {'status': 'failed', 'error': str(exc)}

    if task_mode == 'manual':
        return {'status': 'queued'}

    if task_mode == 'celery' and celery:
        result = farming_loop.delay(account_id, duration, farming_mode, session_id=session_id)
        session = db.session.get(FarmSession, session_id)
        session.task_id = result.id
        db.session.commit()
        return {'task_id': result.id, 'status': 'queued'}

    thread = Thread(
        target=_thread_runner,
        args=(app, account_id, duration, farming_mode, session_id),
        daemon=True,
        name=f'farming-account-{account_id}',
    )
    thread.start()
    task_id = f'thread-{session_id}'
    _BACKGROUND_THREADS[task_id] = thread
    session = db.session.get(FarmSession, session_id)
    session.task_id = task_id
    db.session.commit()
    return {'task_id': task_id, 'status': 'queued'}
