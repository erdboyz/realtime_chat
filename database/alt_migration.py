"""
Alternative migration script using SQLAlchemy's declarative API
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
from sqlalchemy import Column, String, Boolean
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database_alternative():
    """
    Alternative migration method using declarative SQLAlchemy API
    """
    with app.app_context():
        logger.info("Starting alternative database migration...")
        
        try:
            # Check if we need to add the encryption_salt column to User
            inspector = db.inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            pm_columns = [col['name'] for col in inspector.get_columns('private_message')]
            
            # Add encryption_salt to User if it doesn't exist
            if 'encryption_salt' not in user_columns:
                logger.info("Adding encryption_salt column to User table using declarative API")
                # Add column to model
                column = Column('encryption_salt', String(64), default=lambda: base64.urlsafe_b64encode(os.urandom(32)).decode())
                column_name = 'encryption_salt'
                
                # Get the table
                table = User.__table__
                
                # Create column
                column.key = column_name
                column.name = column_name
                column._set_parent(table)
                
                # Create the column in the database
                db.engine.execute(f'ALTER TABLE {table.name} ADD COLUMN {column_name} VARCHAR(64)')
                
                # Update all existing users with a random salt
                users = User.query.all()
                for user in users:
                    user.encryption_salt = base64.urlsafe_b64encode(os.urandom(32)).decode()
                
                logger.info(f"Added encryption salt to {len(users)} users")
            
            # Add is_encrypted column to PrivateMessage if it doesn't exist
            if 'is_encrypted' not in pm_columns:
                logger.info("Adding is_encrypted column to PrivateMessage table using declarative API")
                # Add column to model
                column = Column('is_encrypted', Boolean(), default=False)
                column_name = 'is_encrypted'
                
                # Get the table
                table = PrivateMessage.__table__
                
                # Create column
                column.key = column_name
                column.name = column_name
                column._set_parent(table)
                
                # Create the column in the database - use the right SQL for SQLite
                db.engine.execute(f'ALTER TABLE {table.name} ADD COLUMN {column_name} BOOLEAN DEFAULT FALSE')
                
                # Mark existing messages as not encrypted
                existing_messages = PrivateMessage.query.all()
                for message in existing_messages:
                    message.is_encrypted = False
                
                logger.info(f"Set encryption status on {len(existing_messages)} existing messages")
            
            db.session.commit()
            logger.info("Alternative migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Alternative migration failed: {str(e)}")
            
            # Provide helpful error message
            if isinstance(e, OperationalError) and 'no such column' in str(e).lower():
                logger.error("This appears to be a column access error. The model has been updated but the database schema hasn't been updated yet.")
                logger.error("Try running the following commands manually in a SQLite shell:")
                logger.error("1. ALTER TABLE user ADD COLUMN encryption_salt VARCHAR(64);")
                logger.error("2. ALTER TABLE private_message ADD COLUMN is_encrypted BOOLEAN DEFAULT FALSE;")
            raise

if __name__ == '__main__':
    migrate_database_alternative() 