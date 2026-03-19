import re
from .base import DocumentProcessor
from ..utils.cleaner import AmountCleaner

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
        # Recherche des mots-clés de totaux dans le texte brut
        for keyword in keywords_total:
            # On cherche le mot clé suivi d'un montant sur la même ligne
            match = re.search(rf"{keyword}.*?(\d[\d\s.,]+)", text_upper)
            if match:
                val = AmountCleaner.clean(match.group(1))
                if val > 2030 or (val > 0 and val < 1900): # Éviter les dates et petits chiffres
                    selected_amount = val
                    found_amount = True
                    break
        
        # Fallback : si rien trouvé via mots-clés, on cherche le plus gros montant plausible
        if not found_amount:
            all_numbers = re.findall(r'(\d+[\s.,]\d{2})', text_upper)
            amounts = [AmountCleaner.clean(n) for n in all_numbers]
            valid_amounts = [a for a in amounts if 1000 < a < 1000000]
            if valid_amounts:
                selected_amount = max(valid_amounts)


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
            "total_actif": selected_amount,
            "total_passif": selected_amount,
            "resultat_net": 0.0, # Pourrait être extrait séparément
            "date_validation": date_cloture,
            "devise": "EUR"
        }