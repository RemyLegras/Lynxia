from fastapi import APIRouter, Depends
from app.auth_utils import get_current_user

router = APIRouter()

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}