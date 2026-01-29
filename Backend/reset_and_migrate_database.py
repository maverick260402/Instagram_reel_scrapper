#!/usr/bin/env python3
"""
Database Reset and Migration Script
====================================
This script:
1. Drops all existing tables (clean slate)
2. Runs 000_base_schema.sql (core tables)
3. Runs 001_multi_user_system.sql (Phase 1 features)
4. Verifies all tables exist

⚠️ WARNING: This will DELETE ALL DATA in the database!
Only use this for fresh setup or complete reset.
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from config import settings

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(message)
    print("=" * 70 + "\n")

def print_step(step_num, message):
    """Print a formatted step"""
    print(f"[STEP {step_num}] {message}")

def print_success(message):
    """Print success message"""
    print(f"✓ {message}")

def print_error(message):
    """Print error message"""
    print(f"✗ {message}")

def confirm_reset():
    """Ask user to confirm database reset"""
    print_header("⚠️  DATABASE RESET WARNING")
    print("This script will:")
    print("  1. DROP ALL existing tables")
    print("  2. DELETE ALL data")
    print("  3. Create fresh schema")
    print("  4. Run migrations")
    print("\nThis action CANNOT be undone!\n")

    response = input("Type 'RESET' to confirm, or anything else to cancel: ")
    return response == "RESET"

def drop_all_tables(engine):
    """Drop all tables in the database"""
    print_step(1, "Dropping all existing tables...")

    with engine.connect() as conn:
        # Get all table names
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        tables = [row[0] for row in result]

        if not tables:
            print("  No tables to drop.")
            return

        print(f"  Found {len(tables)} tables to drop:")
        for table in tables:
            print(f"    - {table}")

        # Drop all tables with CASCADE
        for table in tables:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                print(f"  ✓ Dropped: {table}")
            except Exception as e:
                print(f"  ✗ Failed to drop {table}: {e}")

        conn.commit()

    print_success("All tables dropped successfully\n")

def run_sql_file(engine, file_path):
    """Execute a SQL file"""
    if not os.path.exists(file_path):
        print_error(f"SQL file not found: {file_path}")
        return False

    print(f"  Executing: {os.path.basename(file_path)}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        with engine.connect() as conn:
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]

            for i, statement in enumerate(statements):
                if statement:
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        # Some errors are expected (e.g., "already exists")
                        if "already exists" not in str(e):
                            print(f"    Warning: {str(e)[:100]}")

            conn.commit()

        print_success(f"Executed {os.path.basename(file_path)}")
        return True

    except Exception as e:
        print_error(f"Failed to execute {file_path}: {e}")
        return False

def verify_tables(engine):
    """Verify all expected tables exist"""
    print_step(4, "Verifying database schema...")

    expected_tables = [
        'users',
        'user_groups',
        'scraping_jobs',
        'scraped_reels',
        'activity_logs',
        'instagram_accounts',
        'api_keys',
        'admin_users'
    ]

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """))
        existing_tables = [row[0] for row in result]

    print(f"\n  Expected: {len(expected_tables)} tables")
    print(f"  Found:    {len(existing_tables)} tables\n")

    all_exist = True
    for table in expected_tables:
        if table in existing_tables:
            print(f"  ✓ {table}")
        else:
            print(f"  ✗ {table} (MISSING)")
            all_exist = False

    if all_exist:
        print_success(f"\nAll {len(expected_tables)} tables verified successfully!")
        return True
    else:
        print_error("\nSome tables are missing!")
        return False

def main():
    """Main execution"""
    print_header("DATABASE RESET AND MIGRATION TOOL")

    # Confirm reset
    if not confirm_reset():
        print("\n❌ Reset cancelled by user.")
        sys.exit(0)

    try:
        # Create engine
        print("\nConnecting to database...")
        engine = create_engine(settings.DATABASE_URL)
        print_success("Connected to database\n")

        # Step 1: Drop all tables
        drop_all_tables(engine)

        # Step 2: Run base schema
        print_step(2, "Creating base schema...")
        migrations_dir = Path(__file__).parent / "migrations"
        base_schema = migrations_dir / "000_base_schema.sql"

        if not run_sql_file(engine, base_schema):
            print_error("Failed to create base schema")
            sys.exit(1)
        print()

        # Step 3: Run Phase 1 migration
        print_step(3, "Running Phase 1 migration...")
        phase1_migration = migrations_dir / "001_multi_user_system.sql"

        if not run_sql_file(engine, phase1_migration):
            print_error("Failed to run Phase 1 migration")
            sys.exit(1)
        print()

        # Step 4: Verify
        if verify_tables(engine):
            print_header("✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
            print("\nNext steps:")
            print("  1. Start the backend server: python app.py")
            print("  2. Create admin user if needed")
            print("  3. Add Instagram accounts to the pool")
            print("  4. Generate API keys for cookie updates")
        else:
            print_header("⚠️  MIGRATION COMPLETED WITH WARNINGS")
            print("\nSome tables may be missing. Check the logs above.")
            sys.exit(1)

    except Exception as e:
        print_error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
