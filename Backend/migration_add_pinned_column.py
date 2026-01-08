"""
Migration script to add is_reel_pinned column to scraped_reels table
Run this script once to update your existing database
"""
from sqlalchemy import text, inspect
from database import engine

def run_migration():
    """Add is_reel_pinned column to scraped_reels table"""
    try:
        print("Connecting to database...")

        # Create inspector to check if column exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('scraped_reels')]

        print("Checking if is_reel_pinned column exists...")

        if 'is_reel_pinned' in columns:
            print("[OK] Column 'is_reel_pinned' already exists. No migration needed.")
        else:
            print("Adding is_reel_pinned column to scraped_reels table...")
            with engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE scraped_reels
                    ADD COLUMN is_reel_pinned VARCHAR(3);
                """))
                conn.commit()
            print("[OK] Column 'is_reel_pinned' added successfully!")

        print("\n" + "="*60)
        print("[OK] Migration completed successfully!")
        print("="*60)
        return True

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Add is_reel_pinned Column")
    print("="*60)
    print()

    success = run_migration()

    if not success:
        print("\nPlease check your database connection settings.")
        print("If you need to manually run the migration:")
        print("  ALTER TABLE scraped_reels ADD COLUMN is_reel_pinned VARCHAR(3);")
