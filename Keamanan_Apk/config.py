# config.py
import os

class Config:
    # Kunci Rahasia untuk Flask (GANTI INI DENGAN KUNCI KUAT & UNIK!)
    # Gunakan os.environ.get untuk produksi, atau string default untuk development
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci_rahasia_super_unik_dan_panjang_sekali_ini_mesti_diganti_nanti'

    # Konfigurasi Database SQLite
    # basedir akan merujuk ke direktori tempat config.py berada (yaitu root proyek)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Kunci Enkripsi Fernet (GANTI INI DENGAN KUNCI YANG ANDA DAPATKAN!)
    # Ini harus dalam bentuk bytes (diawali 'b')
    # Contoh: b't7tqK5Ba9xS6eQHgN6GLpF94cYlgdAKxY-tAVmO14y0='
    FERNET_KEY = os.environ.get('FERNET_KEY') or b'gAAAAABmXpZ...ANDA_HARUS_GANTI_INI_DENGAN_KEY_ASLI_ANDA='
