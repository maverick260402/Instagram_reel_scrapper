"""
Database setup script - Creates database, user, and tables
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import getpass

# Database configuration
DB_NAME = "instagram_scraper"
DB_USER = "scraper_user"
DB_PASSWORD = "scraper_password_123"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database_and_user(postgres_password):
    """Connect to PostgreSQL and create database and user"""
    try:
        # Connect to default postgres database
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=postgres_password,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (DB_USER,))
        user_exists = cur.fetchone()

        if not user_exists:
            print(f"Creating user '{DB_USER}'...")
            cur.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                sql.Identifier(DB_USER)
            ), (DB_PASSWORD,))
            print(f"✓ User '{DB_USER}' created")
        else:
            print(f"✓ User '{DB_USER}' already exists")
            # Update password just in case
            cur.execute(sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                sql.Identifier(DB_USER)
            ), (DB_PASSWORD,))
            print(f"✓ Password updated for user '{DB_USER}'")

        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
        db_exists = cur.fetchone()

        if not db_exists:
            print(f"Creating database '{DB_NAME}'...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_NAME)
            ))
            print(f"✓ Database '{DB_NAME}' created")
        else:
            print(f"✓ Database '{DB_NAME}' already exists")

        # Grant privileges on database
        cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
            sql.Identifier(DB_NAME),
            sql.Identifier(DB_USER)
        ))
        print(f"✓ Database privileges granted to '{DB_USER}'")

        cur.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print("\n❌ Error: Could not connect to PostgreSQL")
            print("Please provide the PostgreSQL 'postgres' user password")
            return False
        else:
            print(f"\n❌ Error: {e}")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def grant_schema_permissions(postgres_password):
    """Grant schema permissions to the user (required for PostgreSQL 15+)"""
    try:
        print(f"\nGranting schema permissions to '{DB_USER}'...")
        # Connect to the instagram_scraper database as postgres
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user="postgres",
            password=postgres_password,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Grant schema permissions (required for PostgreSQL 15+)
        cur.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(
            sql.Identifier(DB_USER)
        ))
        cur.execute(sql.SQL("GRANT CREATE ON SCHEMA public TO {}").format(
            sql.Identifier(DB_USER)
        ))

        # Grant usage and create on schema
        cur.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {}").format(
            sql.Identifier(DB_USER)
        ))
        cur.execute(sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {}").format(
            sql.Identifier(DB_USER)
        ))

        print(f"✓ Schema permissions granted to '{DB_USER}'")

        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error granting schema permissions: {e}")
        return False

def test_connection():
    """Test connection with the new user"""
    try:
        print(f"\nTesting connection as '{DB_USER}'...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✓ Successfully connected to PostgreSQL")
        print(f"  Version: {version[0][:50]}...")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

def create_tables():
    """Create database tables using SQLAlchemy models"""
    try:
        print("\nCreating database tables...")
        from database import init_db
        init_db()
        print("✓ All tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Instagram Scraper - Database Setup")
    print("="*60)

    # Prompt for PostgreSQL password
    print("\nPlease enter the PostgreSQL 'postgres' user password:")
    postgres_password = getpass.getpass("Password: ")

    # Step 1: Create database and user
    if not create_database_and_user(postgres_password):
        print("\nPlease run this script with PostgreSQL 'postgres' user credentials")
        print("   Or create the database and user manually:")
        print(f"   CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';")
        print(f"   CREATE DATABASE {DB_NAME};")
        print(f"   GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")
        sys.exit(1)

    # Step 2: Grant schema permissions (PostgreSQL 15+ requirement)
    if not grant_schema_permissions(postgres_password):
        print("\nWarning: Could not grant schema permissions automatically")
        print("You may need to run these SQL commands manually:")
        print(f"   \\c {DB_NAME}")
        print(f"   GRANT ALL ON SCHEMA public TO {DB_USER};")
        print(f"   GRANT CREATE ON SCHEMA public TO {DB_USER};")
        sys.exit(1)

    # Step 3: Test connection
    if not test_connection():
        sys.exit(1)

    # Step 4: Create tables
    if not create_tables():
        sys.exit(1)

    print("\n" + "="*60)
    print("✓ Database setup completed successfully!")
    print("="*60)
    print("\nYou can now start the application with:")
    print("  python app.py")
    print("\nThe server will be available at: http://127.0.0.1:8888")
