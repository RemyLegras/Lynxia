from app.database import get_connection
from app.utils import hash_password


def to_public_user(user: dict | None, fallback_email: str | None = None):
    user = user or {}
    return {
        "email": user.get("email", fallback_email),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
    }

def create_user(email: str, password: str, first_name: str | None = None, last_name: str | None = None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (email, password_hash, first_name, last_name) VALUES (%s, %s, %s, %s)",
                (email, hash_password(password), first_name, last_name)
            )
        conn.commit()
    finally:
        conn.close()

def get_user(email: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
    finally:
        conn.close()

def user_exists(email: str) -> bool:
    return get_user(email) is not None


def update_user_profile(email: str, first_name: str | None, last_name: str | None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET first_name = %s, last_name = %s WHERE email = %s",
                (first_name, last_name, email),
            )
        conn.commit()
    finally:
        conn.close()
