import os
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "documents_db"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_tables():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    email VARCHAR(255) PRIMARY KEY,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
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
    except pymysql.MySQLError:
        pass
    finally:
        conn.close()

init_tables() # Initialise les tables au démarrage
