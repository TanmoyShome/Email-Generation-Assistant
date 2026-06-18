from fastapi import APIRouter

from app.api.v1.routes import evaluation, generation

api_router = APIRouter()
api_router.include_router(generation.router, prefix="/emails", tags=["generation"])
api_router.include_router(evaluation.router, prefix="/emails", tags=["evaluation"])
