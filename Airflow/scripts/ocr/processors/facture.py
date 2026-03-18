import re
from .base import DocumentProcessor
from utils.cleaner import AmountCleaner

class FactureProcessor(DocumentProcessor):
    def __init__(self):
        self.ttc_patterns = [
            r'(?:TOTAL TTC|NET A PAYER|À PAYER|TOTAL A PAYER|TOTAL DUE|MONTANT TTC|TOTAL|PRIX TOTAL|SOMME|SOLDE)\s*[:]*\s*(?:€|EUR|[$])?\s*([\d\s]+[.,]\d{2})',
            r'PORTANT SUR UN TOTAL DE\s*([\d\s]+[.,]\d{2})',
            r'DONT\s*([\d\s]+[.,]\d{2})\s*(?:€|EUR|[$])\s*TTC'
        ]
        self.ht_patterns = [
            r'(?:TOTAL HT|MONTANT HT|BASE HT|NET HT|TOTAL NET HT)\s*[:]*\s*(?:€|EUR|[$])?\s*([\d\s]+[.,]\d{2})'
        ]
        self.tva_multi_pattern = r'(?:TVA|DONT TVA|MONTANT TVA)\s*(?:\d*[.,]?\d*\s*%?)?\s*[:]*\s*(?:€|EUR|[$])?\s*([\d\s]+[.,]\d{2})'

    def can_handle(self, text_up: str) -> bool:
        if any(k in text_up for k in ["BILAN", "LIASSE FISCALE", "TABLEAU DES FILIALES", "ACTIF", "PASSIF"]):
            return False
        keywords = ["FACTURE", "INVOICE", "NOTE DE FRAIS", "REÇU", "QUITTANCE", "TTC", "TVA", "ULYS", "VINCI", "TICKET", "PAIEMENT", "COMMANDE", "TOTAL"]
        return any(k in text_up for k in keywords) or len(re.findall(r'\d+[.,]\d{2}', text_up)) > 0

    def process(self, result, text_up: str) -> dict:
        clean_tech = re.sub(r'[^A-Z0-9]', '', text_up)

        siret_matches = re.findall(r'\d{14}', clean_tech)
        siret_final = next((s for s in siret_matches if not s.startswith("250")), "N/A")

        all_matches = re.findall(r'(\d+[\s.,]\d{2})(?!\d)', text_up)
        all_amounts = [AmountCleaner.clean(a) for a in all_matches]

        credible_amounts = [a for a in all_amounts if 0.40 < a < 1000]

        m_ttc = self._extract_regex(self.ttc_patterns, text_up)
        m_ht = self._extract_regex(self.ht_patterns, text_up)
        
        if credible_amounts:
            last_amount = credible_amounts[-1]
            
            if m_ttc == 0 or (m_ttc not in credible_amounts) or (m_ttc < max(credible_amounts) * 0.1):
                 m_ttc = last_amount

        tva_matches = re.findall(self.tva_multi_pattern, text_up, re.IGNORECASE)
        tva_list = [AmountCleaner.clean(val) for val in tva_matches if AmountCleaner.clean(val) < m_ttc]
        m_tva_total = sum(list(set(tva_list)))

        if m_ttc > 0:
            if 0 < m_ht < m_ttc and (m_ttc - m_ht) < (m_ttc * 0.3): 
                m_tva_total = round(m_ttc - m_ht, 2)
            elif 0 < m_tva_total < m_ttc:
                m_ht = round(m_ttc - m_tva_total, 2)
            else:
                m_ht = round(m_ttc / 1.2, 2)
                m_tva_total = round(m_ttc - m_ht, 2)

        date_match = re.search(r'(\d{2}[/.-]\d{2}[/.-]\d{4})', text_up)
        tva_intra_m = re.search(r'FR[0-9]{11}', clean_tech)

        return {
            "document_type": "facture",
            "montant_ht": round(max(0.0, m_ht), 2),
            "montant_tva": round(max(0.0, m_tva_total), 2),
            "montant_ttc": round(max(0.0, m_ttc), 2),
            "tva": tva_intra_m.group(0) if tva_intra_m else "N/A",
            "date_validation": date_match.group(1) if date_match else "N/A",
            "siret": siret_final,
            "devise": "USD" if "$" in text_up or "USD" in text_up else "EUR"
        }

    def _extract_regex(self, patterns, text):
        for p in patterns:
            matches = re.findall(p, text, re.IGNORECASE)
            if matches:
                vals = [AmountCleaner.clean(m) for m in matches]
                valid_vals = [v for v in vals if 0.5 < v < 1500]
                if valid_vals:
                    return valid_vals[-1]
        return 0.0