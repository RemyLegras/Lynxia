import os
import torch
import numpy as np
import re
from doctr.models import ocr_predictor 
from doctr.io import DocumentFile

from .processors.bilan import BilanProcessor
from .processors.facture import FactureProcessor
from .processors.devis import DevisProcessor
from .processors.attestation import AttestationProcessor
from .utils.cleaner import AmountCleaner

DEVICE = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")

class OCRAnalyzer:
    def __init__(self):
        self.predictor = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True).to(DEVICE)
        self.processors = [
            BilanProcessor(),
            FactureProcessor(),
            DevisProcessor(),
            AttestationProcessor()
        ]

    def analyze(self, filepath, filename, element_id):
        try:
            doc = DocumentFile.from_pdf(filepath) if filename.lower().endswith('.pdf') else DocumentFile.from_images(filepath)
        except:
            return {"element_id": element_id, "statut": "erreur", "description": "Format non supporté"}

        result = self.predictor(doc)
        
        full_text = ""
        for page in result.pages:
            for block in page.blocks:
                for line in block.lines:
                    full_text += " ".join([w.value for w in line.words]) + " "
            full_text += "\n"
        
        text_up = full_text.upper()
        clean_tech_text = re.sub(r'[\s\-\.]', '', text_up)

        # Routage
        data = None
        for processor in self.processors:
            if processor.can_handle(text_up):
                data = processor.process(result, text_up)
                break

        if data is None or (data.get("document_type") == "autre" and data.get("montant_ttc") == 0):
            all_prices = [AmountCleaner.clean(a) for a in re.findall(r'(\d+[.,]\d{2})', text_up) if len(a.replace(',','').replace('.','')) <= 7]
            val_max = max(all_prices) if all_prices else 0.0
            data = {
                "document_type": "autre",
                "montant_ttc": val_max,
                "montant_ht": round(val_max / 1.2, 2),
                "montant_tva": round(val_max - (val_max / 1.2), 2)
            }

        siret_final = data.get("siret", "N/A")
        if siret_final == "N/A":
            siret_m = re.search(r'\d{14}', clean_tech_text)
            siret_final = siret_m.group(0) if siret_m else "N/A"

        tva_final = data.get("tva", "N/A")
        if tva_final == "N/A" and data.get("document_type") == "facture":
            siret_digits = re.sub(r'\D', '', siret_final) 
            if len(siret_digits) >= 9:
                tva_final = f"FR{siret_digits[:9]}"

        return {
            "element_id": element_id,
            "document_type": data.get("document_type", "autre"),
            "siret": siret_final,
            "tva": tva_final,
            "montant_ht": data.get("montant_ht", 0.0),
            "montant_ttc": data.get("montant_ttc", 0.0),
            "montant_tva": data.get("montant_tva", 0.0),
            "devise": data.get("devise", "EUR"),
            "date_validation": data.get("date_validation", "N/A"),
            "date_expiration_attestation": data.get("date_expiration_attestation", "N/A"),
            "statut": "valide" if data.get("document_type") != "autre" else "anomalie",
            "description": filename,
            "justificatif_url": f"https://intranet.myleasy.com/api/ndf/file/{filename}"
        }