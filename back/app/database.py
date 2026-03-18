import os
import time
import pymysql

def get_connection():
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "documents_db")

    # MySQL peut démarrer quelques secondes après l'API dans Docker.
    # On retente la connexion pour éviter les démarrages partiels.
    last_error = None
    for _ in range(20):
        try:
            return pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        except pymysql.MySQLError as err:
            last_error = err
            time.sleep(1)

    raise last_error

def init_tables():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            db_name = os.getenv("MYSQL_DATABASE", "documents_db")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email VARCHAR(255) PRIMARY KEY,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'first_name'
                """,
                (db_name,),
            )
            first_name_exists = (cursor.fetchone() or {}).get("total", 0) > 0
            if not first_name_exists:
                cursor.execute("ALTER TABLE users ADD COLUMN first_name VARCHAR(100)")

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'last_name'
                """,
                (db_name,),
            )
            last_name_exists = (cursor.fetchone() or {}).get("total", 0) > 0
            if not last_name_exists:
                cursor.execute("ALTER TABLE users ADD COLUMN last_name VARCHAR(100)")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email) REFERENCES users(email)
                )
            """)
            
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
    except pymysql.MySQLError as err:
        raise RuntimeError(f"Erreur initialisation MySQL: {err}") from err
    finally:
        conn.close()

init_tables() # Initialise les tables au démarrage
