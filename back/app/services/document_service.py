from app.database import get_connection
import json
import uuid

def create_document(doc_data: dict, owner_email: str):
    doc_id = str(uuid.uuid4())[:8]
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO documents (element_id, owner_user_id, document_type, curated_data, status, raw_path, clean_text_ref, inconsistencies)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc_id,
                owner_email,
                doc_data.get("document_type"),
                json.dumps(doc_data.get("curated_data", {})),
                doc_data.get("status", "uploaded"),
                doc_data.get("raw_path"),
                doc_data.get("clean_text_ref"),
                json.dumps(doc_data.get("inconsistencies", []))
            ))
        conn.commit()
        
        return {
            "element_id": doc_id,
            "owner_user_id": owner_email,
            "document_type": doc_data.get("document_type"),
            "curated_data": doc_data.get("curated_data", {}),
            "status": doc_data.get("status", "uploaded"),
            "raw_path": doc_data.get("raw_path"),
            "clean_text_ref": doc_data.get("clean_text_ref"),
            "inconsistencies": doc_data.get("inconsistencies", [])
        }
    finally:
        conn.close()

def get_document(doc_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE element_id = %s", (doc_id,))
            result = cursor.fetchone()
            if result and result.get("curated_data"):
                result["curated_data"] = json.loads(result["curated_data"])
            if result and result.get("inconsistencies"):
                result["inconsistencies"] = json.loads(result["inconsistencies"])
            return result
    finally:
        conn.close()

def get_user_documents(email: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE owner_user_id = %s", (email,))
            results = cursor.fetchall()
            for r in results:
                if r.get("curated_data"):
                    r["curated_data"] = json.loads(r["curated_data"])
                if r.get("inconsistencies"):
                    r["inconsistencies"] = json.loads(r["inconsistencies"])
            return results
    finally:
        conn.close()

def update_document(doc_id: str, updates: dict):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            set_parts = []
            values = []
            
            for key, value in updates.items():
                if key in ["curated_data", "inconsistencies"]:
                    value = json.dumps(value)
                set_parts.append(f"{key} = %s")
                values.append(value)
            
            values.append(doc_id)
            cursor.execute(f"UPDATE documents SET {', '.join(set_parts)} WHERE element_id = %s", values)
        conn.commit()
        return True
    finally:
        conn.close()
