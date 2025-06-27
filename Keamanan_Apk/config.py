# config.py
import os

class Config:
    # Kunci Rahasia untuk Flask (GANTI INI DENGAN KUNCI KUAT & UNIK!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_here_for_flask_session_default_kuat'

    # Konfigurasi Database SQLite
    # app.root_path akan merujuk ke direktori 'app'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/site.db' # Lokasi site.db di dalam folder instance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Kunci Enkripsi Fernet (GANTI INI DENGAN KUNCI YANG ANDA DAPATKAN!)
    # Penting: Kunci ini harus sama dengan yang Anda dapatkan dari terminal!
    # Contoh: b't7tqK5Ba9xS6eQHgN6GLpF94cYlgdAKxY-tAVmO14y0='
    FERNET_KEY = os.environ.get('FERNET_KEY') or b'YOUR_GENERATED_FERNET_KEY_HERE_PASTE_IT_FROM_TERMINAL_OUTPUT='