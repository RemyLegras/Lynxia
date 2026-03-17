from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class DocumentCuratedData(BaseModel):
    siret: str = Field(..., description="Numéro SIRET de l'entreprise")
    tva: str = Field(..., description="Numéro de TVA intracommunautaire")
    montant_ht: float = Field(..., description="Montant hors taxes")
    montant_ttc: float = Field(..., description="Montant toutes taxes comprises")
    montant_tva: str = Field(..., description="Montant de la TVA")
    devise: str = Field(default="EUR", description="Devise")
    date_frais: Optional[date] = Field(None, description="Date des frais")
    date_validation: Optional[date] = Field(None, description="Date de validation du document")
    date_expiration_attestation: Optional[date] = Field(None, description="Date d'expiration de l'attestation")
    statut: str = Field(..., description="Statut du document")
    description: Optional[str] = Field(None, description="Description")
    justificatif_url: Optional[str] = Field(None, description="URL du justificatif")

class Document(BaseModel):
    element_id: str = Field(..., description="ID unique du document")
    document_type: str = Field(..., description="Type de document (facture, devis, attestation, etc.)")
    curated_data: DocumentCuratedData = Field(..., description="Données structurées extraites")
    
    # Métadonnées système
    owner_user_id: Optional[str] = Field(None, description="ID du propriétaire")
    status: str = Field(default="uploaded", description="Statut de traitement")
    raw_path: Optional[str] = Field(None, description="Chemin fichier brut (raw zone)")
    clean_text_ref: Optional[str] = Field(None, description="Référence texte OCR (clean zone)")
    inconsistencies: Optional[list] = Field(default=[], description="Liste des incohérences détectées")
    created_at: Optional[str] = Field(None, description="Date de création")
    updated_at: Optional[str] = Field(None, description="Date de mise à jour")
