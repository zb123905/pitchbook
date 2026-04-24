"""
PostgreSQL Database Connection Test Script

Remote Database Info:
- Host: 43.137.10.188
- Port: 5432
- User: edit_user
- Password: Suibe_edit
- Database: vcpe_pitchbook
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from database.base import DatabaseManager, DatabaseConfig
from database.models import Base

def test_connection():
    """Test database connection and create tables"""

    # Set database connection
    config.DB_ENABLED = True
    config.DB_HOST = "43.137.10.188"
    config.DB_PORT = 5432
    config.DB_NAME = "vcpe_pitchbook"
    config.DB_USER = "edit_user"
    config.DB_PASSWORD = "Suibe_edit"

    # Recompute DB_URL after setting config values
    config.DB_URL = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

    print("=" * 50)
    print("PostgreSQL Database Connection Test")
    print("=" * 50)
    print(f"Host: {config.DB_HOST}")
    print(f"Port: {config.DB_PORT}")
    print(f"Database: {config.DB_NAME}")
    print(f"User: {config.DB_USER}")
    print("=" * 50)

    # Create database manager
    db_config = DatabaseConfig.from_config(config)
    db_manager = DatabaseManager(db_config)

    # Test connection
    print("\n[1/3] Connecting to database...")
    if db_manager.connect():
        print("[OK] Database connected successfully!")

        # Test basic query
        print("\n[2/3] Testing query...")
        if db_manager.test_connection():
            print("[OK] Query test passed!")
        else:
            print("[FAIL] Query test failed!")
            db_manager.disconnect()
            return False

        # Create tables
        print("\n[3/3] Creating database tables...")
        if db_manager.create_tables(Base):
            print("[OK] Database tables created successfully!")
            print("\nTables created:")
            print("  - emails               (Email main table)")
            print("  - email_links          (Email links)")
            print("  - email_attachments    (Email attachments)")
            print("  - downloaded_reports   (Downloaded reports)")
            print("  - extracted_content    (Extracted content)")
            print("  - analysis_results     (Analysis results)")
            print("  - scraped_web_content  (Scraped web content)")
            print("  - market_overviews     (Market overviews)")
            print("  - processing_logs      (Processing logs)")
        else:
            print("[FAIL] Failed to create database tables!")

        db_manager.disconnect()
        return True
    else:
        print("[FAIL] Database connection failed!")
        print("\nPossible reasons:")
        print("  1. Database server not running")
        print("  2. Network connection issue (firewall/security group)")
        print("  3. Database 'vcpe_pitchbook' does not exist")
        print("  4. Wrong username or password")
        print("  5. PostgreSQL not allowing remote connections")
        return False

if __name__ == "__main__":
    success = test_connection()
    print("\n" + "=" * 50)
    if success:
        print("[OK] All tests passed! Database configured.")
        print("\nNext step: Enable database in GUI")
    else:
        print("[FAIL] Test failed! Please check configuration.")
    print("=" * 50)

    sys.exit(0 if success else 1)
