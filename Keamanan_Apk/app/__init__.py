# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from bcrypt import hashpw, gensalt # Tetap di sini untuk generate password admin
from cryptography.fernet import Fernet # Tetap di sini untuk inisialisasi cipher_suite
from config import Config # Import konfigurasi kita
import os
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
cipher_suite = None # Akan diinisialisasi di create_app

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login' # Endpoint login kita sekarang

    # Inisialisasi cipher_suite setelah app config diload
    global cipher_suite
    cipher_suite = Fernet(app.config['FERNET_KEY'])

    # Import dan register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # User Loader untuk Flask-Login
    from app.models import User # Import model User dari models.py
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Fungsi untuk membuat tabel database dan user admin default
    with app.app_context():
        db.create_all()
        # Buat user admin default jika belum ada
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('adminpassword') # GANTI PASSWORD INI DI LINGKUNGAN PRODUKSI!
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='admin', password='adminpassword'")

    return app