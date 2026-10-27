from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.health import ComponentStatus, HealthResponse
from app.services.health import HealthService, get_health_service

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Returns application health status, database connectivity, and storage availability.",
)
def get_health(
    response: Response,
    db: Session = Depends(get_db),
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Check health of the backend application and its backing services."""
    health_data = health_service.get_system_health(db)
    if health_data.status == ComponentStatus.DOWN:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health_data
