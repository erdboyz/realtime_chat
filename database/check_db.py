"""
A helper script to check the database status after migration
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from database.models import User, PrivateMessage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Check database for encryption status"""
    with app.app_context():
        logger.info("Checking database encryption status...")
        
        # Check if User has encryption_salt column
        try:
            # Count users with and without salt
            total_users = User.query.count()
            users_with_salt = User.query.filter(User.encryption_salt.isnot(None)).count()
            
            logger.info(f"Total users: {total_users}")
            logger.info(f"Users with encryption salt: {users_with_salt}")
            
            if total_users > 0 and users_with_salt == total_users:
                logger.info("✅ All users have encryption salts")
            else:
                logger.warning("⚠️ Some users are missing encryption salts")
                
            # Check private messages
            total_messages = PrivateMessage.query.count()
            encrypted_messages = PrivateMessage.query.filter_by(is_encrypted=True).count()
            non_encrypted_messages = PrivateMessage.query.filter_by(is_encrypted=False).count()
            
            logger.info(f"Total private messages: {total_messages}")
            logger.info(f"Encrypted messages: {encrypted_messages}")
            logger.info(f"Non-encrypted messages: {non_encrypted_messages}")
            
            # Check for NULL is_encrypted values
            null_encryption = PrivateMessage.query.filter(PrivateMessage.is_encrypted.is_(None)).count()
            if null_encryption > 0:
                logger.warning(f"⚠️ {null_encryption} messages have NULL is_encrypted value")
            
            # Database structure info
            inspector = db.inspect(db.engine)
            
            # Output columns for user table
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            logger.info(f"User table columns: {', '.join(user_columns)}")
            
            # Output columns for private_message table
            pm_columns = [col['name'] for col in inspector.get_columns('private_message')]
            logger.info(f"PrivateMessage table columns: {', '.join(pm_columns)}")
            
            logger.info("Database check completed.")
            
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            raise

if __name__ == "__main__":
    logger.info("Running database check...")
    check_database()
    logger.info("Database check completed.") 