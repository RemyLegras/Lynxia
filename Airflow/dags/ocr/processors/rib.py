import re
from .base import DocumentProcessor

class RIBProcessor(DocumentProcessor):
    def can_handle(self, text_up: str) -> bool:
        banques = ["BOURSORAMA", "SOCIETE GENERALE", "BNP PARIBAS", "CREDIT AGRICOLE", 
                   "REVOLUT", "HELLO BANK", "LCL", "CAISSE D'EPARGNE", "BANQUE POPULAIRE",
                   "MUTUEL", "N26", "MONZO", "QONTO", "SHINE"]
        keywords = ["RIB", "IBAN", "IDENTITE BANCAIRE", "RELEVE D'IDENTITE"]
        return any(k in text_up for k in keywords) or any(b in text_up for b in banques)

    def process(self, result, text_up: str) -> dict:
        clean_text = re.sub(r'[^A-Z0-9]', '', text_up)
        
        iban_m = re.search(r'FR[0-9]{2}[0-9A-Z]{23}', clean_text)
        iban_val = "N/A"
        if iban_m:
            raw = iban_m.group(0)
            iban_val = ' '.join(raw[i:i+4] for i in range(0, len(raw), 4)) 

        return {
            "document_type": "rib",
            "iban": iban_val,
            "montant_ttc": 0.0,
            "date_validation": "N/A",
            "siret": "N/A"
        }