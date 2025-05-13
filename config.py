import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'супер-секретный-ключ-по-умолчанию'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False