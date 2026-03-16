import os
import pymysql

def get_mysql_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "documents_db"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_database():
    """Crée les tables si elles n'existent pas"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            # Table users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email VARCHAR(255) PRIMARY KEY,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email) REFERENCES users(email)
                )
            """)
            
            # Table documents
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    element_id VARCHAR(50) PRIMARY KEY,
                    owner_user_id VARCHAR(255) NOT NULL,
                    document_type VARCHAR(100),
                    curated_data JSON,
                    status VARCHAR(50) DEFAULT 'uploaded',
                    raw_path VARCHAR(500),
                    clean_text_ref VARCHAR(500),
                    inconsistencies JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_user_id) REFERENCES users(email)
                )
            """)
        conn.commit()
    finally:
        conn.close()

def init_database_if_available():
    """Initialise la base si MySQL est disponible, sans bloquer le démarrage de l'API."""
    try:
        init_database()
    except pymysql.MySQLError as exc:
        print(f"[WARN] MySQL indisponible au démarrage, initialisation ignorée: {exc}")

# Initialiser la base au démarrage (best-effort)
init_database_if_available()
