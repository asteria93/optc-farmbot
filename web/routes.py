"""
Web interface routes
Serves the dashboard and UI pages
"""
from flask import Blueprint, render_template, jsonify
import logging

logger = logging.getLogger(__name__)

web_bp = Blueprint('web', __name__)

@web_bp.route('/', methods=['GET'])
def index():
    """Main dashboard page"""
    return render_template('index.html')

@web_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Farming dashboard"""
    return render_template('dashboard.html')

@web_bp.route('/accounts', methods=['GET'])
def accounts_page():
    """Accounts management page"""
    return render_template('accounts.html')

@web_bp.route('/farming', methods=['GET'])
def farming_page():
    """Farming control page"""
    return render_template('farming.html')

@web_bp.route('/settings', methods=['GET'])
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@web_bp.route('/logs', methods=['GET'])
def logs_page():
    """Logs viewer page"""
    return render_template('logs.html')
