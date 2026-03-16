from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.user_service import create_user, user_exists

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(user: UserRegister):
    if user_exists(user.email):
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    create_user(user.email, user.password)
    return {"message": "Inscription réussie"}