from fastapi import APIRouter
from app.api.routes.auth.register import router as register_router
from app.api.routes.auth.login import router as login_router
from app.api.routes.auth.me import router as me_router
from app.api.routes.documents import router as documents_router

api_router = APIRouter()

api_router.include_router(register_router, prefix="/auth", tags=["auth"])
api_router.include_router(login_router, prefix="/auth", tags=["auth"])
api_router.include_router(me_router, prefix="/auth", tags=["auth"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])