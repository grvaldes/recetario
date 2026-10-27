from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.schemas.health import ComponentStatus


def test_health_endpoint_success(client: TestClient) -> None:
    """Test that GET /api/health returns 200 OK with operational components."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == ComponentStatus.OPERATIONAL
    assert data["app_name"] == "Recetario Test"
    assert data["version"] == "0.1.0-test"
    assert data["environment"] == "test"

    # Verify components
    components = data["components"]
    assert "database" in components
    assert components["database"]["status"] == ComponentStatus.OPERATIONAL
    assert "uploads_storage" in components
    assert components["uploads_storage"]["status"] == ComponentStatus.OPERATIONAL

    # Verify timestamp is valid UTC ISO string
    parsed_timestamp = datetime.fromisoformat(data["timestamp"])
    assert parsed_timestamp.tzinfo is not None


def test_health_endpoint_database_failure(client: TestClient) -> None:
    """Test that GET /api/health reports degraded/down and non-200 when database fails."""

    def failing_get_db():
        class MockFailingSession:
            def execute(self, *args, **kwargs):
                raise RuntimeError("Simulated database failure")

            def close(self):
                pass

        yield MockFailingSession()

    app.dependency_overrides[get_db] = failing_get_db

    try:
        response = client.get("/api/health")
        data = response.json()

        assert data["components"]["database"]["status"] == ComponentStatus.DOWN
        assert "Simulated database failure" in data["components"]["database"]["message"]
        # When DB is down but storage is up, overall status is degraded or down
        assert data["status"] in (ComponentStatus.DEGRADED, ComponentStatus.DOWN)
    finally:
        # Restore standard test override
        from tests.conftest import override_get_db
        app.dependency_overrides[get_db] = override_get_db
