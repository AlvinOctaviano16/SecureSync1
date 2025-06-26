# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bcrypt import hashpw, gensalt, checkpw
from cryptography.fernet import Fernet
import os
from datetime import datetime

# Inisialisasi Flask aplikasi
app = Flask(__name__)

# --- PENTING: KUNCI RAHASIA APLIKASI ---
# GANTI INI DENGAN STRING ACAK YANG SANGAT KUAT DAN UNIK!
# Digunakan untuk mengamankan sesi pengguna (Flask session).
app.config['SECRET_KEY'] = 'a_very_long_and_complex_secret_key_for_your_secure_app_123!@#ABC'

# Konfigurasi Database SQLite
# 'sqlite:///site.db' berarti database akan disimpan dalam file 'site.db' di folder yang sama dengan app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Menonaktifkan pelacakan modifikasi objek SQLAlchemy

# Inisialisasi SQLAlchemy dengan aplikasi Flask
db = SQLAlchemy(app)

# Konfigurasi Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Menentukan endpoint login jika pengguna belum terautentikasi

# --- PENTING: KUNCI ENKRIPSI FERNET ---
# Kunci ini digunakan untuk enkripsi/dekripsi data sensitif (deskripsi tugas).
# Ini adalah kunci yang Anda dapatkan sebelumnya dari terminal.
app.config['FERNET_KEY'] = b't7tqK5Ba9xS6eQHgN6GLpF94cYlgdAKxY-tAVmO14y0='
cipher_suite = Fernet(app.config['FERNET_KEY'])

# --- User Loader untuk Flask-Login ---
# Fungsi ini dipanggil oleh Flask-Login untuk memuat objek User berdasarkan ID-nya dari sesi.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- MODEL DATABASE (Definisi Tabel) ---
# Setiap kelas merepresentasikan satu tabel di database.
# Nama tabel di database otomatis menjadi lowercase dan snake_case dari nama kelas.
# Contoh: Kelas `User` -> tabel `user`, `ToDoList` -> tabel `to_do_list`.

# Model User: Untuk menyimpan informasi pengguna (username, password hashed, role)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False) # Menyimpan hash password
    role = db.Column(db.String(10), default='user') # Peran pengguna: 'user' atau 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke ToDoList (sebagai pemilik), ToDoListMember (sebagai anggota), Task (sebagai pembuat), dan ActivityLog (sebagai aktor)
    owned_todo_lists = db.relationship('ToDoList', backref='owner', lazy=True)
    memberships = db.relationship('ToDoListMember', backref='member', lazy=True)
    created_tasks = db.relationship('Task', backref='creator', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='actor', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

    # Metode untuk hashing password menggunakan bcrypt
    def set_password(self, password_text):
        self.password = hashpw(password_text.encode('utf-8'), gensalt()).decode('utf-8')

    # Metode untuk memeriksa password yang dimasukkan dengan hash yang tersimpan
    def check_password(self, password_text):
        return checkpw(password_text.encode('utf-8'), self.password.encode('utf-8'))

# Model ToDoList: Untuk menyimpan daftar tugas utama
class ToDoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # FOREIGN KEY: Merujuk ke tabel 'user'
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke Task (tugas-tugas di dalamnya) dan ToDoListMember (anggota kolaborasi)
    tasks = db.relationship('Task', backref='todo_list', lazy=True, cascade="all, delete-orphan")
    members = db.relationship('ToDoListMember', backref='todo_list', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"ToDoList('{self.name}', Owner:{self.owner_id})"

# Model Task: Untuk menyimpan setiap tugas dalam daftar ToDoList
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # FOREIGN KEY: Merujuk ke tabel 'to_do_list' (nama tabel otomatis dari ToDoList)
    todo_list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description_encrypted = db.Column(db.LargeBinary, nullable=False) # Deskripsi yang dienkripsi
    status = db.Column(db.String(20), default='pending', nullable=False) # Status tugas: 'pending' atau 'completed'
    # FOREIGN KEY: Merujuk ke tabel 'user'
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Siapa yang membuat tugas ini
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Task('{self.title}', Status:'{self.status}')"

    # Metode untuk enkripsi deskripsi sebelum disimpan ke database
    def set_description(self, description_text):
        self.description_encrypted = cipher_suite.encrypt(description_text.encode('utf-8'))

    # Metode untuk dekripsi deskripsi saat diambil dari database
    def get_description(self):
        return cipher_suite.decrypt(self.description_encrypted).decode('utf-8')

# Model ToDoListMember: Untuk mengelola anggota dan tingkat izin dalam ToDoList kolaboratif
class ToDoListMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # FOREIGN KEY: Merujuk ke tabel 'to_do_list'
    todo_list_id = db.Column(db.Integer, db.ForeignKey('to_do_list.id'), nullable=False)
    # FOREIGN KEY: Merujuk ke tabel 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permission_level = db.Column(db.String(20), nullable=False, default='read') # Tingkat izin: 'read', 'write'

    # Memastikan kombinasi todo_list_id dan user_id unik (satu user hanya bisa jadi anggota sekali per list)
    __table_args__ = (db.UniqueConstraint('todo_list_id', 'user_id', name='_todo_list_member_uc'),)

    def __repr__(self):
        return f"ToDoListMember(User:{self.user_id} -> ToDoList:{self.todo_list_id}, Perm:'{self.permission_level}')"

# Model ActivityLog: Untuk mencatat aktivitas penting pengguna (Accounting)
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # FOREIGN KEY: Merujuk ke tabel 'user' (nullable karena aksi bisa dari sistem)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False) # Jenis aksi (e.g., 'user_registered', 'create_todo')
    details = db.Column(db.Text, nullable=True) # Detail tambahan tentang aksi
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ActivityLog(User:{self.user_id}, Action:'{self.action}', Time:'{self.timestamp}')"

# --- Fungsi untuk Membuat Tabel Database dan User Admin Default ---
# Fungsi ini akan dipanggil secara eksplisit saat aplikasi dijalankan untuk pertama kali
# dalam konteks aplikasi.
def create_tables_and_admin():
    db.create_all() # Membuat semua tabel yang didefinisikan oleh model di database
    # Membuat user admin default jika belum ada
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', role='admin')
        admin_user.set_password('adminpassword') # GANTI PASSWORD INI DI LINGKUNGAN PRODUKSI!
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: username='admin', password='adminpassword'")

# --- ROUTES (Fungsionalitas Aplikasi) ---

# Halaman Beranda
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

# Route Services (Placeholder)
@app.route("/services")
def services():
    # Ini adalah halaman placeholder. Anda bisa mengisi kontennya nanti.
    return render_template('services.html')

# Route About Us (Placeholder)
@app.route("/about")
def about():
    # Ini adalah halaman placeholder. Anda bisa mengisi kontennya nanti.
    return render_template('about.html')

# Registrasi Pengguna Baru
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: # Jika user sudah login, redirect ke dashboard
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password or not confirm_password:
            flash('Semua kolom wajib diisi!', 'danger')
        elif password != confirm_password:
            flash('Password tidak cocok!', 'danger')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username sudah ada. Silakan pilih yang lain.', 'danger')
            else:
                user = User(username=username)
                user.set_password(password) # Hash password sebelum disimpan
                db.session.add(user)
                db.session.commit()
                # Log aktivitas (Accounting)
                log = ActivityLog(user_id=user.id, action='user_registered', details=f"Pengguna '{username}' mendaftar.")
                db.session.add(log)
                db.session.commit()
                flash('Akun Anda telah dibuat! Anda sekarang bisa login.', 'success')
                return redirect(url_for('login'))
    return render_template('register.html')

# Login Pengguna
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # Jika user sudah login, redirect ke dashboard
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password): # Verifikasi password
            login_user(user) # Login pengguna dengan Flask-Login
            # Log aktivitas (Accounting)
            log = ActivityLog(user_id=user.id, action='user_logged_in', details=f"Pengguna '{username}' login.")
            db.session.add(log)
            db.session.commit()
            flash(f'Selamat datang, {user.username}! Login berhasil.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login gagal. Periksa username dan password.', 'danger')
    return render_template('login.html')

# Logout Pengguna
@app.route("/logout")
@login_required # Hanya pengguna yang sudah login yang bisa logout
def logout():
    # Log aktivitas (Accounting)
    log = ActivityLog(user_id=current_user.id, action='user_logged_out', details=f"Pengguna '{current_user.username}' logout.")
    db.session.add(log)
    db.session.commit()
    logout_user() # Logout pengguna dari sesi
    flash('Anda telah logout.', 'info')
    return redirect(url_for('home'))

# Dashboard Pengguna: Menampilkan ToDoList milik sendiri dan yang di-share
@app.route("/dashboard")
@login_required
def dashboard():
    # To-Do Lists yang dimiliki oleh user yang sedang login
    owned_lists = ToDoList.query.filter_by(owner_id=current_user.id).order_by(ToDoList.created_at.desc()).all()

    # To-Do Lists yang di-share dengan user yang sedang login
    shared_memberships = ToDoListMember.query.filter_by(user_id=current_user.id).all()
    # Mengambil objek ToDoList dari relasi membership
    shared_lists = [membership.todo_list for membership in shared_memberships if membership.todo_list]
    
    # Filter list yang dimiliki sendiri agar tidak duplikat di bagian "shared_lists"
    shared_lists = [lst for lst in shared_lists if lst.owner_id != current_user.id]

    return render_template('dashboard.html', owned_lists=owned_lists, shared_lists=shared_lists, current_user=current_user)

# Membuat To-Do List Baru
@app.route("/create_todo", methods=['GET', 'POST'])
@login_required # Hanya pengguna yang login bisa membuat ToDoList
def create_todo():
    if request.method == 'POST':
        todo_name = request.form.get('name')
        if not todo_name:
            flash('Nama To-Do List tidak boleh kosong!', 'danger')
        else:
            new_todo = ToDoList(name=todo_name, owner=current_user) # current_user adalah objek User Flask-Login
            db.session.add(new_todo)
            db.session.commit()
            # Log aktivitas (Accounting)
            log = ActivityLog(user_id=current_user.id, action='create_todo', details=f"Membuat To-Do List '{todo_name}' (ID: {new_todo.id}).")
            db.session.add(log)
            db.session.commit()
            flash(f'To-Do List "{todo_name}" berhasil dibuat!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('create_todo.html')

# Melihat Detail To-Do List dan Tugas-tugasnya
@app.route("/todo/<int:todo_id>")
@login_required
def todo_detail(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id) # Mengambil ToDoList atau menampilkan 404 jika tidak ditemukan

    # Authorization: Memeriksa apakah pengguna adalah pemilik atau anggota dari ToDoList ini
    is_owner = (todo_list.owner_id == current_user.id)
    is_member = ToDoListMember.query.filter_by(todo_list_id=todo_id, user_id=current_user.id).first()
    
    # Jika bukan pemilik dan bukan anggota, tolak akses
    if not is_owner and not is_member:
        flash('Anda tidak memiliki izin untuk melihat To-Do List ini.', 'danger')
        return redirect(url_for('dashboard'))

    # Mengambil semua tugas untuk ToDoList ini
    tasks = Task.query.filter_by(todo_list_id=todo_id).order_by(Task.created_at.asc()).all()
    
    # Menentukan tingkat izin pengguna untuk ToDoList ini
    permission = 'read' # Default jika dia anggota (member)
    if is_owner:
        permission = 'owner' # Jika dia pemilik
    elif is_member and is_member.permission_level == 'write':
        permission = 'write' # Jika dia anggota dengan izin 'write'

    return render_template('todo_list_detail.html', todo_list=todo_list, tasks=tasks, permission=permission)

# Menambahkan Tugas Baru ke To-Do List
@app.route("/todo/<int:todo_id>/add_task", methods=['POST'])
@login_required
def add_task(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)

    # Authorization: Hanya pemilik atau anggota dengan izin 'write' yang bisa menambah tugas
    is_owner = (todo_list.owner_id == current_user.id)
    is_write_member = ToDoListMember.query.filter_by(
        todo_list_id=todo_id, user_id=current_user.id, permission_level='write'
    ).first()

    if not is_owner and not is_write_member:
        flash('Anda tidak memiliki izin untuk menambah tugas ke To-Do List ini.', 'danger')
        return redirect(url_for('todo_detail', todo_id=todo_id))

    task_title = request.form.get('title')
    task_description = request.form.get('description')

    if not task_title:
        flash('Judul tugas tidak boleh kosong!', 'danger')
    else:
        new_task = Task(title=task_title, todo_list=todo_list, creator=current_user)
        new_task.set_description(task_description) # Enkripsi deskripsi sebelum disimpan
        db.session.add(new_task)
        db.session.commit()
        # Log aktivitas (Accounting)
        log = ActivityLog(user_id=current_user.id, action='add_task', details=f"Menambahkan tugas '{task_title}' ke To-Do List '{todo_list.name}' (ID: {todo_list.id}).")
        db.session.add(log)
        db.session.commit()
        flash('Tugas berhasil ditambahkan!', 'success')
    return redirect(url_for('todo_detail', todo_id=todo_id))

# Memperbarui Status Tugas (pending/completed)
@app.route("/task/<int:task_id>/update_status", methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    todo_list = task.todo_list

    # Authorization: Hanya pemilik atau anggota dengan izin 'write' yang bisa mengubah status tugas
    is_owner = (todo_list.owner_id == current_user.id)
    is_write_member = ToDoListMember.query.filter_by(
        todo_list_id=todo_list.id, user_id=current_user.id, permission_level='write'
    ).first()
    
    if not is_owner and not is_write_member:
        flash('Anda tidak memiliki izin untuk memperbarui status tugas ini.', 'danger')
        return redirect(url_for('todo_detail', todo_id=todo_list.id))

    new_status = request.form.get('status')
    if new_status in ['pending', 'completed']: # Memastikan status yang valid
        old_status = task.status
        task.status = new_status
        db.session.commit()
        # Log aktivitas (Accounting)
        log = ActivityLog(user_id=current_user.id, action='update_task_status', details=f"Status tugas '{task.title}' diubah dari '{old_status}' menjadi '{new_status}' di To-Do List '{todo_list.name}'.")
        db.session.add(log)
        db.session.commit()
        flash(f'Status tugas "{task.title}" berhasil diperbarui menjadi "{new_status}"!', 'success')
    else:
        flash('Status tidak valid diberikan.', 'danger')
    return redirect(url_for('todo_detail', todo_id=todo_list.id))

# Menghapus To-Do List
@app.route("/todo/<int:todo_id>/delete", methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)

    # Authorization: Hanya pemilik yang bisa menghapus To-Do List
    if todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus To-Do List ini.', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(todo_list) # Menghapus ToDoList (dan tugas-tugas di dalamnya karena cascade)
    db.session.commit()
    # Log aktivitas (Accounting)
    log = ActivityLog(user_id=current_user.id, action='delete_todo', details=f"Menghapus To-Do List '{todo_list.name}' (ID: {todo_id}).")
    db.session.add(log)
    db.session.commit()
    flash('To-Do List berhasil dihapus!', 'success')
    return redirect(url_for('dashboard'))

# Menghapus Tugas dari To-Do List
@app.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    todo_list = task.todo_list

    # Authorization: Hanya pemilik ToDoList yang bisa menghapus tugas dari ToDoList tersebut
    if todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus tugas ini.', 'danger')
        return redirect(url_for('todo_detail', todo_id=todo_list.id))

    db.session.delete(task) # Menghapus tugas
    db.session.commit()
    # Log aktivitas (Accounting)
    log = ActivityLog(user_id=current_user.id, action='delete_task', details=f"Menghapus tugas '{task.title}' dari To-Do List '{todo_list.name}'.")
    db.session.add(log)
    db.session.commit()
    flash('Tugas berhasil dihapus!', 'success')
    return redirect(url_for('todo_detail', todo_id=todo_list.id))

# Berbagi To-Do List dengan Pengguna Lain
@app.route("/todo/<int:todo_id>/share", methods=['GET', 'POST'])
@login_required
def share_todo(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)

    # Authorization: Hanya pemilik yang bisa berbagi To-Do List
    if todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk berbagi To-Do List ini.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username_to_share = request.form.get('username')
        permission_level = request.form.get('permission') # 'read' atau 'write'

        user_to_share = User.query.filter_by(username=username_to_share).first()

        if not user_to_share:
            flash(f'Pengguna "{username_to_share}" tidak ditemukan.', 'danger')
        elif user_to_share.id == current_user.id:
            flash('Anda tidak bisa berbagi To-Do List dengan diri sendiri.', 'warning')
        else:
            existing_member = ToDoListMember.query.filter_by(
                todo_list_id=todo_id, user_id=user_to_share.id
            ).first()
            if existing_member:
                # Update permission if already a member, if different
                if existing_member.permission_level != permission_level:
                    existing_member.permission_level = permission_level
                    db.session.commit()
                    log = ActivityLog(user_id=current_user.id, action='update_share_permission', details=f"Mengubah izin berbagi To-Do List '{todo_list.name}' untuk '{user_to_share.username}' menjadi '{permission_level}'.")
                    db.session.add(log)
                    db.session.commit()
                    flash(f'Izin berbagi untuk "{username_to_share}" berhasil diperbarui menjadi {permission_level}!', 'success')
                else:
                    flash(f'Pengguna "{username_to_share}" sudah menjadi anggota To-Do List ini dengan izin yang sama.', 'warning')
            else:
                new_member = ToDoListMember(
                    todo_list=todo_list, user=user_to_share, permission_level=permission_level
                )
                db.session.add(new_member)
                db.session.commit()
                # Log aktivitas (Accounting)
                log = ActivityLog(user_id=current_user.id, action='share_todo', details=f"Membagi To-Do List '{todo_list.name}' dengan '{user_to_share.username}' (Izin: {permission_level}).")
                db.session.add(log)
                db.session.commit()
                flash(f'To-Do List berhasil dibagikan dengan "{username_to_share}" dengan akses {permission_level}!', 'success')
                return redirect(url_for('share_todo', todo_id=todo_id))
    
    # Mendapatkan daftar anggota saat ini untuk ditampilkan di halaman share
    current_members = ToDoListMember.query.filter_by(todo_list_id=todo_id).all()
    return render_template('share_todo.html', todo_list=todo_list, current_members=current_members)

# Admin Panel: Melihat Log Aktivitas dan Mengelola Pengguna
@app.route("/admin_panel", methods=['GET', 'POST']) # Tambahkan metode POST untuk reset password
@login_required
def admin_panel():
    # Authorization: Hanya pengguna dengan peran 'admin' yang bisa melihat dan menggunakan admin panel
    if current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses Admin Panel.', 'danger')
        return redirect(url_for('dashboard'))

    # Bagian untuk menampilkan log aktivitas
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()

    # Bagian untuk menampilkan daftar pengguna
    users = User.query.order_by(User.username.asc()).all()

    return render_template('admin_panel.html', logs=logs, users=users)

# Route untuk Reset Password Pengguna (Admin Only)
@app.route("/admin/reset_password/<int:user_id>", methods=['POST'])
@login_required
def admin_reset_password(user_id):
    # Authorization: Hanya pengguna dengan peran 'admin' yang bisa mereset password
    if current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk mereset password pengguna.', 'danger')
        return redirect(url_for('dashboard'))

    user_to_reset = User.query.get_or_404(user_id)
    
    # Mencegah admin mereset password admin default-nya sendiri secara tidak sengaja melalui fitur ini
    if user_to_reset.username == 'admin' and user_to_reset.id == current_user.id:
        flash('Anda tidak dapat mereset password akun admin Anda sendiri melalui fitur ini. Gunakan metode lain jika diperlukan.', 'warning')
        return redirect(url_for('admin_panel'))

    # Generate password sementara yang kuat
    temporary_password = os.urandom(8).hex() # Contoh password 16 karakter acak (hex)
    user_to_reset.set_password(temporary_password) # Hash dan set password baru
    db.session.commit()

    # Log aktivitas (Accounting)
    log = ActivityLog(user_id=current_user.id, action='admin_reset_password', details=f"Admin '{current_user.username}' mereset password pengguna '{user_to_reset.username}'. Password sementara: {temporary_password}")
    db.session.add(log)
    db.session.commit()

    flash(f"Password untuk pengguna '{user_to_reset.username}' telah direset. Password sementara: <strong>{temporary_password}</strong>. Informasikan kepada pengguna dan minta mereka mengubahnya setelah login.", 'success')
    return redirect(url_for('admin_panel'))


# --- Main App Execution ---
if __name__ == '__main__':
    # Untuk memastikan operasi database seperti db.create_all() berjalan dalam konteks aplikasi
    with app.app_context():
        create_tables_and_admin() # Panggil fungsi ini secara manual saat pertama kali dijalankan
        # Jalankan aplikasi Flask
        app.run(debug=True, port=5000)