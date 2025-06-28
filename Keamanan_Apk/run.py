# run.py
import os
from app import create_app, create_tables_and_admin

# Buat instance aplikasi Flask
app = create_app()

# Panggil fungsi untuk membuat tabel dan user admin
# Ini akan membuat file database site.db jika belum ada
with app.app_context():
    create_tables_and_admin(app)

# Jalankan aplikasi
if __name__ == '__main__':
    # Pastikan host 0.0.0.0 agar bisa diakses di jaringan lokal
    app.run(debug=True, host='0.0.0.0', port=5000)