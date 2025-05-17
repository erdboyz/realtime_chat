"""
Database models for the chat application
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import base64
import os

# Initialize SQLAlchemy
db = SQLAlchemy()

# Application encryption key - generated once and used for all messages
# In production, this should be stored in environment variables or a secure vault
APP_ENCRYPTION_KEY = Fernet.generate_key()
ENCRYPTOR = Fernet(APP_ENCRYPTION_KEY)

class User(UserMixin, db.Model):
    """User model representing application users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200), default='default_avatar.png')
    encryption_salt = db.Column(db.String(64), default=lambda: base64.urlsafe_b64encode(os.urandom(32)).decode())
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    sent_messages = db.relationship('PrivateMessage', foreign_keys='PrivateMessage.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('PrivateMessage', foreign_keys='PrivateMessage.recipient_id', backref='recipient', lazy='dynamic')

    def __repr__(self):
        return f'<Пользователь {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    """Public message model for the chat room"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Сообщение {self.body}>'

class PrivateMessage(db.Model):
    """Private message model for direct messaging between users"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    is_encrypted = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<PrivateMessage {self.id}>'
    
    def encrypt_message(self, plain_text):
        """Encrypt a message using the application encryption key"""
        if not plain_text:
            return ''
        
        try:
            encrypted_data = ENCRYPTOR.encrypt(plain_text.encode())
            return encrypted_data.decode()
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return plain_text
    
    def decrypt_message(self, encrypted_text):
        """Decrypt a message using the application encryption key"""
        if not encrypted_text or not self.is_encrypted:
            return encrypted_text
        
        # Don't try to decrypt already decrypted messages
        if not encrypted_text.startswith('gAAAAAB'):
            return encrypted_text
            
        try:
            decrypted_data = ENCRYPTOR.decrypt(encrypted_text.encode())
            return decrypted_data.decode()
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return "[Зашифрованное сообщение]" 