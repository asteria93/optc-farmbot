"""
Celery tasks for OPTC Farming Bot
Background tasks for farming, gift acceptance, and card management
"""
import logging
import time
from datetime import datetime
from celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(bind=True, name='tasks.farm_account')
def farm_account(self, account_id, duration=3600, mode='all'):
    """
    Main farming task for an account.

    Args:
        account_id: The account identifier
        duration: Farming duration in seconds (default 1 hour)
        mode: Farming mode - 'all', 'story', 'events', 'missions'
    """
    logger.info(f'Starting farming for account {account_id}, mode={mode}, duration={duration}s')

    start_time = time.time()
    items_collected = 0
    runs_completed = 0

    self.update_state(state='STARTED', meta={
        'account_id': account_id,
        'mode': mode,
        'start_time': datetime.utcnow().isoformat(),
        'items_collected': items_collected,
        'runs_completed': runs_completed,
    })

    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            remaining = duration - elapsed

            if mode in ('all', 'story'):
                result = _farm_story(account_id)
                items_collected += result.get('items', 0)
                runs_completed += 1

            if mode in ('all', 'events'):
                result = _farm_events(account_id)
                items_collected += result.get('items', 0)
                runs_completed += 1

            if mode in ('all', 'missions'):
                result = _complete_missions(account_id)
                items_collected += result.get('items', 0)
                runs_completed += 1

            self.update_state(state='PROGRESS', meta={
                'account_id': account_id,
                'mode': mode,
                'elapsed': elapsed,
                'remaining': remaining,
                'items_collected': items_collected,
                'runs_completed': runs_completed,
            })

            # Accept gifts periodically
            accept_gifts.delay(account_id)

            # Sell excess cards periodically
            if runs_completed % 5 == 0:
                sell_cards.delay(account_id)

            time.sleep(30)

    except Exception as exc:
        logger.error(f'Farming error for account {account_id}: {exc}')
        raise self.retry(exc=exc, countdown=60, max_retries=3)

    result = {
        'account_id': account_id,
        'mode': mode,
        'duration': duration,
        'items_collected': items_collected,
        'runs_completed': runs_completed,
        'end_time': datetime.utcnow().isoformat(),
    }
    logger.info(f'Farming completed for account {account_id}: {result}')
    return result


@celery.task(name='tasks.accept_gifts')
def accept_gifts(account_id):
    """
    Accept all pending gifts for an account.

    Args:
        account_id: The account identifier
    """
    logger.info(f'Accepting gifts for account {account_id}')
    gifts_accepted = 0

    try:
        # Simulate gift acceptance logic
        gifts_accepted = _accept_all_gifts(account_id)
        logger.info(f'Accepted {gifts_accepted} gifts for account {account_id}')
    except Exception as exc:
        logger.error(f'Error accepting gifts for account {account_id}: {exc}')
        raise

    return {'account_id': account_id, 'gifts_accepted': gifts_accepted}


@celery.task(name='tasks.sell_cards')
def sell_cards(account_id, rarity_threshold=3):
    """
    Sell low-rarity cards for an account.

    Args:
        account_id: The account identifier
        rarity_threshold: Cards with rarity below this value will be sold
    """
    logger.info(f'Selling cards for account {account_id} (rarity < {rarity_threshold})')
    cards_sold = 0

    try:
        cards_sold = _sell_low_rarity_cards(account_id, rarity_threshold)
        logger.info(f'Sold {cards_sold} cards for account {account_id}')
    except Exception as exc:
        logger.error(f'Error selling cards for account {account_id}: {exc}')
        raise

    return {'account_id': account_id, 'cards_sold': cards_sold}


@celery.task(name='tasks.complete_daily_missions')
def complete_daily_missions(account_id):
    """
    Complete daily missions for an account.

    Args:
        account_id: The account identifier
    """
    logger.info(f'Completing daily missions for account {account_id}')

    try:
        result = _complete_missions(account_id, mission_type='daily')
        return {'account_id': account_id, 'missions_completed': result.get('count', 0)}
    except Exception as exc:
        logger.error(f'Error completing missions for account {account_id}: {exc}')
        raise


@celery.task(name='tasks.refill_stamina')
def refill_stamina(account_id):
    """
    Refill stamina for an account using in-game items.

    Args:
        account_id: The account identifier
    """
    logger.info(f'Refilling stamina for account {account_id}')

    try:
        success = _use_stamina_item(account_id)
        return {'account_id': account_id, 'stamina_refilled': success}
    except Exception as exc:
        logger.error(f'Error refilling stamina for account {account_id}: {exc}')
        raise


# ============ Internal helper functions ============

def _farm_story(account_id):
    """Simulate farming a story chapter."""
    logger.debug(f'Farming story for account {account_id}')
    return {'items': 10, 'exp': 50}


def _farm_events(account_id):
    """Simulate farming an event stage."""
    logger.debug(f'Farming events for account {account_id}')
    return {'items': 20, 'exp': 100}


def _complete_missions(account_id, mission_type='all'):
    """Simulate completing missions."""
    logger.debug(f'Completing {mission_type} missions for account {account_id}')
    return {'count': 3, 'items': 15}


def _accept_all_gifts(account_id):
    """Simulate accepting all pending gifts."""
    logger.debug(f'Accepting all gifts for account {account_id}')
    return 5


def _sell_low_rarity_cards(account_id, rarity_threshold):
    """Simulate selling low-rarity cards."""
    logger.debug(f'Selling cards (rarity < {rarity_threshold}) for account {account_id}')
    return 12


def _use_stamina_item(account_id):
    """Simulate using a stamina item."""
    logger.debug(f'Using stamina item for account {account_id}')
    return True
