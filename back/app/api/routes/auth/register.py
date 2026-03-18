from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.user_service import create_user, user_exists

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None

@router.post("/register")
def register(user: UserRegister):
    if user_exists(user.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    create_user(user.email, user.password, user.first_name, user.last_name)
    return {"message": "Inscription réussie"}