from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth_utils import get_current_user
from app.services.document_service import get_user_document_stats
from app.services.user_service import get_user, to_public_user, update_user_profile


router = APIRouter()


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


@router.patch("/me")
def update_me(payload: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    update_user_profile(current_user["email"], payload.first_name, payload.last_name)
    user = get_user(current_user["email"])
    return {"user": to_public_user(user, fallback_email=current_user["email"])}


@router.get("/stats")
def get_my_stats(current_user: dict = Depends(get_current_user)):
    email = current_user["email"]
    document_stats = get_user_document_stats(email)
    profile_stats = {
        "total_documents": document_stats["total_documents"],
        "uploaded_documents": document_stats["uploaded_documents"],
        "processed_documents": document_stats["processed_documents"],
    }
    return {
        "user": to_public_user(current_user, fallback_email=email),
        "profile_stats": profile_stats,
        "document_stats": document_stats,
    }