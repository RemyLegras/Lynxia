import re
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class MLClassifier:
    """
    A simple TF-IDF + Random Forest classifier to categorize documents.
    In a real scenario, this would be trained on a large dataset and loaded from a .pkl file.
    Here we train a small simulated model on initialization if no save file exists.
    """
    def __init__(self, model_path="/opt/airflow/data/rf_model.pkl"):
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words=['le', 'la', 'les', 'de', 'des', 'un', 'une'])
        self.classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectorizer = data['vectorizer']
                    self.classifier = data['classifier']
                    self.is_trained = True
                return
            except Exception as e:
                from loguru import logger
                logger.warning(f"Could not load model: {e}. Retraining...")

        # Simulated training data
        texts = [
            "FACTURE N° 1234 Total TTC 150.00 EUR TVA 20% Siret 12345678900012 A payer",
            "INVOICE #9983 Amount due 500$ Tax included",
            "REÇU de paiement carte bancaire montant 12.50",
            "Facture de prestation de service informatique",
            "DEVIS estimatif pour travaux de rénovation Total HT 5000 Bon pour accord",
            "Proposition commerciale devis chauffage",
            "Devis n° 2026-45 pour installation électrique",
            "BILAN COMPTABLE ACTIF PASSIF IMMOBILISATIONS CAPITAUX PROPRES",
            "LIASSE FISCALE comptes annuels exercice clos résultat",
            "Bilan simplifié exercice 2023",
            "COMPTE DE RÉSULTAT ET BILAN",
            "Attestation de vigilance URSSAF cotisations sociales",
            "Attestation fiscale de régularité impôts",
            "Certificat de conformité",
            "Menu du restaurant du coin",
            "Lettre de motivation suite à l'annonce",
            "Ceci est un document inconnu"
        ]
        labels = [
            "facture", "facture", "facture", "facture",
            "devis", "devis", "devis",
            "bilan", "bilan", "bilan", "bilan",
            "attestation", "attestation", "attestation",
            "autre", "autre", "autre"
        ]
        
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_trained = True

        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({'vectorizer': self.vectorizer, 'classifier': self.classifier}, f)
        except Exception:
            pass # Ignore if we can't save in current env

    def clean_text(self, text):
        return re.sub(r'[^a-zA-Z0-9\s€]', ' ', text.lower())

    def predict(self, raw_text):
        if not self.is_trained or not raw_text.strip():
            return "autre"
        
        cleaned = self.clean_text(raw_text)
        X = self.vectorizer.transform([cleaned])
        
        # Get probabilities to apply a confidence threshold
        probs = self.classifier.predict_proba(X)[0]
        max_prob = max(probs)
        pred_class = self.classifier.classes_[probs.argmax()]
        
        if max_prob < 0.35: # Low confidence fallback
            return "autre"
            
        return pred_class
