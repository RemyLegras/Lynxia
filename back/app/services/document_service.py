from app.database import get_connection
import json
import uuid


def _deserialize_document_row(row: dict | None):
    if not row:
        return row

    if row.get("curated_data"):
        row["curated_data"] = json.loads(row["curated_data"])
    if row.get("inconsistencies"):
        row["inconsistencies"] = json.loads(row["inconsistencies"])

    return row

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


def get_user_document_stats(email: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_documents,
                    SUM(CASE WHEN status = 'uploaded' THEN 1 ELSE 0 END) AS uploaded_documents,
                    SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) AS processed_documents,
                    COUNT(DISTINCT document_type) AS distinct_document_types
                FROM documents
                WHERE owner_user_id = %s
                """,
                (email,),
            )
            summary = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT document_type, COUNT(*) AS total
                FROM documents
                WHERE owner_user_id = %s
                GROUP BY document_type
                ORDER BY total DESC
                """,
                (email,),
            )
            by_type = cursor.fetchall() or []

            return {
                "total_documents": int(summary.get("total_documents") or 0),
                "uploaded_documents": int(summary.get("uploaded_documents") or 0),
                "processed_documents": int(summary.get("processed_documents") or 0),
                "distinct_document_types": int(summary.get("distinct_document_types") or 0),
                "documents_by_type": by_type,
            }
    finally:
        conn.close()

def get_document(doc_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE element_id = %s", (doc_id,))
            result = cursor.fetchone()
            return _deserialize_document_row(result)
    finally:
        conn.close()

def get_user_documents(email: str, status: str | None = None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if status:
                cursor.execute(
                    "SELECT * FROM documents WHERE owner_user_id = %s AND status = %s ORDER BY created_at DESC",
                    (email, status),
                )
            else:
                cursor.execute(
                    "SELECT * FROM documents WHERE owner_user_id = %s ORDER BY created_at DESC",
                    (email,),
                )
            results = cursor.fetchall()
            return [_deserialize_document_row(r) for r in results]
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
