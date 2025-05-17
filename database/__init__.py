"""
Database package for the chat application
"""
# Import models for easy access
from database.models import db, User, Message, PrivateMessage

__all__ = ['db', 'User', 'Message', 'PrivateMessage'] 