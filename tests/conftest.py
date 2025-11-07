import os

# Set environment variables BEFORE any imports
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")


import pytest
from unittest.mock import patch


# Mock database for tests that don't need it
@pytest.fixture(scope="session", autouse=True)
def mock_database():
    """Mock database engine and session for tests."""
    with patch("tprep.infrastructure.database.engine") as mock_engine, \
         patch("tprep.infrastructure.database.SessionLocal") as mock_session:
        mock_engine.configure_mock(**{"dialect.name": "sqlite"})
        yield mock_engine, mock_session