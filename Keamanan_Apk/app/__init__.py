import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from cryptography.fernet import Fernet
<<<<<<< HEAD
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
=======

# Inisialisasi db dan login_manager secara global di sini
# Ini harus didefinisikan sebelum diimpor oleh modul lain
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
                instance_relative_config=True, 
                static_folder='../static', 
                template_folder='../templates')
    
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FERNET_KEY'] = b't7tqK5Ba9xS6eQHgN6GLpF94cYlgdAKxY-tAVmO14y0='
    app.config['CIPHER_SUITE'] = Fernet(app.config['FERNET_KEY'])
>>>>>>> Develop

    # Konfigurasi kunci enkripsi Fernet
    app.config['FERNET_KEY'] = b't7tqK5Ba9xS6eQHgN6GLpF94cYlgdAKxY-tAVmO14y0='
    app.config['CIPHER_SUITE'] = Fernet(app.config['FERNET_KEY'])

    # Inisialisasi ekstensi dengan aplikasi
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login_register'
    
<<<<<<< HEAD
    # User loader untuk Flask-Login
=======
    # Import model User di sini, SETELAH db diinisialisasi dengan app
    # Ini penting untuk user_loader
    from .models import User 

>>>>>>> Develop
    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))

<<<<<<< HEAD
    # Daftarkan Blueprint di sini
=======
    # Import Blueprint di sini (Blueprint juga akan mengimpor model)
    from .routes import main_bp
>>>>>>> Develop
    app.register_blueprint(main_bp)

    return app

<<<<<<< HEAD
# Fungsi untuk membuat tabel (dipanggil dari run.py)
=======
>>>>>>> Develop
def create_tables_and_admin(app):
    with app.app_context():
        # Import User di dalam fungsi ini juga agar tersedia di lingkup ini
        from .models import User 
        db.create_all()
<<<<<<< HEAD
        # Membuat user admin default jika belum ada
=======
>>>>>>> Develop
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('adminpassword') 
            db.session.add(admin_user)
            db.session.commit()
<<<<<<< HEAD
            print("Default admin user created: username='admin', password='adminpassword'")
=======
            print("Default admin user created: username='admin', password='adminpassword'")

>>>>>>> Develop
