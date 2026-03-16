from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import time

from app.services.auth_service import delete_token, get_token_data

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    token_data = get_token_data(token)

    if not token_data:
        raise HTTPException(status_code=401, detail="Token invalide")

    if time.time() - token_data["created_at"] > 86400:
        delete_token(token)
        raise HTTPException(status_code=401, detail="Token expire")

    return {"email": token_data["email"]}
