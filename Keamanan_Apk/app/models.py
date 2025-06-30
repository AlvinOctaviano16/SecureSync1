# app/models.py

from app import db 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from cryptography.fernet import Fernet 
from flask import current_app 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False) 
    role = db.Column(db.String(50), default='user') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owned_todo_lists = db.relationship('ToDoList', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    memberships = db.relationship('ToDoListMember', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password_text):
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password, password_text)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='todo_list', lazy='dynamic', cascade="all, delete-orphan")
    members = db.relationship('ToDoListMember', back_populates='todo_list', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ToDoList {self.name}>'

class ToDoListMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(50), default='read') 
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # DIKOREKSI: Mengubah nama relasi dari 'user_obj' menjadi 'user'
    user = db.relationship('User', back_populates='memberships') 
    # DIKOREKSI: Mengubah nama relasi dari 'todo_list_obj' menjadi 'todo_list'
    todo_list = db.relationship('ToDoList', back_populates='members')

    __table_args__ = (db.UniqueConstraint('todo_list_id', 'user_id', name='_todo_list_user_uc'),)

    def __repr__(self):
        return f'<ToDoListMember List:{self.todo_list_id} User:{self.user_id} Perm:{self.permission_level}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo_list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    encrypted_description = db.Column(db.LargeBinary, nullable=True) 
    status = db.Column(db.String(50), default='pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', backref='created_tasks')

    def set_description(self, description_text):
        if description_text:
            cipher_suite = current_app.config['CIPHER_SUITE']
            self.encrypted_description = cipher_suite.encrypt(description_text.encode('utf-8'))
        else:
            self.encrypted_description = None

    def get_description(self):
        if self.encrypted_description:
            cipher_suite = current_app.config['CIPHER_SUITE']
            return cipher_suite.decrypt(self.encrypted_description).decode('utf-8')
        return ""

    def __repr__(self):
        return f'<Task {self.title}>'

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False) 
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activity_logs')

    def __repr__(self):
        return f'<ActivityLog User:{self.user_id} Action:{self.action} Time:{self.timestamp}>'