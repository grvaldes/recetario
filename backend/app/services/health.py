import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.schemas.health import ComponentStatus, HealthResponse, ServiceHealthDetails

logger = logging.getLogger(__name__)


class HealthService:
    """Service handling system health checks and component diagnostics."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def check_database(self, db: Session) -> ServiceHealthDetails:
        """Verify database connectivity via a lightweight query."""
        try:
            db.execute(text("SELECT 1"))
            return ServiceHealthDetails(status=ComponentStatus.OPERATIONAL, message="Database connection active")
        except Exception as exc:
            logger.error("Database health check failed: %s", exc)
            return ServiceHealthDetails(
                status=ComponentStatus.DOWN,
                message=f"Database unreachable: {str(exc)}",
            )

    def check_storage(self, upload_dir: Path) -> ServiceHealthDetails:
        """Verify that the recipe image upload directory exists and is writable."""
        try:
            if not upload_dir.exists():
                upload_dir.mkdir(parents=True, exist_ok=True)

            # Test write access with a temporary probe file
            test_file = upload_dir / ".health_probe"
            test_file.write_text("probe", encoding="utf-8")
            if test_file.exists():
                test_file.unlink()

            return ServiceHealthDetails(status=ComponentStatus.OPERATIONAL, message="Upload storage writable")
        except Exception as exc:
            logger.error("Storage health check failed: %s", exc)
            return ServiceHealthDetails(
                status=ComponentStatus.DOWN,
                message=f"Storage directory inaccessible: {str(exc)}",
            )

    def get_system_health(self, db: Session) -> HealthResponse:
        """Aggregate health statuses and return the full health response."""
        db_health = self.check_database(db)
        storage_health = self.check_storage(self.settings.UPLOAD_DIR)

        components = {
            "database": db_health,
            "uploads_storage": storage_health,
        }

        # Calculate overall status
        if all(comp.status == ComponentStatus.OPERATIONAL for comp in components.values()):
            overall_status = ComponentStatus.OPERATIONAL
        elif any(comp.status == ComponentStatus.OPERATIONAL for comp in components.values()):
            overall_status = ComponentStatus.DEGRADED
        else:
            overall_status = ComponentStatus.DOWN

        return HealthResponse(
            status=overall_status,
            app_name=self.settings.APP_NAME,
            version=self.settings.VERSION,
            environment=self.settings.ENVIRONMENT,
            timestamp=datetime.now(timezone.utc),
            components=components,
        )


def get_health_service(settings: Settings = Depends(get_settings)) -> HealthService:
    """Dependency injection provider for HealthService."""
    return HealthService(settings=settings)


