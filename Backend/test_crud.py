"""
Unit tests for CRUD operations
"""
import pytest
from crud import (
    get_user_by_email,
    get_user_by_username,
    create_user,
    create_instagram_account,
    create_activity_log,
    get_all_instagram_accounts
)
from schemas import UserCreate


@pytest.mark.integration
def test_create_user(db_session):
    """Test user creation via CRUD"""
    user_data = UserCreate(
        email="newuser@test.com",
        username="newuser",
        password="TestPass123"
    )

    user = create_user(db_session, user_data)

    assert user is not None
    assert user.email == "newuser@test.com"
    assert user.username == "newuser"
    assert user.is_active is True
    assert user.daily_credit_limit == 2000


@pytest.mark.integration
def test_get_user_by_email(db_session):
    """Test user retrieval by email"""
    # First create a user
    user_data = UserCreate(
        email="lookup@test.com",
        username="lookupuser",
        password="TestPass123"
    )
    created_user = create_user(db_session, user_data)

    # Then look it up
    found_user = get_user_by_email(db_session, "lookup@test.com")

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == "lookup@test.com"


@pytest.mark.integration
def test_get_user_by_username(db_session):
    """Test user retrieval by username"""
    # First create a user
    user_data = UserCreate(
        email="usertest@test.com",
        username="testuserx",
        password="TestPass123"
    )
    created_user = create_user(db_session, user_data)

    # Then look it up
    found_user = get_user_by_username(db_session, "testuserx")

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == "testuserx"


@pytest.mark.integration
def test_create_instagram_account(db_session):
    """Test Instagram account creation"""
    account = create_instagram_account(
        db=db_session,
        username="insta_test_account",
        email="insta@test.com",
        password="instapass123"
    )

    assert account is not None
    assert account.username == "insta_test_account"
    assert account.email == "insta@test.com"
    assert account.is_active is True
    assert account.is_paused is False


@pytest.mark.integration
def test_create_activity_log(db_session):
    """Test activity log creation"""
    log = create_activity_log(
        db=db_session,
        event_type="test_event",
        details={"test_key": "test_value"}
    )

    assert log is not None
    assert log.event_type == "test_event"
    assert log.details["test_key"] == "test_value"


@pytest.mark.integration
def test_get_all_instagram_accounts(db_session):
    """Test retrieving all Instagram accounts"""
    # Create a couple of accounts
    create_instagram_account(
        db=db_session,
        username="account1",
        email="acc1@test.com",
        password="pass1"
    )
    create_instagram_account(
        db=db_session,
        username="account2",
        email="acc2@test.com",
        password="pass2"
    )

    # Get all accounts
    accounts = get_all_instagram_accounts(db_session)

    assert accounts is not None
    assert len(accounts) >= 2  # At least the two we created
    usernames = [acc.username for acc in accounts]
    assert "account1" in usernames
    assert "account2" in usernames


@pytest.mark.integration
def test_user_not_found(db_session):
    """Test that non-existent user returns None"""
    user = get_user_by_email(db_session, "nonexistent@test.com")
    assert user is None


@pytest.mark.integration
def test_duplicate_user_email(db_session):
    """Test that duplicate email is handled"""
    user_data = UserCreate(
        email="duplicate@test.com",
        username="user1",
        password="TestPass123"
    )
    create_user(db_session, user_data)

    # Try to create another user with same email
    user_data2 = UserCreate(
        email="duplicate@test.com",  # Same email
        username="user2",  # Different username
        password="TestPass123"
    )

    # This should fail due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        create_user(db_session, user_data2)
        db_session.commit()
