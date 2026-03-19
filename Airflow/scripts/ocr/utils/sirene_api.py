import requests
from loguru import logger

def fetch_sirene_info(siret):
    """
    Appelle l'API SIRENE gratuite du gouvernement pour vérifier l'existence de l'entreprise.
    Renvoie un dictionnaire avec { "is_valid": bool, "company_name": str, "address": str }
    """
    if not siret or len(siret) < 9:
        return {"is_valid": False, "company_name": None, "address": None}

    # On utilise la base SIREN / SIRET officielle (recherche d'entreprise gratuite)
    # SIRET = 14 chiffres, SIREN = 9 chiffres. L'API recherche par siren/siret sans token auth
    url = f"https://recherche-entreprises.api.gouv.fr/search?q={siret}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return {
                    "is_valid": True,
                    "company_name": result.get("nom_complet", ""),
                    "address": result.get("siege", {}).get("adresse", "") 
                               if "siege" in result else ""
                }
    except requests.exceptions.RequestException as e:
        logger.warning(f"Impossible de joindre l'API SIRENE: {e}")
        
    return {"is_valid": False, "company_name": None, "address": None}
