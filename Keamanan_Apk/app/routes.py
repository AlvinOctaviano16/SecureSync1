from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
# Impor db dari app (objek global)
from app import db 
# Impor model spesifik dari .models
from .models import User, ToDoList, ToDoListMember, Task, ActivityLog
from datetime import datetime
import os

main_bp = Blueprint('main', __name__, template_folder='../templates')

@main_bp.route("/")
@main_bp.route("/home")
def home():
    return render_template('pages/home.html')

@main_bp.route("/login_register", methods=['GET'])
def login_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login_register.html')

@main_bp.route("/process_login", methods=['POST'])
def process_login():
    print("DEBUG: Fungsi process_login diakses.")
    if current_user.is_authenticated:
        print("DEBUG: User sudah terautentikasi, redirect ke dashboard.")
        return redirect(url_for('main.dashboard'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"DEBUG: Menerima username: '{username}', password (sebagian): '{password[:3]}...'")

    user = User.query.filter_by(username=username).first()
    
    if user:
        print(f"DEBUG: User '{username}' ditemukan di database.")
        if user.check_password(password):
            print("DEBUG: Password cocok. Melakukan login user.")
            login_user(user)
            log = ActivityLog(user_id=user.id, action='user_logged_in', details=f"Pengguna '{username}' login.")
            db.session.add(log)
            db.session.commit()
            flash(f'Selamat datang, {user.username}! Login berhasil.', 'success')
            print("DEBUG: Flash message sukses dan redirect ke dashboard.")
            return redirect(url_for('main.dashboard'))
        else:
            print("DEBUG: Password tidak cocok.")
            flash('Login gagal. Periksa username dan password.', 'danger')
            return redirect(url_for('main.login_register', form='login'))
    else:
        print(f"DEBUG: User '{username}' tidak ditemukan.")
        flash('Login gagal. Periksa username dan password.', 'danger')
        return redirect(url_for('main.login_register', form='login'))

@main_bp.route("/process_register", methods=['POST'])
def process_register():
    print("DEBUG: Fungsi process_register diakses.")
    if current_user.is_authenticated:
        print("DEBUG: User sudah terautentikasi, redirect ke dashboard (register).")
        return redirect(url_for('main.dashboard'))
        
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not username or not password or not confirm_password:
        print("DEBUG: Ada kolom kosong saat register.")
        flash('Semua kolom wajib diisi!', 'danger')
    elif password != confirm_password:
        print("DEBUG: Konfirmasi password tidak cocok (register).")
        flash('Konfirmasi password tidak cocok!', 'danger')
    else:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"DEBUG: Username '{username}' sudah ada (register).")
            flash('Username sudah ada. Silakan pilih yang lain.', 'danger')
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            log = ActivityLog(user_id=user.id, action='user_registered', details=f"Pengguna '{username}' mendaftar.")
            db.session.add(log)
            db.session.commit()
            flash('Akun Anda telah dibuat! Silakan login.', 'success')
            print(f"DEBUG: User '{username}' berhasil didaftarkan. Redirect ke login.")
            return redirect(url_for('main.login_register', form='login'))
        
    return redirect(url_for('main.login_register', form='register'))

@main_bp.route("/logout")
@login_required
def logout():
    log = ActivityLog(user_id=current_user.id, action='user_logged_out', details=f"Pengguna '{current_user.username}' logout.")
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('main.home'))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    owned_lists = ToDoList.query.filter_by(owner_id=current_user.id).order_by(ToDoList.created_at.desc()).all()
    shared_memberships = ToDoListMember.query.filter_by(user_id=current_user.id).all()
    shared_lists = [membership.todo_list for membership in shared_memberships if membership.todo_list]
    shared_lists = [lst for lst in shared_lists if lst.owner_id != current_user.id]
    return render_template('pages/dashboard.html', user_todo_lists=owned_lists, shared_todo_lists=shared_lists, current_user=current_user)

@main_bp.route("/services")
def services():
    return render_template('pages/services.html', title='Layanan')

@main_bp.route("/about")
def about():
    return render_template('pages/about.html', title='Tentang Kami')

@main_bp.route("/my_todo_lists")
@login_required
def my_todo_lists():
    owned_lists = ToDoList.query.filter_by(owner_id=current_user.id).order_by(ToDoList.created_at.desc()).all()
    return render_template('todos/my_todo_lists.html', owned_lists=owned_lists)

@main_bp.route("/shared_todo_lists")
@login_required
def shared_todo_lists():
    shared_memberships = ToDoListMember.query.filter_by(user_id=current_user.id).all()
    shared_lists = [membership.todo_list for membership in shared_memberships if membership.todo_list]
    shared_lists = [lst for lst in shared_lists if lst.owner_id != current_user.id]
    return render_template('todos/shared_todo_lists.html', shared_lists=shared_lists)

@main_bp.route("/create_todo", methods=['GET', 'POST'])
@login_required
def create_todo():
    if request.method == 'POST':
        todo_name = request.form.get('name')
        todo_description = request.form.get('description')
        if not todo_name:
            flash('Nama To-Do List tidak boleh kosong!', 'danger')
        else:
            new_todo = ToDoList(name=todo_name, description=todo_description, owner=current_user)
            db.session.add(new_todo)
            db.session.commit()
            log = ActivityLog(user_id=current_user.id, action='create_todo', details=f"Membuat To-Do List '{todo_name}' (ID: {new_todo.id}).")
            db.session.add(log)
            db.session.commit()
            flash(f'To-Do List "{todo_name}" berhasil dibuat!', 'success')
            return redirect(url_for('main.dashboard'))
    return render_template('todos/create_todo.html')

@main_bp.route("/todo/<int:todo_id>")
@login_required
def todo_detail(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)
    is_owner = (todo_list.owner_id == current_user.id)
    is_member = ToDoListMember.query.filter_by(todo_list_id=todo_id, user_id=current_user.id).first()
    if not is_owner and not is_member:
        flash('Anda tidak memiliki izin untuk melihat To-Do List ini.', 'danger')
        return redirect(url_for('main.dashboard'))
    tasks = Task.query.filter_by(todo_list_id=todo_id).order_by(Task.created_at.asc()).all()
    permission = 'read'
    if is_owner:
        permission = 'owner'
    elif is_member and is_member.permission_level == 'write':
        permission = 'write'
    return render_template('todos/todo_list_detail.html', todo_list=todo_list, tasks=tasks, permission=permission)

@main_bp.route("/todo/<int:todo_id>/add_task", methods=['POST'])
@login_required
def add_task(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)
    is_owner = (todo_list.owner_id == current_user.id)
    is_write_member = ToDoListMember.query.filter_by(todo_list_id=todo_list.id, user_id=current_user.id, permission_level='write').first()
    if not is_owner and not is_write_member:
        flash('Anda tidak memiliki izin untuk menambah tugas ke To-Do List ini.', 'danger')
        return redirect(url_for('main.todo_detail', todo_id=todo_list.id))
    task_title = request.form.get('title')
    task_description = request.form.get('description')
    if not task_title:
        flash('Judul tugas tidak boleh kosong!', 'danger')
    else:
        new_task = Task(title=task_title, todo_list=todo_list, creator=current_user)
        new_task.set_description(task_description)
        db.session.add(new_task)
        db.session.commit()
        log = ActivityLog(user_id=current_user.id, action='add_task', details=f"Menambahkan tugas '{new_task.title}' ke To-Do List '{todo_list.name}' (ID: {todo_list.id}).")
        db.session.add(log)
        db.session.commit()
        flash('Tugas berhasil ditambahkan!', 'success')
    return redirect(url_for('main.todo_detail', todo_id=todo_list.id))

@main_bp.route("/task/<int:task_id>/update_status", methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    todo_list = task.todo_list
    is_owner = (todo_list.owner_id == current_user.id)
    is_write_member = ToDoListMember.query.filter_by(todo_list_id=todo_list.id, user_id=current_user.id, permission_level='write').first()
    if not is_owner and not is_write_member:
        flash('Anda tidak memiliki izin untuk memperbarui status tugas ini.', 'danger')
        return redirect(url_for('main.todo_detail', todo_id=todo_list.id))
    new_status = request.form.get('status')
    if new_status in ['pending', 'completed']:
        old_status = task.status
        task.status = new_status
        db.session.commit()
        log = ActivityLog(user_id=current_user.id, action='update_task_status', details=f"Status tugas '{task.title}' diubah dari '{old_status}' menjadi '{new_status}' di To-Do List '{todo_list.name}'.")
        db.session.add(log)
        db.session.commit()
        flash(f'Status tugas "{task.title}" berhasil diperbarui menjadi "{new_status}"!', 'success')
    else:
        flash('Status tidak valid diberikan.', 'danger')
    return redirect(url_for('main.todo_detail', todo_id=todo_list.id))

@main_bp.route("/todo/<int:todo_id>/delete", methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)
    if todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus To-Do List ini.', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(todo_list)
    db.session.commit()
    log = ActivityLog(user_id=current_user.id, action='delete_todo', details=f"Menghapus To-Do List '{todo_list.name}' (ID: {todo_id}).")
    db.session.add(log)
    db.session.commit()
    flash('To-Do List berhasil dihapus!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    todo_list = task.todo_list
    if todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus tugas ini.', 'danger')
        return redirect(url_for('main.todo_detail', todo_id=todo_list.id))
    db.session.delete(task)
    db.session.commit()
    log = ActivityLog(user_id=current_user.id, action='delete_task', details=f"Menghapus tugas '{task.title}' dari To-Do List '{todo_list.name}'.")
    db.session.add(log)
    db.session.commit()
    flash('Tugas berhasil dihapus!', 'success')
    return redirect(url_for('main.todo_detail', todo_id=todo_list.id))

@main_bp.route("/todo/<int:todo_id>/share", methods=['GET', 'POST'])
@login_required
def share_todo(todo_id):
    todo_list = ToDoList.query.get_or_404(todo_id)
    if todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk berbagi To-Do List ini.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username_to_share = request.form.get('username')
        permission_level = request.form.get('permission')
        user_to_share = User.query.filter_by(username=username_to_share).first()
        if not user_to_share:
            flash(f'Pengguna "{username_to_share}" tidak ditemukan.', 'danger')
        elif user_to_share.id == current_user.id:
            flash('Anda tidak bisa berbagi To-Do List dengan diri sendiri.', 'warning')
        else:
            existing_member = ToDoListMember.query.filter_by(todo_list_id=todo_id, user_id=user_to_share.id).first()
            if existing_member:
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
                # KODE YANG DIKOREKSI: Menggunakan todo_list_id alih-alih todo_list
                new_member = ToDoListMember(todo_list_id=todo_list.id, user_id=user_to_share.id, permission_level=permission_level)
                db.session.add(new_member)
                db.session.commit()
                log = ActivityLog(user_id=current_user.id, action='share_todo', details=f"Membagi To-Do List '{todo_list.name}' dengan '{user_to_share.username}' (Izin: {permission_level}).")
                db.session.add(log)
                db.session.commit()
                flash(f'To-Do List berhasil dibagikan dengan "{username_to_share}" dengan akses {permission_level}!', 'success')
                return redirect(url_for('main.share_todo', todo_id=todo_id))
    current_members = ToDoListMember.query.filter_by(todo_list_id=todo_id).all()
    return render_template('todos/share_todo.html', todo_list=todo_list, current_members=current_members)

@main_bp.route("/todo_member/<int:todo_member_id>/remove", methods=['POST'])
@login_required
def remove_member(todo_member_id):
    member_to_remove = ToDoListMember.query.get_or_404(todo_member_id)
    
    # Pastikan current_user adalah owner dari ToDoList ini
    if member_to_remove.todo_list.owner_id != current_user.id:
        flash('Anda tidak memiliki izin untuk menghapus anggota ini.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    todo_list_id = member_to_remove.todo_list.id
    db.session.delete(member_to_remove)
    db.session.commit()
    
    log = ActivityLog(user_id=current_user.id, action='remove_member', details=f"Menghapus '{member_to_remove.user.username}' dari To-Do List '{member_to_remove.todo_list.name}'.")
    db.session.add(log)
    db.session.commit()
    
    flash(f"Anggota '{member_to_remove.user.username}' berhasil dihapus dari To-Do List.", 'success')
    return redirect(url_for('main.share_todo', todo_id=todo_list_id))


@main_bp.route("/admin_panel", methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk mengakses Admin Panel.', 'danger')
        return redirect(url_for('main.dashboard'))
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    users = User.query.order_by(User.username.asc()).all()
    return render_template('pages/admin_panel.html', logs=logs, users=users)

@main_bp.route("/admin/reset_password/<int:user_id>", methods=['POST'])
@login_required
def admin_reset_password(user_id):
    if current_user.role != 'admin':
        flash('Anda tidak memiliki izin untuk mereset password pengguna.', 'danger')
        return redirect(url_for('main.dashboard'))
    user_to_reset = User.query.get_or_404(user_id)
    if user_to_reset.username == 'admin' and user_to_reset.id == current_user.id:
        flash('Anda tidak dapat mereset password akun admin Anda sendiri melalui fitur ini. Gunakan metode lain jika diperlukan.', 'warning')
        return redirect(url_for('main.admin_panel'))
    temporary_password = os.urandom(8).hex()
    user_to_reset.set_password(temporary_password)
    db.session.commit()
    log = ActivityLog(user_id=current_user.id, action='admin_reset_password', details=f"Admin '{current_user.username}' mereset password pengguna '{user_to_reset.username}'. Password sementara: {temporary_password}")
    db.session.add(log)
    db.session.commit()
    flash(f"Password untuk pengguna '{user_to_reset.username}' telah direset. Password sementara: <strong>{temporary_password}</strong>. Informasikan kepada pengguna dan minta mereka mengubahnya setelah login.", 'success')
    return redirect(url_for('main.admin_panel'))