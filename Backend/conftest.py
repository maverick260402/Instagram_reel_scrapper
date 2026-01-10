"""
Pytest configuration and fixtures - Makes existing tests pytest-compatible
"""
import pytest
import sys
import os
from pathlib import Path

# Add Backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up test environment variables BEFORE importing modules
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://scraper_user:scraper_password_123@localhost:5432/instagram_scraper"
)
os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-key-for-testing-only-not-for-production-use-123456789"
)
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
os.environ.setdefault("MAX_GROUPS_PER_USER", "100")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:8080")

# Now import database modules
from database import SessionLocal, engine, Base
from models import User, InstagramAccount, ApiKey, AdminUser, ActivityLog, ScrapingJob, ScrapedReel

# Import existing test modules (makes them discoverable)
from test_phase1 import *
from test_phase2 import *
from test_phase3 import *


@pytest.fixture(scope="session")
def database_url():
    """Provide database URL for tests"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://scraper_user:scraper_password_123@localhost:5432/instagram_scraper"
    )


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database session for each test function
    (Compatible with test_phase1.py fixtures)
    """
    # Create a new database session
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()


@pytest.fixture(scope="function")
def db_session(database_url):
    """
    Provide database session for tests
    (Alternative name for compatibility)
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Setup test database tables (runs once per test session)
    """
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally drop tables after tests (commented out to preserve data)
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any global state between tests"""
    yield
    # Cleanup code here if needed
