import os
import re
import cv2
import pytesseract
from pdf2image import convert_from_path

from .processors.bilan import BilanProcessor
from .processors.facture import FactureProcessor
from .processors.devis import DevisProcessor
from .processors.attestation import AttestationProcessor
from .utils.cleaner import AmountCleaner
from .classifier import MLClassifier

class OCRAnalyzer:
    def __init__(self):
        self.classifier = MLClassifier()
        # DocTR est remplacé par Pytesseract pour la légèreté de l'image Docker
        self.processors = [
            BilanProcessor(),
            FactureProcessor(),
            DevisProcessor(),
            AttestationProcessor()
        ]

    def analyze(self, filepath, filename, element_id):
        full_text = ""
        try:
            if filename.lower().endswith('.pdf'):
                pages = convert_from_path(filepath, dpi=200)
                for page in pages:
                    text = pytesseract.image_to_string(page, lang="fra")
                    full_text += text + " \n"
            else:
                img = cv2.imread(filepath)
                text = pytesseract.image_to_string(img, lang="fra")
                full_text = text
        except Exception as e:
            from loguru import logger
            logger.error(f"Erreur Tesseract sur {filepath}: {e}")
            return {"element_id": element_id, "statut": "erreur", "description": "Format non supporté"}
        
        text_up = full_text.upper()
        clean_tech_text = re.sub(r'[\s\-\.]', '', text_up)

        # Routage ML robuste (Random Forest)
        predicted_type = self.classifier.predict(full_text)
        
        data = None
        for processor in self.processors:
            # On cherche le processeur qui correspond au type prédit par ML
            # Au lieu du vieux `can_handle()` bête
            proc_name = processor.__class__.__name__.lower().replace("processor", "")
            if predicted_type == proc_name:
                data = processor.process(None, text_up)
                break

        # Si ML fail ou type "autre", on fait une extraction par défaut
        if data is None or (data.get("document_type", "autre") == "autre" and data.get("montant_ttc", 0) == 0):
            all_prices = [AmountCleaner.clean(a) for a in re.findall(r'(\d+[.,]\d{2})', text_up) if len(a.replace(',','').replace('.','')) <= 7]
            val_max = max(all_prices) if all_prices else 0.0
            data = {
                "document_type": predicted_type if predicted_type != "autre" else "autre",
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

        result_dict = {
            "element_id": element_id,
            "document_type": data.get("document_type", "autre"),
            "siret": siret_final,
            "date_validation": data.get("date_validation", "N/A"),
            "statut": "valide" if data.get("document_type") != "autre" else "anomalie",
            "description": filename,
            "raw_text": full_text
        }

        # Add specific fields based on type
        doc_type = data.get("document_type")
        if doc_type == "facture":
            result_dict.update({
                "montant_ht": data.get("montant_ht", 0.0),
                "montant_ttc": data.get("montant_ttc", 0.0),
                "montant_tva": data.get("montant_tva", 0.0),
                "tva": tva_final,
                "devise": data.get("devise", "EUR"),
                "justificatif_url": f"https://intranet.myleasy.com/api/ndf/file/{filename}"
            })
        elif doc_type == "bilan":
            result_dict.update({
                "total_actif": data.get("total_actif", 0.0),
                "total_passif": data.get("total_passif", 0.0),
                "resultat_net": data.get("resultat_net", 0.0),
                "devise": data.get("devise", "EUR")
            })
        elif doc_type == "devis":
            result_dict.update({
                "montant_total": data.get("montant_total", 0.0),
                "devise": data.get("devise", "EUR")
            })
        elif doc_type == "attestation":
            result_dict.update({
                "date_expiration_attestation": data.get("date_expiration_attestation", "N/A")
            })

        return result_dict