import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from cryptography.fernet import Fernet
from .routes import main_bp
from .models import db, User 

login_manager = LoginManager()

def create_app():
    # Inisialisasi Flask aplikasi
    # Beri tahu Flask di mana folder static berada
    app = Flask(__name__, instance_relative_config=True, static_folder='../static') # <-- Perbaikan di sini!
    
    # Konfigurasi aplikasi
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Konfigurasi kunci enkripsi Fernet
    app.config['FERNET_KEY'] = b't7tqK5Ba9xS6eQHgN6GLpF94cYlgdAKxY-tAVmO14y0='
    app.config['CIPHER_SUITE'] = Fernet(app.config['FERNET_KEY'])

    # Inisialisasi ekstensi dengan aplikasi
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login_register'
    
    # User loader untuk Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))

    # Daftarkan Blueprint di sini
    app.register_blueprint(main_bp)

    return app

# Fungsi untuk membuat tabel (dipanggil dari run.py)
def create_tables_and_admin(app):
    with app.app_context():
        db.create_all()
        # Membuat user admin default jika belum ada
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('adminpassword') 
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='admin', password='adminpassword'")