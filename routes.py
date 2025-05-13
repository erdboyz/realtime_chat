from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Message, db
from forms import LoginForm, RegistrationForm
from flask_socketio import emit

# Track connected users
connected_users = set()

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
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Поздравляем, вы зарегистрированы!')
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Регистрация', form=form)
    
    @app.route('/chat')
    @login_required
    def chat():
        messages = Message.query.order_by(Message.timestamp.asc()).all()
        return render_template('chat.html', title='Чат', messages=messages)
    
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            connected_users.add(current_user.id)
            emit('user_count', {'count': len(connected_users)}, broadcast=True)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated and current_user.id in connected_users:
            connected_users.remove(current_user.id)
            emit('user_count', {'count': len(connected_users)}, broadcast=True)
    
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