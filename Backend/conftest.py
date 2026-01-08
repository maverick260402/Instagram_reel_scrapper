"""
pytest configuration - Makes existing tests pytest-compatible
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

# Now import existing test modules (makes them discoverable)
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
def db_session(database_url):
    """Provide database session for tests"""
    from database import SessionLocal, engine
    from models import Base

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any global state between tests"""
    yield
    # Cleanup code here if needed
