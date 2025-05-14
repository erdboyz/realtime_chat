from flask import render_template, flash, redirect, url_for, request, jsonify, abort, current_app, session
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Message, db
from forms import LoginForm, RegistrationForm, ProfileForm
from flask_socketio import emit
from functools import wraps
from datetime import datetime, timezone, timedelta
import os
import secrets
from PIL import Image
from werkzeug.utils import secure_filename

# Track connected users by their user IDs and session IDs
connected_users = {}  # Maps session ID to user ID

# Define the time zone offset to apply (MSK is UTC+3)
TIMEZONE_OFFSET = 3  # hours

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('У вас нет прав доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def configure_routes(app, socketio):
    
    # Helper function to save avatar files
    def save_avatar(form_avatar):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_avatar.filename)
        avatar_filename = random_hex + f_ext
        avatar_path = os.path.join(app.root_path, 'static/avatars', avatar_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.join(app.root_path, 'static/avatars'), exist_ok=True)
        
        # Open and process the image with high quality settings
        image = Image.open(form_avatar)
        
        # Keep aspect ratio by creating a square crop of the center
        width, height = image.size
        min_dimension = min(width, height)
        
        # Calculate crop box (left, upper, right, lower)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension
        
        # Crop to square
        image = image.crop((left, top, right, bottom))
        
        # Resize to desired dimensions (preserving quality)
        output_size = (200, 200)  # Increased from 150x150 for better quality
        image = image.resize(output_size, Image.Resampling.LANCZOS)  # Using high quality resampling
        
        # Save with maximum quality for JPEG
        if f_ext.lower() in ['.jpg', '.jpeg']:
            image.save(avatar_path, format='JPEG', quality=95)
        else:
            image.save(avatar_path)
        
        return avatar_filename
    
    @app.route('/')
    @app.route('/index')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('chat'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('chat'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Неверное имя пользователя или пароль')
                return redirect(url_for('login'))
            
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('chat'))
        
        return render_template('login.html', title='Вход', form=form)
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('chat'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if this is the first user to register
            is_first_user = User.query.count() == 0
            
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            
            # If this is the first user, make them an admin
            if is_first_user:
                user.is_admin = True
            
            db.session.add(user)
            db.session.commit()
            
            if is_first_user:
                flash('Поздравляем! Вы зарегистрированы как администратор.')
            else:
                flash('Поздравляем, вы зарегистрированы!')
                
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Регистрация', form=form)
    
    @app.route('/chat')
    @login_required
    def chat():
        messages = Message.query.order_by(Message.timestamp.asc()).all()
        return render_template('chat.html', title='Чат', messages=messages)
    
    @app.route('/admin')
    @login_required
    @admin_required
    def admin():
        users = User.query.all()
        return render_template('admin.html', title='Админ-панель', users=users)
    
    @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            flash('Вы не можете удалить свой собственный аккаунт.', 'danger')
            return redirect(url_for('admin'))
            
        # Check if target user is an admin
        if user.is_admin and user.id != current_user.id:
            flash('Вы не можете удалить другого администратора.', 'danger')
            return redirect(url_for('admin'))
            
        # Delete all messages from the user
        Message.query.filter_by(user_id=user.id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Пользователь {user.username} был удален.', 'success')
        return redirect(url_for('admin'))
    
    @app.route('/admin/clear_chat', methods=['POST'])
    @login_required
    @admin_required
    def clear_chat():
        # Delete all messages
        Message.query.delete()
        db.session.commit()
        
        # Emit event to all clients to clear chat
        socketio.emit('clear_chat')
        
        flash('Чат успешно очищен.', 'success')
        return redirect(url_for('admin'))
    
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            # Add user with their session ID
            connected_users[request.sid] = current_user.id
            
            # Count distinct users (not connections)
            distinct_users = set(connected_users.values())
            emit('user_count', {'count': len(distinct_users)}, broadcast=True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if request.sid in connected_users:
            # Remove this connection
            del connected_users[request.sid]
            
            # Count distinct users (not connections)
            distinct_users = set(connected_users.values())
            emit('user_count', {'count': len(distinct_users)}, broadcast=True)
    
    @socketio.on('send_message')
    def handle_message(data):
        if current_user.is_authenticated:
            # Create message with current time
            now = datetime.now(timezone.utc)
            message = Message(body=data['message'], author=current_user, timestamp=now)
            db.session.add(message)
            db.session.commit()
            
            # Calculate time with offset
            adjusted_hour = (now.hour + TIMEZONE_OFFSET) % 24
            formatted_time = f"{adjusted_hour:02d}:{now.minute:02d}"
            
            # Send formatted time
            emit('receive_message', {
                'message': message.body,
                'username': current_user.username,
                'display_time': formatted_time,
                'timestamp': message.timestamp.isoformat(),
                'avatar': current_user.avatar
            }, broadcast=True)
    
    @app.route('/profile')
    @login_required
    def profile():
        # Check if profile was just updated and show a notification if so
        show_profile_updated = session.pop('profile_updated', False)
        
        return render_template('profile.html', title='Профиль', user=current_user, 
                            show_profile_updated=show_profile_updated)
    
    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
        if form.validate_on_submit():
            # Check if current password is provided and correct when changing password
            if form.new_password.data:
                if not form.current_password.data:
                    flash('Для изменения пароля необходимо ввести текущий пароль', 'danger')
                    return render_template('edit_profile.html', title='Редактировать профиль', form=form)
                
                if not current_user.check_password(form.current_password.data):
                    flash('Текущий пароль введен неверно', 'danger')
                    return render_template('edit_profile.html', title='Редактировать профиль', form=form)
                
                current_user.set_password(form.new_password.data)
                # Only show password change notification on the profile page
                # flash('Пароль успешно изменен', 'success')
            
            # Update username and email
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            # Handle avatar upload
            if form.avatar.data:
                try:
                    avatar_file = save_avatar(form.avatar.data)
                    # Delete old avatar if it's not the default
                    if current_user.avatar != 'default_avatar.png':
                        old_avatar_path = os.path.join(app.root_path, 'static/avatars', current_user.avatar)
                        if os.path.exists(old_avatar_path):
                            os.remove(old_avatar_path)
                    current_user.avatar = avatar_file
                except Exception as e:
                    flash(f'Ошибка при загрузке аватара: {str(e)}', 'danger')
            
            db.session.commit()
            
            # Store the success message in the session instead of using flash
            # This ensures it only appears on the profile page
            session['profile_updated'] = True
            return redirect(url_for('profile'))
            
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
            
        return render_template('edit_profile.html', title='Редактировать профиль', form=form)