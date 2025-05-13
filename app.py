from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config
from models import db, User
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

configure_routes(app, socketio)

# Create tables before first request
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True)