"""
Phase 2 Testing Script
Tests account rotation, credit system, API endpoints, and scheduler
"""

import sys
from database import SessionLocal
from passlib.context import CryptContext
import models
from datetime import datetime, date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def print_header(title):
    """Print a formatted test header"""
    print("\n" + "=" * 60)
    print(f"TEST: {title}")
    print("=" * 60)


def print_result(success, message):
    """Print test result"""
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {message}")
    return success


def test_account_rotation():
    """Test 1: Account rotation logic"""
    print_header("Account Rotation System")

    db = SessionLocal()
    try:
        from account_rotation import get_least_used_account, increment_account_usage

        # Get least used account
        try:
            account = get_least_used_account(db)
            if account:
                print_result(True, f"Selected account: {account.username} (ID: {account.id})")
                print(f"     Daily count: {account.daily_scrape_count}")
                print(f"     Total scrapes: {account.total_scrapes}")

                # Test incrementing usage
                initial_count = account.daily_scrape_count
                increment_account_usage(db, account.id, 5)

                # Verify increment
                db.refresh(account)
                if account.daily_scrape_count == initial_count + 5:
                    return print_result(True, f"Usage incremented correctly: {initial_count} -> {account.daily_scrape_count}")
                else:
                    return print_result(False, f"Usage increment failed: expected {initial_count + 5}, got {account.daily_scrape_count}")
            else:
                return print_result(False, "No account returned (pool may be empty)")

        except Exception as e:
            return print_result(False, f"Account rotation failed: {str(e)}")

    finally:
        db.close()


def test_credit_system():
    """Test 2: Credit validation and deduction"""
    print_header("Credit System")

    db = SessionLocal()
    try:
        from credit_system import validate_scrape_request, deduct_credits, reset_user_credits

        # Get a test user
        user = db.query(models.User).first()
        if not user:
            return print_result(False, "No users in database for testing")

        print(f"Testing with user: {user.email} (ID: {user.id})")
        print(f"Current credits: {user.credits_used_today}/{user.daily_credit_limit}")

        # Test validation (should pass)
        is_valid, msg, remaining = validate_scrape_request(db, user.id, 10)
        if not is_valid:
            return print_result(False, f"Credit validation failed unexpectedly: {msg}")

        print_result(True, f"Credit validation passed. Remaining: {remaining}")

        # Test deduction
        initial_used = user.credits_used_today
        deduct_credits(db, user.id, 10)
        db.refresh(user)

        if user.credits_used_today == initial_used + 10:
            print_result(True, f"Credits deducted correctly: {initial_used} -> {user.credits_used_today}")
        else:
            return print_result(False, f"Credit deduction failed: expected {initial_used + 10}, got {user.credits_used_today}")

        # Test exceeding limit
        is_valid, msg, remaining = validate_scrape_request(db, user.id, 10000)
        if not is_valid:
            print_result(True, f"Correctly rejected excessive request: {msg}")
        else:
            return print_result(False, "Should have rejected request exceeding credit limit")

        # Test reset
        reset_user_credits(db, user.id)
        db.refresh(user)

        if user.credits_used_today == 0:
            return print_result(True, f"Credits reset successfully to 0")
        else:
            return print_result(False, f"Credit reset failed: {user.credits_used_today}")

    finally:
        db.close()


def test_api_key_creation():
    """Test 3: API key CRUD operations"""
    print_header("API Key Management")

    db = SessionLocal()
    try:
        from crud import create_api_key, get_all_api_keys

        # Create test API key
        test_key = "test_key_for_phase2"
        api_key_hash = pwd_context.hash(test_key)

        api_key = create_api_key(db, "Phase 2 Test Key", api_key_hash)

        if api_key and api_key.is_active:
            print_result(True, f"API key created: {api_key.key_name} (ID: {api_key.id})")
        else:
            return print_result(False, "Failed to create API key")

        # Test retrieval
        all_keys = get_all_api_keys(db)
        if any(k.id == api_key.id for k in all_keys):
            return print_result(True, f"API key retrieved successfully (Total keys: {len(all_keys)})")
        else:
            return print_result(False, "Failed to retrieve API key")

    finally:
        db.close()


def test_activity_logging():
    """Test 4: Activity logging"""
    print_header("Activity Logging System")

    db = SessionLocal()
    try:
        from crud import create_activity_log

        # Create test log
        log = create_activity_log(
            db=db,
            event_type="test_event",
            user_id=1,
            instagram_account_id=None,
            job_id="test_job_123",
            details={"test": "data", "phase": 2}
        )

        if log:
            print_result(True, f"Activity log created (ID: {log.id})")
            print(f"     Event type: {log.event_type}")
            print(f"     Details: {log.details}")

            # Verify retrieval
            retrieved = db.query(models.ActivityLog).filter(
                models.ActivityLog.id == log.id
            ).first()

            if retrieved and retrieved.details.get('phase') == 2:
                return print_result(True, "Activity log retrieved and verified")
            else:
                return print_result(False, "Activity log retrieval failed")
        else:
            return print_result(False, "Failed to create activity log")

    finally:
        db.close()


def test_instagram_account_management():
    """Test 5: Instagram account CRUD"""
    print_header("Instagram Account Management")

    db = SessionLocal()
    try:
        from crud import (
            get_instagram_account_by_id,
            update_instagram_account_cookies,
            get_all_instagram_accounts
        )

        # Get existing account
        account = db.query(models.InstagramAccount).first()
        if not account:
            return print_result(False, "No Instagram accounts in pool for testing")

        print_result(True, f"Testing with account: {account.username} (ID: {account.id})")

        # Test cookie update
        test_cookies = {
            "sessionid": "test_session_123",
            "csrftoken": "test_csrf_456"
        }
        cookie_string = "sessionid=test_session_123; csrftoken=test_csrf_456"

        update_instagram_account_cookies(
            db, account.id, test_cookies, cookie_string, "test_csrf_456"
        )

        # Verify update
        db.refresh(account)
        if account.cookie_string == cookie_string:
            print_result(True, "Cookies updated successfully")
        else:
            return print_result(False, "Cookie update failed")

        # Verify cookies_updated_at timestamp
        if account.cookies_updated_at:
            return print_result(True, f"Cookie timestamp updated: {account.cookies_updated_at}")
        else:
            return print_result(False, "Cookie timestamp not set")

    finally:
        db.close()


def test_scheduler_functions():
    """Test 6: Scheduler reset functions"""
    print_header("Daily Reset Functions")

    db = SessionLocal()
    try:
        from account_rotation import reset_daily_counts
        from credit_system import reset_all_daily_credits

        # Reset account daily counts
        accounts_reset = reset_daily_counts(db)
        print_result(True, f"Reset daily counts for {accounts_reset} Instagram account(s)")

        # Verify accounts were reset
        account = db.query(models.InstagramAccount).first()
        if account and account.daily_scrape_count == 0:
            print_result(True, f"Account {account.username} daily count reset to 0")
        else:
            print_result(False, "Account daily count not reset")

        # Reset user credits
        users_reset = reset_all_daily_credits(db)
        print_result(True, f"Reset credits for {users_reset} user(s)")

        # Verify user credits were reset
        user = db.query(models.User).first()
        if user and user.credits_used_today == 0 and user.last_credit_reset_date == date.today():
            return print_result(True, f"User {user.email} credits reset successfully")
        else:
            return print_result(False, "User credits not reset correctly")

    finally:
        db.close()


def test_job_creation_with_instagram_account():
    """Test 7: Job creation with Instagram account linkage"""
    print_header("Job Creation with Account Linkage")

    db = SessionLocal()
    try:
        from crud import create_job

        user = db.query(models.User).first()
        instagram_account = db.query(models.InstagramAccount).first()

        if not user or not instagram_account:
            return print_result(False, "Need both user and Instagram account for testing")

        # Create job with Instagram account
        job_id = f"test_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job = create_job(
            db=db,
            user_id=user.id,
            job_id=job_id,
            usernames=["test_user1", "test_user2"],
            reel_count=20,
            instagram_account_id=instagram_account.id
        )

        if job and job.instagram_account_id == instagram_account.id:
            print_result(True, f"Job created with Instagram account linkage")
            print(f"     Job ID: {job.job_id}")
            print(f"     Instagram Account: {instagram_account.username}")
            return print_result(True, "Job-Account linkage verified")
        else:
            return print_result(False, "Job creation or linkage failed")

    finally:
        db.close()


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "=" * 60)
    print("PHASE 2 TESTING - ENHANCED FEATURES")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        ("Account Rotation Logic", test_account_rotation),
        ("Credit System", test_credit_system),
        ("API Key Management", test_api_key_creation),
        ("Activity Logging", test_activity_logging),
        ("Instagram Account Management", test_instagram_account_management),
        ("Daily Reset Functions", test_scheduler_functions),
        ("Job-Account Linkage", test_job_creation_with_instagram_account),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_result(False, f"Test crashed: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print("=" * 60)
    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("[OK] All tests PASSED!")
    else:
        print(f"[FAIL] {total - passed} test(s) FAILED")

    print("=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
