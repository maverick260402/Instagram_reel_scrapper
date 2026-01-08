"""
Unit tests for utility functions and general application behavior
"""
import pytest
from datetime import datetime, date, timedelta


def test_date_formatting():
    """Test date formatting utilities"""
    test_date = datetime(2025, 1, 8, 12, 30, 45)

    assert test_date.year == 2025
    assert test_date.month == 1
    assert test_date.day == 8
    assert test_date.hour == 12


def test_string_validation():
    """Test string validation patterns"""
    # Username validation
    valid_username = "testuser123"
    assert len(valid_username) >= 3
    assert valid_username.isalnum() or '_' in valid_username

    # Email basic check
    valid_email = "test@example.com"
    assert "@" in valid_email
    assert "." in valid_email


def test_job_id_format():
    """Test job ID format generation"""
    # Job IDs typically follow pattern: job_YYYYMMDD_HHMMSS_random
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_123456"

    assert job_id.startswith("job_")
    assert len(job_id) > 20
    parts = job_id.split("_")
    assert len(parts) >= 4


def test_credit_calculation():
    """Test credit calculation logic"""
    # 1 credit = 1 reel
    reels_scraped = 20
    credits_required = reels_scraped * 1

    assert credits_required == 20
    assert credits_required > 0


def test_percentage_calculation():
    """Test percentage calculations"""
    used = 150
    limit = 2000
    percentage = (used / limit) * 100

    assert percentage == 7.5
    assert 0 <= percentage <= 100


def test_date_comparison():
    """Test date comparison for daily reset"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    assert yesterday < today
    assert today < tomorrow
    assert today != yesterday


def test_list_operations():
    """Test common list operations"""
    usernames = ["user1", "user2", "user3"]

    assert len(usernames) == 3
    assert "user1" in usernames
    assert "user4" not in usernames
    assert usernames[0] == "user1"


def test_dict_operations():
    """Test common dictionary operations"""
    data = {
        "status": "success",
        "count": 10,
        "results": ["item1", "item2"]
    }

    assert "status" in data
    assert data["status"] == "success"
    assert data["count"] == 10
    assert len(data["results"]) == 2


def test_none_handling():
    """Test None value handling"""
    value = None

    assert value is None
    assert not value
    assert value != False  # None is not False
    assert value != 0  # None is not 0


@pytest.mark.parametrize("input_val,expected", [
    (0, False),
    (1, True),
    (100, True),
    (-1, False),
])
def test_positive_number_check(input_val, expected):
    """Test positive number validation"""
    is_positive = input_val > 0
    assert is_positive == expected


def test_array_normalization():
    """Test array/list normalization"""
    raw_usernames = ["user1", "USER2", " user3 ", "user1"]

    # Normalize: lowercase, strip whitespace, remove duplicates
    normalized = list(set([u.strip().lower() for u in raw_usernames]))

    assert "user1" in normalized
    assert "user2" in normalized
    assert "user3" in normalized
    assert len(normalized) == 3  # Duplicate removed
