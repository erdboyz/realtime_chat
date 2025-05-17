"""
Run this script to apply the database migration for encrypted messages.
"""
import sys
import os
import logging
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Run database migrations for the chat application.')
    parser.add_argument('--method', type=str, default='standard',
                        choices=['standard', 'alternative', 'direct'],
                        help='Migration method to use: standard, alternative, or direct')
    parser.add_argument('--check', action='store_true',
                        help='Check database status after migration')
    parser.add_argument('--db-path', type=str, default='instance/chat.db',
                        help='Path to the SQLite database (only used with direct method)')
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting database migration using {args.method} method...")
        
        # Run the selected migration method
        if args.method == 'standard':
            from database.migration import migrate_database
            migrate_database()
        elif args.method == 'alternative':
            from database.alt_migration import migrate_database_alternative
            migrate_database_alternative()
        elif args.method == 'direct':
            from database.direct_sql import direct_sql_migration
            direct_sql_migration(db_path=args.db_path)
            
        logger.info("Migration completed successfully.")
        
        # Check database status if requested
        if args.check:
            from database.check_db import check_database
            check_database()
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)
        
    logger.info("All done!") 