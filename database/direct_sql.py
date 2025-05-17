"""
Direct SQL migration - use this if other approaches fail
"""
import sqlite3
import os
import logging
import base64
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def direct_sql_migration(db_path='instance/chat.db'):
    """Execute SQL directly against the SQLite database"""
    logger.info(f"Applying direct SQL migration to {db_path}")
    
    try:
        # Check if the database file exists
        if not os.path.exists(db_path):
            logger.error(f"Database file not found at: {db_path}")
            return
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing columns for User table
        cursor.execute("PRAGMA table_info(user)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        # Get existing columns for private_message table
        cursor.execute("PRAGMA table_info(private_message)")
        pm_columns = [col[1] for col in cursor.fetchall()]
        
        # Add encryption_salt column to User if it doesn't exist
        if 'encryption_salt' not in user_columns:
            logger.info("Adding encryption_salt column to User table")
            cursor.execute("ALTER TABLE user ADD COLUMN encryption_salt VARCHAR(64)")
            
            # Update all users with a random salt
            cursor.execute("SELECT id FROM user")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            for user_id in user_ids:
                salt = base64.urlsafe_b64encode(os.urandom(32)).decode()
                cursor.execute("UPDATE user SET encryption_salt = ? WHERE id = ?", (salt, user_id))
            
            logger.info(f"Added encryption salt to {len(user_ids)} users")
        
        # Add is_encrypted column to PrivateMessage if it doesn't exist
        if 'is_encrypted' not in pm_columns:
            logger.info("Adding is_encrypted column to PrivateMessage table")
            cursor.execute("ALTER TABLE private_message ADD COLUMN is_encrypted BOOLEAN DEFAULT 0")
            
            # Update all existing messages to be non-encrypted
            cursor.execute("UPDATE private_message SET is_encrypted = 0 WHERE is_encrypted IS NULL")
            
            # Change body column to TEXT (SQLite treats all text as TEXT anyway, but for consistency)
            if 'body' in pm_columns:
                logger.info("SQLite doesn't need explicit column type changes; 'body' column is already compatible with TEXT")
        
        conn.commit()
        conn.close()
        logger.info("Direct SQL migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Direct SQL migration failed: {str(e)}")
        raise

if __name__ == '__main__':
    logger.info("Running direct SQL migration...")
    direct_sql_migration()
    logger.info("Direct SQL migration completed.") 