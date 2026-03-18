from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
import time

from app.services.auth_service import delete_token, get_token_data
from app.services.user_service import get_user, to_public_user

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    token_data = get_token_data(token)

    if not token_data:
        raise HTTPException(status_code=401, detail="Token invalide")

    created_at = token_data.get("created_at")
    if isinstance(created_at, datetime):
        created_at_ts = created_at.timestamp()
    else:
        created_at_ts = float(created_at)

    if time.time() - created_at_ts > 86400:
        delete_token(token)
        raise HTTPException(status_code=401, detail="Token expire")

    user = get_user(token_data["email"])
    return to_public_user(user, fallback_email=token_data["email"])
