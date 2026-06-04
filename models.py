from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.String(255), nullable=True)
    optc_id = db.Column(db.String(255), nullable=True)
    
    # Farming stats
    is_farming = db.Column(db.Boolean, default=False)
    farming_mode = db.Column(db.String(50), nullable=True)  # story, events, daily, training
    total_sessions = db.Column(db.Integer, default=0)
    total_items_farmed = db.Column(db.Integer, default=0)
    total_exp_gained = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_farmed = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'device_id': self.device_id,
            'optc_id': self.optc_id,
            'is_farming': self.is_farming,
            'farming_mode': self.farming_mode,
            'total_sessions': self.total_sessions,
            'total_items_farmed': self.total_items_farmed,
            'total_exp_gained': self.total_exp_gained,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_farmed': self.last_farmed.strftime('%Y-%m-%d %H:%M:%S') if self.last_farmed else 'Never'
        }


class FarmSession(db.Model):
    __tablename__ = 'farm_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    farming_mode = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    items_collected = db.Column(db.Integer, default=0)
    exp_gained = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='running')  # running, completed, failed
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'farming_mode': self.farming_mode,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'items_collected': self.items_collected,
            'exp_gained': self.exp_gained,
            'status': self.status
        }


class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR, SUCCESS
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'message': self.message,
            'level': self.level,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
