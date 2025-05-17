from flask import render_template, flash, redirect, url_for, request, jsonify, abort, current_app, session
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Message, PrivateMessage, db
from forms import LoginForm, RegistrationForm, ProfileForm
from flask_socketio import emit, join_room
from functools import wraps
from datetime import datetime, timezone, timedelta
import os
import secrets
from PIL import Image
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_, desc

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
    
    @app.route('/user/<username>')
    @login_required
    def view_user_profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        return render_template('user_profile.html', title=f'Профиль {user.username}', user=user)
    
    @app.route('/conversations')
    @login_required
    def conversations():
        # Find all unique users that the current user has exchanged messages with
        sent_to_users = db.session.query(User).join(PrivateMessage, User.id == PrivateMessage.recipient_id)\
            .filter(PrivateMessage.sender_id == current_user.id).all()
        
        received_from_users = db.session.query(User).join(PrivateMessage, User.id == PrivateMessage.sender_id)\
            .filter(PrivateMessage.recipient_id == current_user.id).all()
        
        # Combine and deduplicate users
        conversation_users = list(set(sent_to_users + received_from_users))
        
        conversations = []
        
        # For each user, get last message and unread count
        for user in conversation_users:
            # Find the last message between current user and this user
            last_message = PrivateMessage.query.filter(
                or_(
                    and_(PrivateMessage.sender_id == current_user.id, PrivateMessage.recipient_id == user.id),
                    and_(PrivateMessage.sender_id == user.id, PrivateMessage.recipient_id == current_user.id)
                )
            ).order_by(desc(PrivateMessage.timestamp)).first()
            
            # Count unread messages from this user
            unread_count = PrivateMessage.query.filter(
                PrivateMessage.sender_id == user.id,
                PrivateMessage.recipient_id == current_user.id,
                PrivateMessage.is_read == False
            ).count()
            
            if last_message:
                # Format time
                now = datetime.now(timezone.utc)
                message_time = last_message.timestamp
                
                # If today, show time HH:MM
                if message_time.date() == now.date():
                    adjusted_hour = (message_time.hour + TIMEZONE_OFFSET) % 24
                    time_str = f"{adjusted_hour:02d}:{message_time.minute:02d}"
                else:
                    # If within a week, show day name
                    days_diff = (now.date() - message_time.date()).days
                    if days_diff < 7:
                        weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                        time_str = weekday_names[message_time.weekday()]
                    else:
                        # Otherwise show date DD.MM
                        time_str = f"{message_time.day:02d}.{message_time.month:02d}"
                
                # Create conversation data
                conversations.append({
                    'user': user,
                    'last_message': last_message.body[:30] + ('...' if len(last_message.body) > 30 else ''),
                    'time': time_str,
                    'unread_count': unread_count
                })
        
        # Sort conversations: first by unread (unread first), then by timestamp (newest first)
        conversations.sort(key=lambda x: (-x['unread_count'], x['time']), reverse=True)
        
        return render_template('conversations.html', title='Личные сообщения', conversations=conversations)
    
    @app.route('/messages/<username>')
    @login_required
    def private_messages(username):
        # Get the other user
        other_user = User.query.filter_by(username=username).first_or_404()
        
        # Can't message yourself
        if other_user.id == current_user.id:
            flash('Вы не можете отправлять сообщения самому себе', 'warning')
            return redirect(url_for('conversations'))
        
        # Get all messages between the current user and the other user
        messages = PrivateMessage.query.filter(
            or_(
                and_(PrivateMessage.sender_id == current_user.id, PrivateMessage.recipient_id == other_user.id),
                and_(PrivateMessage.sender_id == other_user.id, PrivateMessage.recipient_id == current_user.id)
            )
        ).order_by(PrivateMessage.timestamp).all()
        
        # Mark all messages from the other user as read
        unread_messages = PrivateMessage.query.filter(
            PrivateMessage.sender_id == other_user.id,
            PrivateMessage.recipient_id == current_user.id,
            PrivateMessage.is_read == False
        ).all()
        
        message_ids = []
        for message in unread_messages:
            message.is_read = True
            message_ids.append(message.id)
        
        db.session.commit()
        
        # Notify the sender that their messages have been read
        if message_ids:
            socketio.emit('message_read_status', {
                'message_ids': message_ids
            }, room=f"user_{other_user.id}")
        
        return render_template('private_messages.html', title=f'Сообщения с {other_user.username}', 
                              messages=messages, other_user=other_user)
    
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
            # Add user to their own room for private messaging
            join_room(f"user_{current_user.id}")
            
            # Add user with their session ID for user count
            connected_users[request.sid] = current_user.id
            
            # Count distinct users (not connections)
            distinct_users = set(connected_users.values())
            emit('user_count', {'count': len(distinct_users)}, broadcast=True)
            
            # Broadcast user online status to everyone
            emit('user_connected', {'user_id': current_user.id}, broadcast=True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if request.sid in connected_users:
            user_id = connected_users[request.sid]
            
            # Remove this connection
            del connected_users[request.sid]
            
            # Count distinct users (not connections)
            distinct_users = set(connected_users.values())
            emit('user_count', {'count': len(distinct_users)}, broadcast=True)
            
            # Check if user has completely gone offline (no more sessions)
            if user_id not in connected_users.values():
                # Broadcast user offline status to everyone
                emit('user_disconnected', {'user_id': user_id}, broadcast=True)
    
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
    
    @socketio.on('send_private_message')
    def handle_private_message(data):
        if current_user.is_authenticated and 'message' in data and 'recipient_id' in data:
            recipient_id = int(data['recipient_id'])
            recipient = User.query.get(recipient_id)
            
            if not recipient:
                return
            
            # Create and save the message
            now = datetime.now(timezone.utc)
            message = PrivateMessage(
                body=data['message'],
                sender_id=current_user.id,
                recipient_id=recipient_id,
                timestamp=now,
                is_read=False
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Format time for display
            adjusted_hour = (now.hour + TIMEZONE_OFFSET) % 24
            formatted_time = f"{adjusted_hour:02d}:{now.minute:02d}"
            
            # Prepare message data
            message_data = {
                'message_id': message.id,
                'message': message.body,
                'sender_id': current_user.id,
                'recipient_id': recipient_id,
                'display_time': formatted_time,
                'timestamp': message.timestamp.isoformat(),
                'avatar': current_user.avatar,
                'username': current_user.username,
                'is_read': False
            }
            
            # Emit to sender and recipient
            emit('receive_private_message', message_data, room=request.sid)
            emit('receive_private_message', message_data, room=f"user_{recipient_id}")
            
            # Also emit a new_private_message event to update counters in real-time
            # Only broadcast to recipient 
            notification_data = {
                'sender_id': current_user.id,
                'recipient_id': recipient_id
            }
            emit('new_private_message', notification_data, room=f"user_{recipient_id}")
    
    @socketio.on('mark_message_read')
    def handle_mark_message_read(data):
        if current_user.is_authenticated and 'message_id' in data:
            message = PrivateMessage.query.get(int(data['message_id']))
            
            if message and message.recipient_id == current_user.id:
                message.is_read = True
                db.session.commit()
                
                # Notify the sender that their message has been read
                emit('message_read_status', {
                    'message_ids': [message.id]
                }, room=f"user_{message.sender_id}")
    
    @socketio.on('request_online_users')
    def handle_request_online_users():
        # Get all distinct user IDs that are currently connected
        online_user_ids = list(set(connected_users.values()))
        emit('online_users', {'user_ids': online_user_ids})
    
    @socketio.on('new_private_message')
    def handle_new_private_message(data):
        # Forward the new message notification to all clients
        if current_user.is_authenticated and 'sender_id' in data:
            # Ensure we're broadcasting to everyone except the sender
            sender_id = int(data['sender_id'])
            emit('new_private_message', data, broadcast=True)
            
            # Log for debugging
            print(f"Broadcasting new_private_message from {sender_id}")
    
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