from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Message, db
from forms import LoginForm, RegistrationForm
from flask_socketio import emit
from functools import wraps

# Track connected users by their user IDs and session IDs
connected_users = {}  # Maps session ID to user ID

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('У вас нет прав доступа к этой странице.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def configure_routes(app, socketio):
    
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
            message = Message(body=data['message'], author=current_user)
            db.session.add(message)
            db.session.commit()
            
            emit('receive_message', {
                'message': message.body,
                'username': current_user.username,
                'timestamp': message.timestamp.strftime('%H:%M')
            }, broadcast=True)