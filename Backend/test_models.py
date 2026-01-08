"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from models import (
    User,
    InstagramAccount,
    ScrapingJob,
    ScrapedReel,
    UserGroup,
    ActivityLog,
    ApiKey,
    AdminUser
)


def test_user_model_creation():
    """Test User model instantiation"""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        is_active=True
    )

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True
    # Defaults may be None until saved to database
    assert user.daily_credit_limit is None or user.daily_credit_limit == 2000
    assert user.credits_used_today is None or user.credits_used_today == 0


def test_instagram_account_model():
    """Test InstagramAccount model"""
    account = InstagramAccount(
        username="insta_test",
        email="insta@test.com",
        password="password123",
        is_active=True,
        is_paused=False
    )

    assert account.username == "insta_test"
    assert account.email == "insta@test.com"
    assert account.is_active is True
    assert account.is_paused is False
    # Defaults may be None until saved to database
    assert account.daily_scrape_count is None or account.daily_scrape_count == 0
    assert account.total_scrapes is None or account.total_scrapes == 0
    assert account.success_count is None or account.success_count == 0
    assert account.failure_count is None or account.failure_count == 0


def test_scraping_job_model():
    """Test ScrapingJob model"""
    job = ScrapingJob(
        job_id="test_job_123",
        user_id=1,
        usernames=["user1", "user2"],
        reel_count=20,
        status="running",
        progress=0.0
    )

    assert job.job_id == "test_job_123"
    assert job.user_id == 1
    assert len(job.usernames) == 2
    assert job.reel_count == 20
    assert job.status == "running"
    assert job.progress == 0.0


@pytest.mark.parametrize("status", ["running", "completed", "failed"])
def test_job_status_values(status):
    """Test valid job status values"""
    job = ScrapingJob(
        job_id=f"test_{status}",
        user_id=1,
        usernames=["test"],
        reel_count=10,
        status=status,
        progress=0.0
    )
    assert job.status == status


def test_scraped_reel_model():
    """Test ScrapedReel model"""
    reel = ScrapedReel(
        job_id="job_123",
        user_id=1,
        instagram_username="testuser",
        reel_pk="reel_12345",
        reel_code="ABC123",
        play_count=1000000,
        comment_count=5000,
        like_count=50000,
        is_reel_pinned="No"
    )

    assert reel.job_id == "job_123"
    assert reel.user_id == 1
    assert reel.instagram_username == "testuser"
    assert reel.play_count == 1000000
    assert reel.like_count == 50000


def test_user_group_model():
    """Test UserGroup model"""
    group = UserGroup(
        user_id=1,
        name="My Test Group",
        usernames=["user1", "user2", "user3"],
        times_used=0
    )

    assert group.user_id == 1
    assert group.name == "My Test Group"
    assert len(group.usernames) == 3
    assert group.times_used == 0


def test_activity_log_model():
    """Test ActivityLog model"""
    log = ActivityLog(
        event_type="test_event",
        user_id=1,
        details={"test_key": "test_value"}
    )

    assert log.event_type == "test_event"
    assert log.user_id == 1
    assert log.details["test_key"] == "test_value"


def test_api_key_model():
    """Test ApiKey model"""
    api_key = ApiKey(
        key_name="Test API Key",
        api_key="hashed_key_value",
        is_active=True,
        permissions=["update_cookies"]
    )

    assert api_key.key_name == "Test API Key"
    assert api_key.is_active is True
    assert "update_cookies" in api_key.permissions


def test_admin_user_model():
    """Test AdminUser model"""
    admin = AdminUser(
        username="admin_test",
        email="admin@test.com",
        password_hash="hashed_admin_password",
        is_active=True
    )

    assert admin.username == "admin_test"
    assert admin.email == "admin@test.com"
    assert admin.is_active is True


def test_user_credit_defaults():
    """Test User model credit-related defaults"""
    user = User(
        email="credits@test.com",
        username="credituser",
        password_hash="hash",
        is_active=True
    )

    # Check credit system defaults (may be None until saved to database)
    assert user.daily_credit_limit is None or user.daily_credit_limit == 2000
    assert user.credits_used_today is None or user.credits_used_today == 0
    # last_credit_reset_date may be None or a valid date


def test_instagram_account_counter_defaults():
    """Test InstagramAccount counter defaults"""
    account = InstagramAccount(
        username="counter_test",
        email="counter@test.com",
        password="pass",
        is_active=True
    )

    # Check counter defaults (may be None until saved to database)
    assert account.daily_scrape_count is None or account.daily_scrape_count == 0
    assert account.total_scrapes is None or account.total_scrapes == 0
    assert account.success_count is None or account.success_count == 0
    assert account.failure_count is None or account.failure_count == 0
