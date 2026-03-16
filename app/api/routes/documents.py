from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.document import Document, DocumentCuratedData
from app.utils.auth import get_current_user
from app.services.document_service import create_document, get_document, get_user_documents, update_document

router = APIRouter()

@router.post("/", response_model=Document)
def create_document_metadata(
    document: Document,
    current_user: dict = Depends(get_current_user)
):
    """Crée les métadonnées d'un document (le fichier est géré par le datalake)"""
    doc_data = {
        "document_type": document.document_type,
        "curated_data": document.curated_data.dict(),
        "status": "processed",
        "raw_path": document.raw_path,
        "clean_text_ref": document.clean_text_ref,
        "inconsistencies": document.inconsistencies or []
    }
    
    created_doc = create_document(doc_data, current_user["email"])
    return Document(**created_doc)

@router.get("/", response_model=List[Document])
def get_documents(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Liste les documents de l'utilisateur connecté"""
    user_docs = get_user_documents(current_user["email"])
    
    # Pagination
    paginated_docs = user_docs[offset:offset + limit]
    
    return [Document(**doc) for doc in paginated_docs]

@router.get("/{document_id}", response_model=Document)
def get_document_by_id(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Détail d'un document"""
    doc = get_document(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    if doc.get("owner_user_id") != current_user["email"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return Document(**doc)

@router.post("/{document_id}/curated-data")
def update_curated_data(
    document_id: str,
    curated_data: DocumentCuratedData,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour les données structurées (après traitement datalake)"""
    doc = get_document(document_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    
    if doc.get("owner_user_id") != current_user["email"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Mettre à jour les données structurées
    updates = {
        "curated_data": curated_data.dict(),
        "status": "processed"
    }
    
    update_document(document_id, updates)
    
    updated_doc = get_document(document_id)
    return {"message": "Données structurées mises à jour", "document": Document(**updated_doc)}