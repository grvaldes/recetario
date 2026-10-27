import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.main import app

# In-memory SQLite engine for isolated, fast, self-contained test execution
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        ENVIRONMENT="test",
        APP_NAME="Recetario Test",
        VERSION="0.1.0-test",
        UPLOAD_DIR=os.path.abspath("./test_uploads"),
    )


@pytest.fixture()
def client(tmp_path) -> Generator[TestClient, None, None]:
    """TestClient fixture with dependency overrides for database and upload path."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    def override_settings() -> Settings:
        return Settings(
            ENVIRONMENT="test",
            APP_NAME="Recetario Test",
            VERSION="0.1.0-test",
            UPLOAD_DIR=upload_dir,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
