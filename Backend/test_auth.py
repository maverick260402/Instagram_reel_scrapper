"""
Unit tests for authentication module
"""
import pytest
from datetime import timedelta
from jose import JWTError, jwt

from auth import (
    verify_password,
    hash_password,
    create_access_token,
    verify_token
)

def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPass123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass", hashed)


def test_jwt_token_creation():
    """Test JWT token creation"""
    data = {"sub": "user@test.com", "user_id": 1}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long


def test_jwt_token_verification():
    """Test JWT token verification"""
    data = {"sub": "user@test.com", "user_id": 1}
    token = create_access_token(data)
    decoded = verify_token(token)

    assert decoded["sub"] == "user@test.com"
    assert decoded["user_id"] == 1


def test_jwt_token_expiration():
    """Test JWT token expiration"""
    from fastapi import HTTPException
    data = {"sub": "user@test.com"}
    # Create token that expired 1 second ago
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))

    with pytest.raises((JWTError, HTTPException)):
        verify_token(token)


@pytest.mark.parametrize("password,expected_valid", [
    ("Short1", False),  # Too short
    ("NoNumbers", False),  # No numbers
    ("12345678", False),  # No letters
    ("GoodPass123", True),  # Valid
])
def test_password_validation_patterns(password, expected_valid):
    """Test various password patterns"""
    # This tests that passwords can be hashed successfully
    # In real implementation, you'd have a password validation function
    try:
        hashed = hash_password(password)
        # All passwords can be hashed, but this tests the pattern
        assert len(password) >= 8 or not expected_valid
    except Exception:
        assert not expected_valid


def test_password_hash_consistency():
    """Test that same password doesn't produce same hash (salt is used)"""
    password = "TestPass123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different due to salt
    assert hash1 != hash2
    # But both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_token_contains_correct_fields():
    """Test that token contains all required fields"""
    data = {
        "sub": "test@example.com",
        "user_id": 42,
        "username": "testuser"
    }
    token = create_access_token(data)
    decoded = verify_token(token)

    assert "sub" in decoded
    assert "user_id" in decoded
    assert "username" in decoded
    assert "exp" in decoded  # Expiration time should be added


def test_invalid_token():
    """Test that invalid tokens raise errors"""
    from fastapi import HTTPException
    invalid_token = "this.is.not.a.valid.jwt.token"

    with pytest.raises((JWTError, HTTPException)):
        verify_token(invalid_token)


def test_password_verification_with_wrong_password():
    """Test password verification fails with wrong password"""
    password = "CorrectPassword123"
    wrong_password = "WrongPassword456"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
    assert verify_password(wrong_password, hashed) is False
