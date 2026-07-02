from datetime import datetime, timezone
import uuid

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.String(64), nullable=False, default=lambda: uuid.uuid4().hex)
    platform = db.Column(db.String(20), nullable=False, default='android')
    version = db.Column(db.String(20), nullable=False, default='gb')
    optc_id = db.Column(db.String(255), nullable=True)

    is_farming = db.Column(db.Boolean, default=False, nullable=False)
    farming_status = db.Column(db.String(20), default='idle', nullable=False)
    farming_mode = db.Column(db.String(50), nullable=True)
    total_sessions = db.Column(db.Integer, default=0, nullable=False)
    total_items_farmed = db.Column(db.Integer, default=0, nullable=False)
    total_exp_gained = db.Column(db.Integer, default=0, nullable=False)
    total_berry = db.Column(db.Integer, default=0, nullable=False)
    total_gold = db.Column(db.Integer, default=0, nullable=False)
    last_error = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)
    last_farmed = db.Column(db.DateTime, nullable=True)

    farming_config = db.relationship(
        'FarmingConfig',
        back_populates='account',
        uselist=False,
        cascade='all, delete-orphan',
    )
    sessions = db.relationship(
        'FarmSession',
        back_populates='account',
        cascade='all, delete-orphan',
        order_by='desc(FarmSession.start_time)',
    )
    logs = db.relationship(
        'Log',
        back_populates='account',
        cascade='all, delete-orphan',
        order_by='desc(Log.timestamp)',
    )

    def to_dict(self, include_sensitive=False):
        payload = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'device_id': self.device_id,
            'platform': self.platform,
            'version': self.version,
            'optc_id': self.optc_id,
            'is_farming': self.is_farming,
            'farming_status': self.farming_status,
            'farming_mode': self.farming_mode,
            'total_sessions': self.total_sessions,
            'total_items_farmed': self.total_items_farmed,
            'total_exp_gained': self.total_exp_gained,
            'total_berry': self.total_berry,
            'total_gold': self.total_gold,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_farmed': self.last_farmed.isoformat() if self.last_farmed else None,
        }
        if self.farming_config:
            payload['farming_config'] = self.farming_config.to_dict()
        if include_sensitive:
            payload['password'] = self.password
        return payload


class FarmSession(db.Model):
    __tablename__ = 'farm_sessions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
    task_id = db.Column(db.String(120), nullable=True)
    farming_mode = db.Column(db.String(50), nullable=False)
    duration_hours = db.Column(db.Float, default=0, nullable=False)
    start_time = db.Column(db.DateTime, default=_utcnow, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    items_collected = db.Column(db.Integer, default=0, nullable=False)
    exp_gained = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(50), default='queued', nullable=False)
    stop_requested = db.Column(db.Boolean, default=False, nullable=False)
    last_message = db.Column(db.Text, nullable=True)

    account = db.relationship('Account', back_populates='sessions')

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'task_id': self.task_id,
            'farming_mode': self.farming_mode,
            'duration_hours': self.duration_hours,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'items_collected': self.items_collected,
            'exp_gained': self.exp_gained,
            'status': self.status,
            'stop_requested': self.stop_requested,
            'last_message': self.last_message,
        }


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True, index=True)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default='INFO', nullable=False)
    timestamp = db.Column(db.DateTime, default=_utcnow, nullable=False)

    account = db.relationship('Account', back_populates='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'message': self.message,
            'level': self.level,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class FarmingConfig(db.Model):
    __tablename__ = 'farming_configs'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, unique=True)
    auto_sell = db.Column(db.Boolean, default=True, nullable=False)
    refill_strategy = db.Column(db.String(50), default='skip', nullable=False)
    farming_content = db.Column(db.JSON, default=list, nullable=False)

    account = db.relationship('Account', back_populates='farming_config')

    def to_dict(self):
        return {
            'auto_sell': self.auto_sell,
            'refill_strategy': self.refill_strategy,
            'farming_content': list(self.farming_content or []),
        }
