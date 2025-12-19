"""
Run database migrations
"""

import psycopg2
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'dbname': 'instagram_scraper',
    'user': 'scraper_user',
    'password': 'scraper_password_123',
    'host': 'localhost',
    'port': 5432
}

def run_migration(migration_file):
    """Run a SQL migration file"""
    print(f"\n{'='*70}")
    print(f"Running migration: {migration_file}")
    print(f"{'='*70}\n")

    # Read migration SQL
    sql_path = Path(__file__).parent / migration_file
    if not sql_path.exists():
        print(f"[ERROR] Migration file not found: {sql_path}")
        return False

    with open(sql_path, 'r') as f:
        sql = f.read()

    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()

        # Execute migration
        print("[1/2] Executing SQL migration...")
        cursor.execute(sql)

        print("[2/2] Migration completed successfully!")
        print(f"\n{'='*70}")
        print("MIGRATION SUCCESSFUL")
        print(f"{'='*70}\n")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file>")
        print("Example: python run_migration.py migrations/002_phase3_indexes_views.sql")
        sys.exit(1)

    migration_file = sys.argv[1]
    success = run_migration(migration_file)

    sys.exit(0 if success else 1)
