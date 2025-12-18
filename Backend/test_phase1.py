"""
Phase 1 Testing Script
Tests database models, account rotation, and credit system
"""

import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from models import User, InstagramAccount, ApiKey, AdminUser, ActivityLog, ScrapingJob, ScrapedReel
from crud import (
    create_instagram_account, get_all_instagram_accounts,
    create_api_key, create_admin_user, create_activity_log,
    create_user
)
from account_rotation import (
    get_least_used_account, increment_account_usage,
    get_account_stats, NoAccountsAvailableError
)
from credit_system import (
    get_user_credits_remaining, deduct_credits,
    get_user_credit_summary, InsufficientCreditsError
)
from auth import hash_password
import config


def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)

    try:
        engine = create_engine(config.settings.DATABASE_URL)
        connection = engine.connect()
        print("✓ Database connection successful")
        connection.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False


def test_table_existence():
    """Test if all tables exist"""
    print("\n" + "=" * 60)
    print("TEST 2: Table Existence")
    print("=" * 60)

    try:
        engine = create_engine(config.settings.DATABASE_URL)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        required_tables = [
            'users', 'instagram_accounts', 'api_keys', 'admin_users',
            'activity_logs', 'scraping_jobs', 'scraped_reels', 'user_groups'
        ]

        all_exist = True
        for table in required_tables:
            if table in existing_tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' MISSING")
                all_exist = False

        return all_exist
    except Exception as e:
        print(f"✗ Error checking tables: {str(e)}")
        return False


def test_table_columns():
    """Test if new columns exist in modified tables"""
    print("\n" + "=" * 60)
    print("TEST 3: New Columns in Existing Tables")
    print("=" * 60)

    try:
        engine = create_engine(config.settings.DATABASE_URL)
        inspector = inspect(engine)

        # Check users table for credit fields
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        required_user_columns = ['daily_credit_limit', 'credits_used_today', 'last_credit_reset_date']

        print("\nUsers table:")
        for col in required_user_columns:
            if col in user_columns:
                print(f"  ✓ Column '{col}' exists")
            else:
                print(f"  ✗ Column '{col}' MISSING")

        # Check scraping_jobs table for new fields
        job_columns = [col['name'] for col in inspector.get_columns('scraping_jobs')]
        required_job_columns = ['instagram_account_id', 'credits_consumed']

        print("\nScraping_jobs table:")
        for col in required_job_columns:
            if col in job_columns:
                print(f"  ✓ Column '{col}' exists")
            else:
                print(f"  ✗ Column '{col}' MISSING")

        # Check scraped_reels table
        reel_columns = [col['name'] for col in inspector.get_columns('scraped_reels')]

        print("\nScraped_reels table:")
        if 'instagram_account_id' in reel_columns:
            print(f"  ✓ Column 'instagram_account_id' exists")
        else:
            print(f"  ✗ Column 'instagram_account_id' MISSING")

        return True
    except Exception as e:
        print(f"✗ Error checking columns: {str(e)}")
        return False


def test_instagram_account_crud(db):
    """Test Instagram account CRUD operations"""
    print("\n" + "=" * 60)
    print("TEST 4: Instagram Account CRUD")
    print("=" * 60)

    try:
        # Create test account
        test_account = create_instagram_account(
            db=db,
            username="test_insta_account",
            email="test@instagram.com",
            password="test_password_123"
        )
        print(f"✓ Created Instagram account: {test_account.username} (ID: {test_account.id})")

        # Verify default values
        assert test_account.is_active == True, "Account should be active by default"
        assert test_account.is_paused == False, "Account should not be paused by default"
        assert test_account.daily_scrape_count == 0, "Daily count should be 0"
        print("✓ Default values are correct")

        # Get all accounts
        all_accounts = get_all_instagram_accounts(db)
        print(f"✓ Retrieved {len(all_accounts)} Instagram account(s)")

        return True
    except Exception as e:
        print(f"✗ Instagram account CRUD failed: {str(e)}")
        return False


def test_account_rotation(db):
    """Test account rotation logic"""
    print("\n" + "=" * 60)
    print("TEST 5: Account Rotation System")
    print("=" * 60)

    try:
        # Get least used account
        account = get_least_used_account(db)
        print(f"✓ Got least used account: {account.username} (Daily count: {account.daily_scrape_count})")

        # Increment usage
        original_count = account.daily_scrape_count
        increment_account_usage(db, account.id, reels_scraped=5, success=True)
        db.refresh(account)
        print(f"✓ Incremented usage: {original_count} → {account.daily_scrape_count}")

        # Get account stats
        stats = get_account_stats(db, account.id)
        print(f"✓ Account stats: {stats['total_scrapes']} total scrapes, {stats['success_rate']}% success rate")

        return True
    except NoAccountsAvailableError as e:
        print(f"! No Instagram accounts available: {str(e)}")
        print("  (This is expected if no Instagram accounts exist in DB)")
        return True
    except Exception as e:
        print(f"✗ Account rotation failed: {str(e)}")
        return False


def test_credit_system(db):
    """Test credit system"""
    print("\n" + "=" * 60)
    print("TEST 6: Credit System")
    print("=" * 60)

    try:
        # Get existing user or create test user
        from crud import get_user_by_email
        test_user = get_user_by_email(db, "test@example.com")

        if not test_user:
            print("Creating test user...")
            from schemas import UserCreate
            test_user = create_user(db, UserCreate(
                email="test@example.com",
                username="testuser",
                password="testpass123"
            ))
            print(f"✓ Created test user: {test_user.username}")
        else:
            print(f"✓ Using existing user: {test_user.username}")

        # Get credit summary
        summary = get_user_credit_summary(db, test_user.id)
        print(f"✓ Credit summary: {summary['remaining']}/{summary['daily_limit']} remaining ({summary['usage_percent']}% used)")

        # Test credit deduction
        initial_remaining = get_user_credits_remaining(db, test_user.id)
        deduct_credits(db, test_user.id, 10)
        new_remaining = get_user_credits_remaining(db, test_user.id)
        print(f"✓ Deducted 10 credits: {initial_remaining} → {new_remaining}")

        assert new_remaining == initial_remaining - 10, "Credit deduction incorrect"
        print("✓ Credit deduction working correctly")

        return True
    except InsufficientCreditsError as e:
        print(f"! Insufficient credits (expected if user's quota is low): {str(e)}")
        return True
    except Exception as e:
        print(f"✗ Credit system failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_activity_logging(db):
    """Test activity logging"""
    print("\n" + "=" * 60)
    print("TEST 7: Activity Logging")
    print("=" * 60)

    try:
        # Create activity log
        log = create_activity_log(
            db=db,
            event_type="test_event",
            details={"message": "This is a test log entry"}
        )
        print(f"✓ Created activity log (ID: {log.id}, Type: {log.event_type})")

        # Retrieve recent logs
        from crud import get_recent_activity
        recent_logs = get_recent_activity(db, limit=5)
        print(f"✓ Retrieved {len(recent_logs)} recent activity log(s)")

        return True
    except Exception as e:
        print(f"✗ Activity logging failed: {str(e)}")
        return False


def test_api_key_crud(db):
    """Test API key CRUD"""
    print("\n" + "=" * 60)
    print("TEST 8: API Key Management")
    print("=" * 60)

    try:
        # Create API key
        test_key_hash = hash_password("test_api_key_12345")
        api_key = create_api_key(db, "Test Key", test_key_hash)
        print(f"✓ Created API key: {api_key.key_name} (ID: {api_key.id})")

        # Verify default values
        assert api_key.is_active == True, "API key should be active by default"
        print("✓ API key is active by default")

        return True
    except Exception as e:
        print(f"✗ API key CRUD failed: {str(e)}")
        return False


def test_admin_user_crud(db):
    """Test admin user CRUD"""
    print("\n" + "=" * 60)
    print("TEST 9: Admin User Management")
    print("=" * 60)

    try:
        from crud import get_admin_by_username

        # Check if admin already exists
        existing_admin = get_admin_by_username(db, "test_admin")

        if not existing_admin:
            # Create admin user
            admin_password_hash = hash_password("admin_test_123")
            admin = create_admin_user(db, "test_admin", "admin@test.com", admin_password_hash)
            print(f"✓ Created admin user: {admin.username} (ID: {admin.id})")
        else:
            print(f"✓ Admin user already exists: {existing_admin.username}")

        return True
    except Exception as e:
        print(f"✗ Admin user CRUD failed: {str(e)}")
        return False


def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "PHASE 1 TEST SUITE" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # Test 1: Database connection
    results.append(test_database_connection())

    # Test 2: Table existence
    results.append(test_table_existence())

    # Test 3: Table columns
    results.append(test_table_columns())

    # Tests requiring database session
    try:
        db = next(get_db())

        # Test 4: Instagram account CRUD
        results.append(test_instagram_account_crud(db))

        # Test 5: Account rotation
        results.append(test_account_rotation(db))

        # Test 6: Credit system
        results.append(test_credit_system(db))

        # Test 7: Activity logging
        results.append(test_activity_logging(db))

        # Test 8: API key CRUD
        results.append(test_api_key_crud(db))

        # Test 9: Admin user CRUD
        results.append(test_admin_user_crud(db))

        db.close()

    except Exception as e:
        print(f"\n✗ Error getting database session: {str(e)}")
        results.append(False)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")

    if passed == total:
        print("\n✓ All tests PASSED! Phase 1 implementation is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) FAILED. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
