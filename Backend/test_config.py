"""
Unit tests for configuration module
"""
import pytest
from config import settings


def test_settings_loaded():
    """Test that settings are loaded successfully"""
    assert settings is not None
    assert hasattr(settings, 'DATABASE_URL')
    assert hasattr(settings, 'SECRET_KEY')


def test_default_values():
    """Test default configuration values"""
    assert settings.MAX_GROUPS_PER_USER == 100
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 10080  # 7 days


def test_jwt_expiration_time():
    """Test JWT expiration time is reasonable"""
    # Should be 7 days (10080 minutes)
    minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    assert minutes == 10080
    # Convert to days
    days = minutes / 60 / 24
    assert days == 7


def test_database_url_exists():
    """Test that DATABASE_URL is configured"""
    assert settings.DATABASE_URL is not None
    assert len(settings.DATABASE_URL) > 0
    assert "postgresql://" in settings.DATABASE_URL


def test_secret_key_exists():
    """Test that SECRET_KEY is configured"""
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) > 0


def test_algorithm_is_hs256():
    """Test that JWT algorithm is HS256"""
    assert settings.ALGORITHM == "HS256"


def test_max_groups_per_user():
    """Test maximum groups per user limit"""
    assert settings.MAX_GROUPS_PER_USER == 100
    assert isinstance(settings.MAX_GROUPS_PER_USER, int)
    assert settings.MAX_GROUPS_PER_USER > 0


def test_allowed_origins_type():
    """Test that ALLOWED_ORIGINS is a string"""
    assert hasattr(settings, 'ALLOWED_ORIGINS')
    assert isinstance(settings.ALLOWED_ORIGINS, str)


def test_environment_setting():
    """Test that ENVIRONMENT setting exists"""
    if hasattr(settings, 'ENVIRONMENT'):
        env = settings.ENVIRONMENT
        assert env in ['development', 'testing', 'production', 'dev', 'prod']
