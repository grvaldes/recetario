from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ComponentStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"


class ServiceHealthDetails(BaseModel):
    status: ComponentStatus
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: ComponentStatus = Field(..., description="Overall health of the application")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment (e.g. development, production)")
    timestamp: datetime = Field(..., description="Current UTC timestamp")
    components: Dict[str, ServiceHealthDetails] = Field(
        ...,
        description="Health status of downstream dependencies (database, storage)",
    )
