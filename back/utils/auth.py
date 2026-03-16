from app.services.auth_service import get_token_data, delete_token
import time
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Décorateur pour valider le token et récupérer l'utilisateur courant"""
    token = credentials.credentials
    token_data = get_token_data(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Token expiré après 24h
    if time.time() - token_data["created_at"] > 86400:
        delete_token(token)
        raise HTTPException(status_code=401, detail="Token expiré")
    
    return {
        "email": token_data["email"]
    }
