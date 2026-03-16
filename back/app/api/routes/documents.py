from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.document import Document, DocumentCuratedData
from app.auth_utils import get_current_user
from app.services.document_service import create_document, get_document, get_user_documents, update_document

router = APIRouter()

def check_access(doc_id: str, user_email: str):
    doc = get_document(doc_id)
    if not doc or doc["owner_user_id"] != user_email:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return doc

@router.post("/", response_model=Document)
def create_doc(document: Document, current_user: dict = Depends(get_current_user)):
    return Document(**create_document({
        "document_type": document.document_type,
        "curated_data": document.curated_data.dict(),
        "status": "processed",
        "raw_path": document.raw_path,
        "clean_text_ref": document.clean_text_ref,
        "inconsistencies": document.inconsistencies or []
    }, current_user["email"]))

@router.get("/", response_model=List[Document])
def list_docs(limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)):
    docs = get_user_documents(current_user["email"])
    return [Document(**doc) for doc in docs[offset:offset + limit]]

@router.get("/{document_id}", response_model=Document)
def get_doc(document_id: str, current_user: dict = Depends(get_current_user)):
    return Document(**check_access(document_id, current_user["email"]))

@router.post("/{document_id}/curated-data")
def update_curated(document_id: str, curated_data: DocumentCuratedData, current_user: dict = Depends(get_current_user)):
    check_access(document_id, current_user["email"])
    update_document(document_id, {
        "curated_data": curated_data.dict(),
        "status": "processed"
    })
    return {"message": "Données mises à jour", "document": Document(**get_document(document_id))}