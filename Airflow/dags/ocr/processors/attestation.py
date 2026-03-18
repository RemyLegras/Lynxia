import re
from .base import DocumentProcessor

class AttestationProcessor(DocumentProcessor):
    def can_handle(self, text_up: str) -> bool:
        keywords = ["ATTESTATION", "VIGILANCE", "ASSURANCE", "DECENNALE", "CERTIFICAT"]
        return any(k in text_up for k in keywords)

    def process(self, result, text_up: str) -> dict:

        dates = re.findall(r'(\d{2}[/.-]\d{2}[/.-]\d{4})', text_up)
        
        date_exp = "N/A"
        if len(dates) >= 2: date_exp = dates[1]
        
        siret_match = re.search(r'\d{14}', text_up.replace(" ", ""))

        return {
            "document_type": "attestation",
            "montant_ht": 0.0,
            "montant_tva": 0.0,
            "montant_ttc": 0.0,
            "devise": "EUR",
            "date_validation": dates[0] if dates else "N/A",
            "date_expiration_attestation": date_exp,
            "siret": siret_match.group(0) if siret_match else "N/A"
        }