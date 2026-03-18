class ExpertDetector:
    @staticmethod
    def is_expert(text_up):
        keywords = ["CABINET", "EXPERTISE", "AUDIT", "AVOCAT", "CONSEIL", "AGC", "COMPTABILITE"]
        return any(k in text_up for k in keywords)