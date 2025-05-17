"""
Database migration module for adding encryption support
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from database.models import User, PrivateMessage
import base64
import os
import logging
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """
    Migration script to update the database schema for encrypted messages
    """
    with app.app_context():
        logger.info("Starting database migration for encryption...")
        
        try:
            # Check if we need to add the encryption_salt column to User
            inspector = db.inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            pm_columns = [col['name'] for col in inspector.get_columns('private_message')]
            
            # Add encryption_salt to User if it doesn't exist
            if 'encryption_salt' not in user_columns:
                logger.info("Adding encryption_salt column to User table")
                try:
                    # SQLite way (more compatible)
                    db.session.execute(text('ALTER TABLE user ADD COLUMN encryption_salt VARCHAR(64);'))
                except OperationalError:
                    logger.info("Standard ALTER TABLE failed, trying with SQLAlchemy")
                    # Roll back any partial changes
                    db.session.rollback()
                    
                    # Use SQLAlchemy Core to add the column
                    with db.engine.begin() as conn:
                        conn.execute(text('ALTER TABLE user ADD COLUMN encryption_salt VARCHAR(64)'))
                
                # Update all existing users with a random salt
                users = User.query.all()
                for user in users:
                    if not user.encryption_salt:
                        user.encryption_salt = base64.urlsafe_b64encode(os.urandom(32)).decode()
                
                logger.info(f"Added encryption salt to {len(users)} users")
            
            # Add is_encrypted column to PrivateMessage if it doesn't exist
            if 'is_encrypted' not in pm_columns:
                logger.info("Adding is_encrypted column to PrivateMessage table")
                try:
                    db.session.execute(text('ALTER TABLE private_message ADD COLUMN is_encrypted BOOLEAN DEFAULT FALSE;'))
                except OperationalError:
                    logger.info("Standard ALTER TABLE failed, trying with SQLAlchemy")
                    # Roll back any partial changes
                    db.session.rollback()
                    
                    # Use SQLAlchemy Core to add the column
                    with db.engine.begin() as conn:
                        conn.execute(text('ALTER TABLE private_message ADD COLUMN is_encrypted BOOLEAN DEFAULT FALSE'))
            
            # Mark existing messages as not encrypted initially
            existing_messages = PrivateMessage.query.filter_by(is_encrypted=None).all()
            if existing_messages:
                logger.info(f"Updating {len(existing_messages)} existing private messages")
                for message in existing_messages:
                    message.is_encrypted = False
            
            db.session.commit()
            logger.info("Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_database() 