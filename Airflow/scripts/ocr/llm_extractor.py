import os
import json
from openai import OpenAI
from loguru import logger

# Configuration Ollama via l'URL envoyée par l'utlisateur
OLLAMA_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
# Ollama ignore la clé, mais openai SDK en réclame une par défaut
OLLAMA_API_KEY = os.getenv("LLM_API_KEY", "ollama")
OLLAMA_MODEL = os.getenv("LLM_MODEL", "llama3") # Le modèle doit être pullé sur le serveur Ollama.

client = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key=OLLAMA_API_KEY
)

PROMPT_TEMPLATE = """Tu es un expert-comptable expert en extraction de données structurées.
Analyse le texte OCR et renvoie un JSON dont la structure dépend du type de document détecté.

### RÈGLES DE STRUCTURE ###
1. Si c'est une FACTURE :
{
  "document_type": "facture",
  "siret": "14 chiffres",
  "tva": "FR...",
  "montant_ht": 0.0,
  "montant_tva": 0.0,
  "montant_ttc": 0.0,
  "date_validation": "JJ/MM/AAAA",
  "iban": "FR..."
}

2. Si c'est un BILAN :
{
  "document_type": "bilan",
  "siret": "14 chiffres",
  "total_actif": 0.0,
  "total_passif": 0.0,
  "resultat_net": 0.0,
  "date_validation": "JJ/MM/AAAA"
}

3. Si c'est un DEVIS :
{
  "document_type": "devis",
  "siret": "14 chiffres",
  "montant_total": 0.0,
  "tva": "FR...",
  "montant_ht": 0.0,
  "montant_tva": 0.0,
  "montant_ttc": 0.0,
  "date_validation": "JJ/MM/AAAA"
}

Règles impératives :
- Réponse STRICTEMENT en JSON. Aucun texte avant ou après.
- Dates en JJ/MM/AAAA.

Met un pourcentage de confiance pour chaque document dans le json sous la clé "confidence". 


### EXEMPLE BILAN ###
Texte : "BILAN COMPTABLE 2024 SIRET 12345678900012 TOTAL ACTIF 500000 TOTAL PASSIF 500000"
JSON : { "confidence": 0.95,
"document_type": "bilan",
"siret": "12345678900012",
"total_actif": 500000.0,
"total_passif": 500000.0, 
"resultat_net": 0.0, 
"date_validation": "01/01/2024"}

### DOCUMENT A TRAITER ###
OCR : {ocr_text}
"""

def extract_with_llm(ocr_text: str) -> dict:
    """
    Envoie le texte brut à l'LLM (Ollama) et attend une réponse JSON structurée.
    """
    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "You are a specialized JSON parser."},
                {"role": "user", "content": PROMPT_TEMPLATE.replace("{ocr_text}", ocr_text)}
            ],
            temperature=0.0,
            # Certains modèles supportent response_format, sinon on force via le prompt
            # response_format={ "type": "json_object" } 
        )
        
        result_content = response.choices[0].message.content.strip()
        
        # Nettoyage d'éventuels backticks markdown `json ... `
        if result_content.startswith("```"):
            result_content = result_content.strip("`").replace("json\n", "", 1)
        if result_content.startswith("```json"):
            result_content = result_content[7:-3]
            
        data = json.loads(result_content)
        return data
        
    except Exception as e:
        logger.error(f"Fallback : Erreur lors de l'appel LLM: {str(e)}")
        return None
