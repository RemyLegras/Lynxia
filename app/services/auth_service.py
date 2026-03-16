from app.database import get_mysql_connection
from app.services.user_service import get_user
from app.utils import hash_password, generate_token
import time

def authenticate_user(email: str, password: str):
    """Vérifie les identifiants et retourne l'utilisateur ou None"""
    user = get_user(email)
    if not user:
        return None
    
    if user["password_hash"] != hash_password(password):
        return None
    
    return user

def create_token(email: str):
    """Crée un token pour l'utilisateur"""
    token = generate_token()
    token_data = {
        "email": email,
        "created_at": time.time()
    }
    
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tokens (token, email, created_at) VALUES (%s, %s, FROM_UNIXTIME(%s))",
                (token, email, token_data["created_at"])
            )
        conn.commit()
        return token
    finally:
        conn.close()

def get_token_data(token: str):
    """Récupère les données d'un token"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT *, UNIX_TIMESTAMP(created_at) as created_at FROM tokens WHERE token = %s", (token,))
            return cursor.fetchone()
    finally:
        conn.close()

def delete_token(token: str):
    """Supprime un token"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tokens WHERE token = %s", (token,))
        conn.commit()
    finally:
        conn.close()

def is_token_valid(token: str) -> bool:
    """Vérifie si un token est valide (non expiré)"""
    token_data = get_token_data(token)
    if not token_data:
        return False
    
    # Token expiré après 24h
    if time.time() - token_data["created_at"] > 86400:
        delete_token(token)
        return False
    
    return True
