from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    events = db.relationship('Event', backref='creator', lazy=True)
    photos = db.relationship('Photo', backref='uploader', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    unique_code = db.Column(db.String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])
    qr_code_path = db.Column(db.String(200))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photos = db.relationship('Photo', backref='event', lazy=True)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable para permitir uploads anônimos

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
