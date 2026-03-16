from app.database import get_connection
from app.services.user_service import get_user
from app.utils import hash_password, generate_token
import time

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if user and user["password_hash"] == hash_password(password):
        return user
    return None

def create_token(email: str):
    token = generate_token()
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tokens (token, email, created_at) VALUES (%s, %s, FROM_UNIXTIME(%s))",
                (token, email, time.time())
            )
        conn.commit()
        return token
    finally:
        conn.close()

def get_token_data(token: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT *, UNIX_TIMESTAMP(created_at) as created_at FROM tokens WHERE token = %s", (token,))
            return cursor.fetchone()
    finally:
        conn.close()

def delete_token(token: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tokens WHERE token = %s", (token,))
        conn.commit()
    finally:
        conn.close()

def is_token_valid(token: str) -> bool:
    token_data = get_token_data(token)
    if not token_data:
        return False
    
    if time.time() - token_data["created_at"] > 86400:
        delete_token(token)
        return False
    
    return True
