from fastapi import APIRouter
from app.api.v1 import health

api_router = APIRouter()

# Include health routes under /api/health
api_router.include_router(health.router, tags=["Health"])

# Future feature modules can be mounted here modularly:
# api_router.include_router(recipes.router, prefix="/v1/recipes", tags=["Recipes"])
