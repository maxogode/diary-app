from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    entries = db.relationship('Entry', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    creation_time = db.Column(db.DateTime, default=datetime.now(timezone(timedelta(hours=4))))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
