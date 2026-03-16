from app.database import get_mysql_connection
import json
import uuid
from datetime import datetime

def parse_json_fields(result):
    """Convertit les champs JSON en dict Python"""
    if result and result.get("curated_data"):
        result["curated_data"] = json.loads(result["curated_data"])
    if result and result.get("inconsistencies"):
        result["inconsistencies"] = json.loads(result["inconsistencies"])
    return result

def create_document(doc_data: dict, owner_email: str):
    """Crée un nouveau document"""
    doc_id = str(uuid.uuid4())[:8]
    
    document = {
        "element_id": doc_id,
        "owner_user_id": owner_email,
        "document_type": doc_data.get("document_type"),
        "curated_data": doc_data.get("curated_data", {}),
        "status": doc_data.get("status", "uploaded"),
        "raw_path": doc_data.get("raw_path"),
        "clean_text_ref": doc_data.get("clean_text_ref"),
        "inconsistencies": doc_data.get("inconsistencies", []),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO documents (element_id, owner_user_id, document_type, curated_data, status, raw_path, clean_text_ref, inconsistencies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                document["element_id"],
                document["owner_user_id"],
                document["document_type"],
                json.dumps(document["curated_data"]),
                document["status"],
                document["raw_path"],
                document["clean_text_ref"],
                json.dumps(document["inconsistencies"])
            ))
        conn.commit()
        return document
    finally:
        conn.close()

def get_document(doc_id: str):
    """Récupère un document par ID"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE element_id = %s", (doc_id,))
            result = cursor.fetchone()
            return parse_json_fields(result)
    finally:
        conn.close()

def get_user_documents(email: str):
    """Récupère tous les documents d'un utilisateur"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE owner_user_id = %s", (email,))
            results = cursor.fetchall()
            return [parse_json_fields(result) for result in results]
    finally:
        conn.close()

def update_document(doc_id: str, updates: dict):
    """Met à jour un document"""
    conn = get_mysql_connection()
    try:
        with conn.cursor() as cursor:
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ["curated_data", "inconsistencies"]:
                    set_clauses.append(f"{key} = %s")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if set_clauses:
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(doc_id)
                
                query = f"UPDATE documents SET {', '.join(set_clauses)} WHERE element_id = %s"
                cursor.execute(query, values)
        conn.commit()
        return True
    finally:
        conn.close()
