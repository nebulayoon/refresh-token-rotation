from fastapi import APIRouter

from app.auth.views import auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
