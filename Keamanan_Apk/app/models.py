# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from bcrypt import hashpw, gensalt, checkpw
from cryptography.fernet import Fernet
from flask import current_app

# db tidak diinisialisasi di sini, akan diinisialisasi di __init__.py
db = SQLAlchemy()

# --- MODEL DATABASE (Definisi Tabel) ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owned_todo_lists = db.relationship('ToDoList', backref='owner', lazy=True)
    memberships = db.relationship('ToDoListMember', backref='member', lazy=True)
    created_tasks = db.relationship('Task', backref='creator', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='actor', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

    def set_password(self, password_text):
        self.password = hashpw(password_text.encode('utf-8'), gensalt()).decode('utf-8')

    def check_password(self, password_text):
        return checkpw(password_text.encode('utf-8'), self.password.encode('utf-8'))

class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship('Task', backref='todo_list', lazy=True, cascade="all, delete-orphan")
    members = db.relationship('ToDoListMember', backref='todo_list', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"ToDoList('{self.name}', Owner:{self.owner_id})"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description_encrypted = db.Column(db.LargeBinary, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Task('{self.title}', Status:'{self.status}')"

    def set_description(self, description_text):
        cipher_suite = current_app.config.get('CIPHER_SUITE')
        if not cipher_suite:
            raise RuntimeError("Fernet cipher_suite not configured. Please set app.config['CIPHER_SUITE'].")
        self.description_encrypted = cipher_suite.encrypt(description_text.encode('utf-8'))

    def get_description(self):
        cipher_suite = current_app.config.get('CIPHER_SUITE')
        if not cipher_suite:
            raise RuntimeError("Fernet cipher_suite not configured. Please set app.config['CIPHER_SUITE'].")
        return cipher_suite.decrypt(self.description_encrypted).decode('utf-8')

class ToDoListMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False, default='read')

    __table_args__ = (db.UniqueConstraint('todo_list_id', 'user_id', name='_todo_list_member_uc'),)

    def __repr__(self):
        return f"ToDoListMember(User:{self.user_id} -> ToDoList:{self.todo_list_id}, Perm:'{self.permission_level}')"

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ActivityLog(User:{self.user_id}, Action:'{self.action}', Time:'{self.timestamp}')"