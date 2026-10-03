"""
Script to safely backup the database.
"""
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pms.config import DB_PATH

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        sys.exit(1)
        
    os.makedirs("backups", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"pharmacy_{timestamp}.db"
    backup_path = os.path.join("backups", backup_filename)
    
    # Safely backup using SQLite's backup API
    print(f"Backing up database to {backup_path}...")
    try:
        source_conn = sqlite3.connect(DB_PATH)
        dest_conn = sqlite3.connect(backup_path)
        
        with source_conn:
            source_conn.backup(dest_conn)
            
        dest_conn.close()
        source_conn.close()
        
        print(f"Backup successful: {backup_path}")
    except Exception as e:
        print(f"Backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
