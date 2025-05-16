from flask import Flask
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from config import Config
from models import db, User, PrivateMessage
from routes import configure_routes

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.context_processor
def inject_unread_messages():
    if current_user.is_authenticated:
        unread_count = PrivateMessage.query.filter_by(
            recipient_id=current_user.id, 
            is_read=False
        ).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}

# Create all database tables
with app.app_context():
    db.create_all()

configure_routes(app, socketio)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)