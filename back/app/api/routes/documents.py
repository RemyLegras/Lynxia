from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List
from app.schemas.document import Document, DocumentCuratedData
from app.auth_utils import get_current_user
from app.services.document_service import create_document, get_document, get_user_documents, update_document
from app.services.minio_service import upload_file_to_minio, download_file_from_minio
import os
import uuid
from pathlib import Path

router = APIRouter()
UPLOAD_DIR = Path("uploads/raw")

def check_access(doc_id: str, user_email: str):
    doc = get_document(doc_id)
    if not doc or doc["owner_user_id"] != user_email:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return doc

@router.post("/upload")
async def upload_doc(
    file: UploadFile = File(...),
    document_type: str = Form("unknown"),
    current_user: dict = Depends(get_current_user),
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_ext = Path(file.filename).suffix
    saved_name = f"{uuid.uuid4().hex}{file_ext}"
    saved_path = UPLOAD_DIR / saved_name

    with saved_path.open("wb") as f:
        f.write(await file.read())

    upload_success = upload_file_to_minio(saved_name, str(saved_path))
    if upload_success:
        os.remove(str(saved_path)) # clean up local

    created = create_document(
        {
            "document_type": document_type,
            "curated_data": {},
            "status": "uploaded",
            "raw_path": saved_name if upload_success else str(saved_path),
            "clean_text_ref": None,
            "inconsistencies": [],
        },
        current_user["email"],
    )

    return {
        "message": "Fichier uploadé",
        "document": created,
    }

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

@router.get("/my-uploads", response_model=List[Document])
def list_my_uploaded_docs(limit: int = 50, offset: int = 0, current_user: dict = Depends(get_current_user)):
    docs = get_user_documents(current_user["email"], status="uploaded")
    return [Document(**doc) for doc in docs[offset:offset + limit]]

@router.get("/{document_id}", response_model=Document)
def get_doc(document_id: str, current_user: dict = Depends(get_current_user)):
    return Document(**check_access(document_id, current_user["email"]))

@router.get("/{document_id}/download")
def download_doc(document_id: str, current_user: dict = Depends(get_current_user)):
    doc = check_access(document_id, current_user["email"])
    raw_path = doc.get("raw_path")

    if not raw_path:
        raise HTTPException(status_code=404, detail="Aucun fichier brut associé")

    dest_path = f"/tmp/{Path(raw_path).name}"
    
    if download_file_from_minio(raw_path, dest_path):
        return FileResponse(dest_path, filename=Path(raw_path).name)

    if os.path.exists(raw_path):
        return FileResponse(raw_path, filename=Path(raw_path).name)

    raise HTTPException(status_code=404, detail="Fichier introuvable")

@router.post("/{document_id}/curated-data")
def update_curated(document_id: str, curated_data: DocumentCuratedData, current_user: dict = Depends(get_current_user)):
    check_access(document_id, current_user["email"])
    update_document(document_id, {
        "curated_data": curated_data.dict(),
        "status": "processed"
    })
    return {"message": "Données mises à jour", "document": Document(**get_document(document_id))}