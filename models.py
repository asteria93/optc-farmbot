from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    STATUS_ACTIVE = 'active'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.String(255), nullable=True)
    optc_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default=STATUS_ACTIVE, nullable=False)
    preferences = db.Column(db.JSON, default=dict, nullable=False)
    
    # Farming stats
    is_farming = db.Column(db.Boolean, default=False)
    farming_mode = db.Column(db.String(50), nullable=True)  # story, events, daily, training
    total_sessions = db.Column(db.Integer, default=0)
    total_items_farmed = db.Column(db.Integer, default=0)
    total_exp_gained = db.Column(db.Integer, default=0)
    total_berry = db.Column(db.Integer, default=0)
    total_gold = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_farmed = db.Column(db.DateTime, nullable=True)
    
    sessions = db.relationship('FarmSession', backref='account', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('Log', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'device_id': self.device_id,
            'optc_id': self.optc_id,
            'status': self.status,
            'preferences': self.preferences or {},
            'is_farming': self.is_farming,
            'farming_mode': self.farming_mode,
            'total_sessions': self.total_sessions,
            'total_items_farmed': self.total_items_farmed,
            'total_exp_gained': self.total_exp_gained,
            'berry': self.total_berry,
            'gold': self.total_gold,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_farmed': self.last_farmed.strftime('%Y-%m-%d %H:%M:%S') if self.last_farmed else 'Never'
        }


class FarmSession(db.Model):
    __tablename__ = 'farm_sessions'
    STATUS_QUEUED = 'queued'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_STOPPED = 'stopped'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    farming_mode = db.Column(db.String(50), nullable=False)
    strategy = db.Column(db.String(50), default='moderate', nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    items_collected = db.Column(db.Integer, default=0)
    exp_gained = db.Column(db.Integer, default=0)
    total_runs = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default=STATUS_QUEUED)  # queued, running, completed, failed, stopped
    task_id = db.Column(db.String(255), nullable=True)
    last_error = db.Column(db.Text, nullable=True)
    
    logs = db.relationship('Log', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'farming_mode': self.farming_mode,
            'strategy': self.strategy,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'items_collected': self.items_collected,
            'exp_gained': self.exp_gained,
            'total_runs': self.total_runs,
            'status': self.status,
            'task_id': self.task_id,
            'last_error': self.last_error,
        }


class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('farm_sessions.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR, SUCCESS
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'session_id': self.session_id,
            'message': self.message,
            'level': self.level,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
