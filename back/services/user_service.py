from app.database import get_mysql_connection
from app.utils import hash_password

def create_user(email: str, password: str):
    """Crée un nouvel utilisateur"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                (email, hash_password(password))
            )
        conn.commit()
        return {"message": "Utilisateur créé"}
    finally:
        conn.close()

def get_user(email: str):
    """Récupère un utilisateur par email"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
    finally:
        conn.close()

def user_exists(email: str) -> bool:
    """Vérifie si un utilisateur existe"""
    return get_user(email) is not None
