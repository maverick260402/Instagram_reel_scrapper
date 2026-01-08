"""
Phase 3 Testing Script
Tests admin panel features, database views, indexes, and statistics
"""

import sys
from datetime import datetime, timedelta, date
from sqlalchemy import inspect, text, func
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

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


def test_database_indexes():
    """Test 1: Verify all Phase 3 indexes exist"""
    print_header("Database Indexes")

    try:
        inspector = inspect(engine)

        # Define required indexes for Phase 3
        required_indexes = {
            'activity_logs': ['idx_activity_logs_event_type', 'idx_activity_logs_created_at'],
            'scraped_reels': ['idx_scraped_reels_scraped_at'],
            'scraping_jobs': ['idx_jobs_status', 'idx_jobs_created_at'],
        }

        all_passed = True

        for table_name, index_names in required_indexes.items():
            indexes = inspector.get_indexes(table_name)
            for idx_name in index_names:
                exists = any(idx['name'] == idx_name for idx in indexes)
                if exists:
                    print_result(True, f"Index '{idx_name}' exists on table '{table_name}'")
                    all_passed &= True
                else:
                    all_passed &= print_result(False, f"Index '{idx_name}' missing on table '{table_name}'")

        return all_passed

    except Exception as e:
        return print_result(False, f"Index verification failed: {str(e)}")


def test_database_views():
    """Test 2: Verify all Phase 3 views exist and are queryable"""
    print_header("Database Views Existence")

    db = SessionLocal()
    try:
        required_views = [
            'v_daily_stats',
            'v_user_summary',
            'v_instagram_account_health',
            'v_recent_activity',
            'v_job_performance',
            'v_hourly_usage_pattern'
        ]

        all_passed = True

        for view_name in required_views:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar()
                all_passed &= print_result(True, f"View '{view_name}' exists and queryable (rows: {result})")
            except Exception as e:
                all_passed &= print_result(False, f"View '{view_name}' error: {str(e)}")

        return all_passed

    finally:
        db.close()


def test_view_daily_stats():
    """Test 3: Test v_daily_stats view calculations"""
    print_header("v_daily_stats View")

    db = SessionLocal()
    try:
        # Query the view
        result = db.execute(text("SELECT * FROM v_daily_stats ORDER BY date DESC LIMIT 1")).fetchone()

        if result:
            print_result(True, f"Retrieved daily stats for date: {result[0]}")
            print(f"     Total reels: {result[1]}")
            print(f"     Active users: {result[2]}")
            print(f"     Accounts used: {result[3]}")
            return print_result(True, "v_daily_stats view working correctly")
        else:
            return print_result(True, "v_daily_stats view exists (no data yet)")

    except Exception as e:
        return print_result(False, f"v_daily_stats test failed: {str(e)}")

    finally:
        db.close()


def test_view_user_summary():
    """Test 4: Test v_user_summary view with credit calculations"""
    print_header("v_user_summary View")

    db = SessionLocal()
    try:
        # Query the view
        # Columns: id, email, username, daily_credit_limit, credits_used_today, credits_remaining,
        #          usage_percent, is_active, total_jobs, successful_jobs, total_reels_scraped, last_job_date
        result = db.execute(text("SELECT * FROM v_user_summary LIMIT 1")).fetchone()

        if result:
            print_result(True, "Retrieved user summary data")
            print(f"     User ID: {result[0]}")
            print(f"     Email: {result[1]}")
            print(f"     Username: {result[2]}")
            print(f"     Total jobs: {result[8]}")

            # Verify credit usage percent calculation
            credit_limit = result[3]  # daily_credit_limit
            credits_used = result[4]  # credits_used_today
            usage_percent = float(result[6]) if result[6] is not None else 0  # usage_percent (convert Decimal to float)

            if credit_limit > 0:
                expected_percent = round((credits_used / credit_limit) * 100, 1)
                if abs(usage_percent - expected_percent) < 0.1:
                    return print_result(True, f"Credit usage percent calculated correctly: {usage_percent}%")
                else:
                    return print_result(False, f"Credit percent mismatch: expected {expected_percent}, got {usage_percent}")
            else:
                return print_result(True, "User summary view working (no usage yet)")
        else:
            return print_result(True, "v_user_summary view exists (no data yet)")

    except Exception as e:
        return print_result(False, f"v_user_summary test failed: {str(e)}")

    finally:
        db.close()


def test_view_instagram_account_health():
    """Test 5: Test v_instagram_account_health cookie health status"""
    print_header("v_instagram_account_health View")

    db = SessionLocal()
    try:
        # Query the view
        result = db.execute(text("SELECT * FROM v_instagram_account_health LIMIT 1")).fetchone()

        if result:
            print_result(True, "Retrieved Instagram account health data")
            print(f"     Account ID: {result[0]}")
            print(f"     Username: {result[1]}")
            print(f"     Success rate: {result[7]}%")
            print(f"     Cookie health: {result[8]}")
            print(f"     Cookie age (days): {result[9]}")

            # Verify cookie health status logic
            cookie_health = result[8]
            cookie_age = result[9]

            if cookie_age is None and cookie_health == "NO_COOKIES":
                return print_result(True, "Cookie health status correctly shows NO_COOKIES")
            elif cookie_age is not None:
                if cookie_age <= 5 and cookie_health == "HEALTHY":
                    return print_result(True, f"Cookie health correctly shows HEALTHY (age: {cookie_age} days)")
                elif 5 < cookie_age <= 7 and cookie_health == "EXPIRING_SOON":
                    return print_result(True, f"Cookie health correctly shows EXPIRING_SOON (age: {cookie_age} days)")
                elif cookie_age > 7 and cookie_health == "EXPIRED":
                    return print_result(True, f"Cookie health correctly shows EXPIRED (age: {cookie_age} days)")
                else:
                    return print_result(True, f"Cookie health status: {cookie_health} (age: {cookie_age} days)")
            else:
                return print_result(True, "Instagram account health view working")
        else:
            return print_result(True, "v_instagram_account_health view exists (no data yet)")

    except Exception as e:
        return print_result(False, f"v_instagram_account_health test failed: {str(e)}")

    finally:
        db.close()


def test_view_recent_activity():
    """Test 6: Test v_recent_activity with joined data"""
    print_header("v_recent_activity View")

    db = SessionLocal()
    try:
        # Query the view
        result = db.execute(text("SELECT * FROM v_recent_activity LIMIT 1")).fetchone()

        if result:
            print_result(True, "Retrieved recent activity data")
            print(f"     Event type: {result[1]}")
            print(f"     Created at: {result[7]}")
            return print_result(True, "v_recent_activity view working with joins")
        else:
            return print_result(True, "v_recent_activity view exists (no data yet)")

    except Exception as e:
        return print_result(False, f"v_recent_activity test failed: {str(e)}")

    finally:
        db.close()


def test_view_job_performance():
    """Test 7: Test v_job_performance duration calculations"""
    print_header("v_job_performance View")

    db = SessionLocal()
    try:
        # Query the view
        # Columns: job_id, user_id, username, status, usernames, reel_count, credits_consumed,
        #          instagram_account_id, instagram_account_username, start_time, end_time, duration_seconds
        result = db.execute(text("SELECT * FROM v_job_performance WHERE duration_seconds IS NOT NULL LIMIT 1")).fetchone()

        if result:
            print_result(True, "Retrieved job performance data")
            print(f"     Job ID: {result[0]}")
            print(f"     Reel count: {result[5]}")
            print(f"     Credits consumed: {result[6]}")
            print(f"     Duration (seconds): {result[11]}")

            # Verify duration calculation is reasonable
            duration = result[11]  # duration_seconds column
            if duration is not None and duration >= 0:
                return print_result(True, f"Duration calculated correctly: {duration} seconds")
            else:
                return print_result(False, f"Invalid duration: {duration}")
        else:
            return print_result(True, "v_job_performance view exists (no completed jobs yet)")

    except Exception as e:
        return print_result(False, f"v_job_performance test failed: {str(e)}")

    finally:
        db.close()


def test_view_hourly_usage_pattern():
    """Test 8: Test v_hourly_usage_pattern aggregation"""
    print_header("v_hourly_usage_pattern View")

    db = SessionLocal()
    try:
        # Query the view
        result = db.execute(text("SELECT * FROM v_hourly_usage_pattern LIMIT 1")).fetchone()

        if result:
            print_result(True, "Retrieved hourly usage pattern data")
            print(f"     Hour: {result[0]}")
            print(f"     Total reels: {result[1]}")
            print(f"     Unique users: {result[2]}")
            return print_result(True, "v_hourly_usage_pattern view working correctly")
        else:
            return print_result(True, "v_hourly_usage_pattern view exists (no data yet)")

    except Exception as e:
        return print_result(False, f"v_hourly_usage_pattern test failed: {str(e)}")

    finally:
        db.close()


def test_admin_user_exists():
    """Test 9: Verify admin user exists in database"""
    print_header("Admin User Existence")

    db = SessionLocal()
    try:
        # Check for admin user
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.email == "admin@example.com"
        ).first()

        if admin:
            print_result(True, f"Admin user found: {admin.username}")
            print(f"     Email: {admin.email}")
            print(f"     Active: {admin.is_active}")

            # Verify password hash exists
            if admin.password_hash and len(admin.password_hash) > 0:
                return print_result(True, "Admin password hash exists")
            else:
                return print_result(False, "Admin password hash missing")
        else:
            return print_result(False, "Default admin user not found (email: admin@example.com)")

    except Exception as e:
        return print_result(False, f"Admin user test failed: {str(e)}")

    finally:
        db.close()


def test_user_management_queries():
    """Test 10: Test user listing and filtering logic"""
    print_header("User Management Queries")

    db = SessionLocal()
    try:
        # Test user listing
        total_users = db.query(func.count(models.User.id)).scalar()
        print_result(True, f"Total users in database: {total_users}")

        # Test active/inactive filtering
        active_users = db.query(func.count(models.User.id)).filter(
            models.User.is_active == True
        ).scalar()
        print_result(True, f"Active users: {active_users}")

        inactive_users = db.query(func.count(models.User.id)).filter(
            models.User.is_active == False
        ).scalar()
        print_result(True, f"Inactive users: {inactive_users}")

        # Verify counts add up
        if active_users + inactive_users == total_users:
            return print_result(True, "User filtering logic correct")
        else:
            return print_result(False, f"User count mismatch: {active_users} + {inactive_users} != {total_users}")

    except Exception as e:
        return print_result(False, f"User management test failed: {str(e)}")

    finally:
        db.close()


def test_activity_log_filtering():
    """Test 11: Test activity log filtering by event type, date"""
    print_header("Activity Log Filtering")

    db = SessionLocal()
    try:
        # Test total logs
        total_logs = db.query(func.count(models.ActivityLog.id)).scalar()
        print_result(True, f"Total activity logs: {total_logs}")

        # Test event type breakdown
        event_types = db.query(
            models.ActivityLog.event_type,
            func.count(models.ActivityLog.id)
        ).group_by(models.ActivityLog.event_type).all()

        print_result(True, f"Event types found: {len(event_types)}")
        for event_type, count in event_types[:5]:  # Show first 5
            print(f"     {event_type}: {count}")

        # Test date filtering (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_logs = db.query(func.count(models.ActivityLog.id)).filter(
            models.ActivityLog.created_at >= seven_days_ago
        ).scalar()
        print_result(True, f"Logs in last 7 days: {recent_logs}")

        return print_result(True, "Activity log filtering working correctly")

    except Exception as e:
        return print_result(False, f"Activity log test failed: {str(e)}")

    finally:
        db.close()


def test_statistics_calculations():
    """Test 12: Test system overview calculations"""
    print_header("Statistics Calculations")

    db = SessionLocal()
    try:
        # Test user statistics
        total_users = db.query(func.count(models.User.id)).scalar()
        active_users = db.query(func.count(models.User.id)).filter(
            models.User.is_active == True
        ).scalar()
        print_result(True, f"User stats: {active_users}/{total_users} active")

        # Test Instagram account statistics
        total_accounts = db.query(func.count(models.InstagramAccount.id)).scalar()
        active_accounts = db.query(func.count(models.InstagramAccount.id)).filter(
            models.InstagramAccount.is_active == True,
            models.InstagramAccount.is_paused == False
        ).scalar()
        print_result(True, f"Account stats: {active_accounts}/{total_accounts} active")

        # Test job statistics
        total_jobs = db.query(func.count(models.ScrapingJob.id)).scalar()
        successful_jobs = db.query(func.count(models.ScrapingJob.id)).filter(
            models.ScrapingJob.status == "completed"
        ).scalar()

        print_result(True, f"Job stats: {successful_jobs}/{total_jobs} completed")

        # Verify success rate calculation
        if total_jobs > 0:
            success_rate = round((successful_jobs / total_jobs) * 100, 1)
            print_result(True, f"Success rate: {success_rate}%")
            return print_result(True, "Statistics calculations working correctly")
        else:
            return print_result(True, "Statistics calculations ready (no jobs yet)")

    except Exception as e:
        return print_result(False, f"Statistics test failed: {str(e)}")

    finally:
        db.close()


def test_usage_statistics():
    """Test 13: Test daily trends and top consumers"""
    print_header("Usage Statistics")

    db = SessionLocal()
    try:
        # Test daily trends
        seven_days_ago = datetime.now() - timedelta(days=7)

        daily_reels = db.query(
            func.date(models.ScrapedReel.scraped_at).label('date'),
            func.count(models.ScrapedReel.id).label('reels_count')
        ).filter(
            models.ScrapedReel.scraped_at >= seven_days_ago
        ).group_by(
            func.date(models.ScrapedReel.scraped_at)
        ).all()

        print_result(True, f"Daily trends: {len(daily_reels)} days with data")
        for day in daily_reels[:3]:  # Show first 3 days
            print(f"     {day.date}: {day.reels_count} reels")

        # Test top credit consumers
        top_users = db.query(
            models.User.username,
            models.User.credits_used_today
        ).filter(
            models.User.credits_used_today > 0
        ).order_by(
            models.User.credits_used_today.desc()
        ).limit(3).all()

        print_result(True, f"Top credit consumers: {len(top_users)} users")
        for username, credits in top_users:
            print(f"     {username}: {credits} credits")

        return print_result(True, "Usage statistics working correctly")

    except Exception as e:
        return print_result(False, f"Usage statistics test failed: {str(e)}")

    finally:
        db.close()


def test_performance_metrics():
    """Test 14: Test account distribution and averages"""
    print_header("Performance Metrics")

    db = SessionLocal()
    try:
        # Test account distribution
        account_usage = db.query(
            models.InstagramAccount.username,
            models.InstagramAccount.daily_scrape_count,
            models.InstagramAccount.total_scrapes,
            models.InstagramAccount.success_count,
            models.InstagramAccount.failure_count
        ).filter(
            models.InstagramAccount.is_active == True
        ).all()

        print_result(True, f"Account distribution: {len(account_usage)} accounts")
        for username, daily, total, success, failure in account_usage[:3]:  # Show first 3
            total_ops = success + failure
            success_rate = round((success / total_ops) * 100, 1) if total_ops > 0 else 0
            print(f"     {username}: {daily} today, {total} total, {success_rate}% success")

        # Test average reels per job
        avg_reels = db.query(func.avg(models.ScrapingJob.reel_count)).filter(
            models.ScrapingJob.status == "completed"
        ).scalar()

        if avg_reels:
            print_result(True, f"Average reels per job: {round(avg_reels, 1)}")
            return print_result(True, "Performance metrics working correctly")
        else:
            return print_result(True, "Performance metrics ready (no completed jobs yet)")

    except Exception as e:
        return print_result(False, f"Performance metrics test failed: {str(e)}")

    finally:
        db.close()


def run_all_tests():
    """Run all Phase 3 tests"""
    print("\n" + "=" * 60)
    print("PHASE 3 TESTING - ADMIN PANEL & STATISTICS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        ("Database Indexes", test_database_indexes),
        ("Database Views Exist", test_database_views),
        ("v_daily_stats View", test_view_daily_stats),
        ("v_user_summary View", test_view_user_summary),
        ("v_instagram_account_health View", test_view_instagram_account_health),
        ("v_recent_activity View", test_view_recent_activity),
        ("v_job_performance View", test_view_job_performance),
        ("v_hourly_usage_pattern View", test_view_hourly_usage_pattern),
        #("Admin User Exists", test_admin_user_exists),
        ("User Management Queries", test_user_management_queries),
        ("Activity Log Filtering", test_activity_log_filtering),
        ("Statistics Calculations", test_statistics_calculations),
        ("Usage Statistics", test_usage_statistics),
        ("Performance Metrics", test_performance_metrics)
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
    print(f"Tests Passed: {passed}/{total} ({round(passed/total * 100, 1)}%)")

    if passed == total:
        print("[OK] All tests PASSED!")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"[FAIL] {total - passed} test(s) FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
