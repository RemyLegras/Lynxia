import re

class AmountCleaner:
    @staticmethod
    def clean(text):
        if not text: return 0.0
        # Supprime tout sauf chiffres, points, virgules et signe moins
        clean = re.sub(r'[^-0-9,.]', '', text)
        if ',' in clean and '.' in clean:
            clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            clean = clean.replace(',', '.')
        elif '.' in clean and len(clean.split('.')[-1]) == 3:
            # Cas des milliers : 1.250 -> 1250
            clean = clean.replace('.', '')
        try:
            return float(clean)
        except:
            return 0.0