"""
Configuration settings for OPTC Farming Bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')

# Database
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/optc_farmbot')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///optc_farmbot.db')

# Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Bot Settings
BOT_MAX_ACCOUNTS = int(os.getenv('BOT_MAX_ACCOUNTS', 10))
BOT_FARMING_INTERVAL = int(os.getenv('BOT_FARMING_INTERVAL', 300))
BOT_CHECK_INTERVAL = int(os.getenv('BOT_CHECK_INTERVAL', 60))

# API Settings
OPTC_API_BASE_URL = os.getenv('OPTC_API_BASE_URL', 'https://api.optc.example.com')
OPTC_API_KEY = os.getenv('OPTC_API_KEY', '')

# Web Server
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/optc_farmbot.log')

# Security
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000').split(',')

# Account Creation
AUTO_CREATE_ACCOUNTS = os.getenv('AUTO_CREATE_ACCOUNTS', 'False').lower() == 'true'
ACCOUNT_CREATION_INTERVAL = int(os.getenv('ACCOUNT_CREATION_INTERVAL', 3600))

# Farming Priorities
PRIORITY_EVENTS = os.getenv('PRIORITY_EVENTS', 'True').lower() == 'true'
PRIORITY_STORY = os.getenv('PRIORITY_STORY', 'True').lower() == 'true'
PRIORITY_MISSIONS = os.getenv('PRIORITY_MISSIONS', 'True').lower() == 'true'
PRIORITY_GRINDING = os.getenv('PRIORITY_GRINDING', 'False').lower() == 'true'

# Farming Strategies
FARMING_STRATEGIES = {
    'aggressive': {
        'description': 'Maximum farming intensity',
        'speed': 'fast',
        'break_interval': 1800,  # 30 minutes
    },
    'moderate': {
        'description': 'Balanced farming',
        'speed': 'normal',
        'break_interval': 3600,  # 1 hour
    },
    'conservative': {
        'description': 'Slow and steady farming',
        'speed': 'slow',
        'break_interval': 5400,  # 90 minutes
    },
}

# Game Modes
GAME_MODES = {
    'story': {'priority': 1, 'enabled': PRIORITY_STORY},
    'events': {'priority': 2, 'enabled': PRIORITY_EVENTS},
    'missions': {'priority': 3, 'enabled': PRIORITY_MISSIONS},
    'grinding': {'priority': 4, 'enabled': PRIORITY_GRINDING},
}
