import re
from .base import DocumentProcessor
from utils.cleaner import AmountCleaner

class BilanProcessor(DocumentProcessor):
    def can_handle(self, text_up: str) -> bool:
        return any(k in text_up for k in ["BILAN", "LIASSE", "PASSIF", "COMPTES ANNUELS", "COMPTE DE RÉSULTAT"])

    def process(self, result, text_up: str) -> dict:
        selected_amount = 0.0
        text_upper = text_up.upper()
        
        siret = "N/A"
        siret_match = re.search(r"SIRET[:\s]*(\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d[\s.]?\d)", text_upper)
        if siret_match:
            siret = re.sub(r"[\s.]", "", siret_match.group(1))
        
        keywords_total = ["TOTAL DE L'ACTIF", "TOTAL DU PASSIF", "TOTAL DES PRODUITS", "TOTAL DES CHARGES", "BÉNÉFICE", "RÉSULTAT"]
        
        found_amount = False
        for page in result.pages:
            if found_amount: break  
            
            for block in page.blocks:
                for line in block.lines:
                    words = line.words
                    if not words: continue
                    
                    full_line_text = " ".join([w.value for w in words]).upper()
                    
                    if any(k in full_line_text for k in keywords_total):
                        reconstructed_cols = []
                        current_col = words[0].value
                        
                        for i in range(1, len(words)):
                            current_word_end = words[i-1].geometry[1][0]
                            next_word_start = words[i].geometry[0][0]
                            
                            if (next_word_start - current_word_end) > 0.02:
                                reconstructed_cols.append(current_col)
                                current_col = words[i].value
                            else:
                                current_col += " " + words[i].value
                        reconstructed_cols.append(current_col)

                        for col in reconstructed_cols:
                            clean_col = re.sub(r'(?<=\d)\s+(?=\d{3}\b)', '', col)
                            numbers = re.findall(r'-?\d+[.,]?\d*', clean_col)
                            
                            for num in numbers:
                                val = AmountCleaner.clean(num)
                                if val > 2030 or (val > 0 and val < 1900):
                                    selected_amount = val
                                    found_amount = True
                                    break
                            if found_amount: break
                    if found_amount: break

        date_cloture = "N/A"
        date_patterns = [
            r"CLOS\s+LE\s+(\d{2}[/.-]\d{2}[/.-]\d{4})",
            r"ARRÊTÉ\s+(?:DES\s+COMPTES\s+)?AU\s+(\d{2}[/.-]\d{2}[/.-]\d{4})",
            r"SITUATION\s+ARRÊTÉE\s+AU\s+(\d{2}[/.-]\d{2}[/.-]\d{4})",
            r"CLÔTURE\s+AU\s+(\d{2}[/.-]\d{2}[/.-]\d{4})",
            r"EXERCICE\s+AU\s+(\d{2}[/.-]\d{2}[/.-]\d{4})",
            r"AU\s+(\d{2}[/.-]\d{2}[/.-]\d{4})"
        ]
        for p in date_patterns:
            match = re.search(p, text_upper)
            if match:
                date_cloture = match.group(1)
                break

        return {
            "document_type": "bilan",
            "siret": siret,
            "tva": "N/A",
            "montant_ht": selected_amount,
            "montant_tva": 0.0,
            "montant_ttc": selected_amount,
            "date_validation": date_cloture,
            "devise": "EUR"
        }