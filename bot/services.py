"""
Database-backed service layer for the OPTC farming bot.
"""
import logging
from datetime import datetime

from sqlalchemy import Integer, cast, func
from werkzeug.security import generate_password_hash

from bot.account_manager import AccountManager, AccountAuthenticator
from bot.farmer import Farmer, FarmingMode, FarmingStrategy
from models import db, Account, FarmSession, Log

logger = logging.getLogger(__name__)

DEFAULT_PREFERENCES = {
    'story_mode': True,
    'events': True,
    'missions': True,
    'grinding': True,
    'auto_sell': True,
    'auto_accept_gifts': True,
}


def normalize_preferences(preferences=None):
    merged = DEFAULT_PREFERENCES.copy()
    if preferences:
        normalized = {}
        for key, value in preferences.items():
            if key not in merged:
                continue
            if isinstance(value, str):
                normalized[key] = value.lower() in {'1', 'true', 'yes', 'on'}
            else:
                normalized[key] = bool(value)
        merged.update(normalized)
    return merged


def parse_mode(mode):
    normalized = (mode or FarmingMode.ALL.value).lower()
    for candidate in FarmingMode:
        if candidate.value == normalized:
            return candidate
    raise ValueError('Invalid farming mode')


def parse_strategy(strategy):
    normalized = (strategy or FarmingStrategy.MODERATE.value).lower()
    for candidate in FarmingStrategy:
        if candidate.value == normalized:
            return candidate
    raise ValueError('Invalid farming strategy')


def create_log(message, level='INFO', account_id=None, session_id=None):
    log_entry = Log(
        account_id=account_id,
        session_id=session_id,
        message=message,
        level=level,
    )
    db.session.add(log_entry)
    return log_entry


def create_account_record(username, email, password, preferences=None):
    seeded_account = AccountManager(None).create_account(username, email, password)
    account = Account(
        username=username,
        email=email,
        password=generate_password_hash(password),
        device_id=seeded_account['id'],
        optc_id=seeded_account['id'],
        status=Account.STATUS_ACTIVE,
        preferences=normalize_preferences(preferences),
    )
    db.session.add(account)
    db.session.flush()
    create_log(
        f'Account {username} registered and ready for automation.',
        level='SUCCESS',
        account_id=account.id,
    )
    db.session.commit()
    return account


def build_account_payload(account):
    return {
        'id': account.id,
        'username': account.username,
        'level': max(1, int(account.total_exp_gained / 1000) + 1),
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


def create_farm_session(account, mode, strategy):
    session = FarmSession(
        account_id=account.id,
        farming_mode=parse_mode(mode).value,
        strategy=parse_strategy(strategy).value,
        status=FarmSession.STATUS_QUEUED,
    )
    account.is_farming = True
    account.farming_mode = session.farming_mode
    db.session.add(session)
    db.session.flush()
    create_log(
        f'Queued farming session in {session.farming_mode} mode.',
        account_id=account.id,
        session_id=session.id,
    )
    db.session.commit()
    return session


def stop_farm_session(session):
    session.status = FarmSession.STATUS_STOPPED
    session.end_time = datetime.utcnow()
    session.account.is_farming = False
    create_log(
        'Farming session stopped.',
        level='WARNING',
        account_id=session.account_id,
        session_id=session.id,
    )
    db.session.commit()
    return session


def _mode_operations(mode, farmer, preferences):
    operations = []
    if mode in (FarmingMode.STORY, FarmingMode.ALL) and preferences.get('story_mode', True):
        operations.append(('story', lambda: farmer.farm_story(1), 'Story chapter cleared'))
    if mode in (FarmingMode.EVENTS, FarmingMode.ALL) and preferences.get('events', True):
        operations.append(('event', lambda: farmer.farm_event('current-event'), 'Event cleared'))
    if mode in (FarmingMode.MISSIONS, FarmingMode.ALL) and preferences.get('missions', True):
        operations.append(('mission', lambda: farmer.farm_mission('daily-mission'), 'Mission completed'))
    if mode in (FarmingMode.GRINDING, FarmingMode.ALL) and preferences.get('grinding', True):
        operations.append(('grinding', lambda: farmer.farm_grinding('resource-island'), 'Grinding run completed'))
    return operations


def execute_farm_session(session_id):
    session = db.session.get(FarmSession, session_id)
    if session is None:
        raise ValueError(f'Farming session {session_id} not found')

    account = session.account
    if session.status in {FarmSession.STATUS_COMPLETED, FarmSession.STATUS_FAILED, FarmSession.STATUS_STOPPED}:
        return session.to_dict()

    session.status = FarmSession.STATUS_RUNNING
    db.session.commit()

    try:
        authenticator = AccountAuthenticator()
        token = authenticator.authenticate(account.username, account.optc_id or str(account.id))
        create_log(
            f'Authenticated account session token {token[:8]}...',
            account_id=account.id,
            session_id=session.id,
        )

        farmer = Farmer(str(account.id), build_account_payload(account))
        farming_mode = parse_mode(session.farming_mode)
        farming_strategy = parse_strategy(session.strategy)
        farmer.start_farming(farming_mode, farming_strategy)

        preferences = normalize_preferences(account.preferences)
        total_rewards = {'berries': 0, 'gold': 0, 'experience': 0}
        operations = _mode_operations(farming_mode, farmer, preferences)

        if not operations:
            raise ValueError('No automation targets are enabled for this account')

        for _, operation, message in operations:
            rewards = operation()
            total_rewards['berries'] += rewards.get('berries', 0)
            total_rewards['gold'] += rewards.get('gold', 0)
            total_rewards['experience'] += rewards.get('experience', 0)
            create_log(
                f'{message}: +{rewards.get("berries", 0)} berries, +{rewards.get("gold", 0)} gold, +{rewards.get("experience", 0)} exp.',
                level='SUCCESS',
                account_id=account.id,
                session_id=session.id,
            )

        items_collected = len(farmer.farming_history)
        if preferences.get('auto_accept_gifts', True):
            total_rewards['berries'] += 25
            create_log(
                'Accepted daily gifts and added 25 berries.',
                level='SUCCESS',
                account_id=account.id,
                session_id=session.id,
            )

        if preferences.get('auto_sell', True):
            auto_sell_gold = items_collected * 10
            total_rewards['gold'] += auto_sell_gold
            create_log(
                f'Auto-sold low-rarity drops for {auto_sell_gold} gold.',
                level='SUCCESS',
                account_id=account.id,
                session_id=session.id,
            )

        account.total_berry += total_rewards['berries']
        account.total_gold += total_rewards['gold']
        account.total_exp_gained += total_rewards['experience']
        account.total_items_farmed += items_collected
        account.total_sessions += 1
        account.last_farmed = datetime.utcnow()
        account.is_farming = False

        session.total_runs = items_collected
        session.items_collected = items_collected
        session.exp_gained = total_rewards['experience']
        session.end_time = datetime.utcnow()
        session.status = FarmSession.STATUS_COMPLETED
        session.last_error = None

        create_log(
            'Farming session completed successfully.',
            level='SUCCESS',
            account_id=account.id,
            session_id=session.id,
        )
        db.session.commit()
    except Exception as exc:
        logger.exception('Farming session failed')
        safe_error = 'Automation run failed. Check worker logs for details.'
        session.status = FarmSession.STATUS_FAILED
        session.last_error = safe_error
        session.end_time = datetime.utcnow()
        account.is_farming = False
        create_log(
            safe_error,
            level='ERROR',
            account_id=account.id,
            session_id=session.id,
        )
        db.session.commit()
    return session.to_dict()


def account_statistics():
    total_accounts = db.session.query(func.count(Account.id)).scalar() or 0
    active_accounts = db.session.query(func.count(Account.id)).filter_by(status=Account.STATUS_ACTIVE).scalar() or 0
    total_level = (
        db.session.query(func.sum(cast(Account.total_exp_gained / 1000, Integer) + 1)).scalar() or 0
    )
    total_rewards = (db.session.query(func.sum(Account.total_berry + Account.total_gold)).scalar() or 0)
    return {
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'average_level': total_level / total_accounts if total_accounts else 0,
        'total_rewards_earned': total_rewards,
    }


def farming_statistics():
    total_sessions = db.session.query(func.count(FarmSession.id)).scalar() or 0
    active_sessions = (
        db.session.query(func.count(FarmSession.id))
        .filter(FarmSession.status.in_([FarmSession.STATUS_QUEUED, FarmSession.STATUS_RUNNING]))
        .scalar()
        or 0
    )
    total_runs = db.session.query(func.sum(FarmSession.total_runs)).scalar() or 0
    return {
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
        'total_runs': total_runs,
    }
