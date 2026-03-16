from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.auth_service import authenticate_user, create_token

router = APIRouter()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin):
    user_data = authenticate_user(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_token(user.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user.email
        }
    }