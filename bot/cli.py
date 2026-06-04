"""
CLI for OPTC Farming Bot
Command-line interface for bot management
"""
import click
import asyncio
from bot.account_manager import AccountManager, AccountAuthenticator
from bot.farmer import Farmer, FarmingMode, FarmingStrategy
from bot.api_client import OPTCAPIClient, GameDataManager
from config.settings import OPTC_API_BASE_URL, OPTC_API_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """OPTC Farming Bot CLI"""
    pass

@cli.command()
@click.option('--username', prompt='Username', help='Account username')
@click.option('--password', prompt='Password', hide_input=True, help='Account password')
@click.option('--email', prompt='Email', help='Account email')
def create_account(username, password, email):
    """Create a new account"""
    try:
        account_manager = AccountManager(None)
        account = account_manager.create_account(username, email, password)
        click.echo(f"✓ Account created successfully!")
        click.echo(f"Account ID: {account['id']}")
        click.echo(f"Username: {account['username']}")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)

@cli.command()
@click.option('--account-id', prompt='Account ID', help='Account ID to farm on')
@click.option('--mode', default='all', help='Farming mode (story/events/missions/grinding/all)')
@click.option('--strategy', default='moderate', help='Farming strategy (aggressive/moderate/conservative)')
@click.option('--duration', default=3600, type=int, help='Duration in seconds')
def start_farming(account_id, mode, strategy, duration):
    """Start farming on an account"""
    try:
        # TODO: Implement actual farming logic
        click.echo(f"✓ Farming started")
        click.echo(f"Account: {account_id}")
        click.echo(f"Mode: {mode}")
        click.echo(f"Strategy: {strategy}")
        click.echo(f"Duration: {duration}s")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)

@cli.command()
@click.option('--account-id', prompt='Account ID', help='Account ID')
def get_account(account_id):
    """Get account information"""
    try:
        account_manager = AccountManager(None)
        account = account_manager.get_account(account_id)
        
        if not account:
            click.echo(f"✗ Account not found")
            return
        
        click.echo(f"Account ID: {account['id']}")
        click.echo(f"Username: {account['username']}")
        click.echo(f"Level: {account['level']}")
        click.echo(f"Berry: {account['berry']}")
        click.echo(f"Gold: {account['gold']}")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)

@cli.command()
def list_accounts():
    """List all accounts"""
    try:
        account_manager = AccountManager(None)
        accounts = account_manager.list_accounts()
        
        if not accounts:
            click.echo("No accounts found")
            return
        
        click.echo(f"\n{'ID':<40} {'Username':<20} {'Level':<10} {'Status':<10}")
        click.echo("-" * 80)
        
        for account in accounts:
            click.echo(f"{account['id']:<40} {account['username']:<20} {account['level']:<10} {account['status']:<10}")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)

@cli.command()
@click.option('--account-id', prompt='Account ID', help='Account ID to delete')
@click.confirmation_option(prompt='Are you sure you want to delete this account?')
def delete_account(account_id):
    """Delete an account"""
    try:
        account_manager = AccountManager(None)
        if account_manager.delete_account(account_id):
            click.echo(f"✓ Account deleted successfully")
        else:
            click.echo(f"✗ Account not found")
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli()
