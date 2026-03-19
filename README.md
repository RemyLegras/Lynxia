# Lynxia

Plateforme d'automatisation de document, gestion de documents et interface comptable.

## Description

Lynxia est une solution complète pour :
- **Traitement des documents** de documents (factures, devis, attestations, bilans)
- **API REST** pour l'intégration des documents
- **Interfaces utilisateur** pour consultation et gestion 

### Les services utiliser

| Service | Port | Description |
|---------|------|-------------|
| API (FastAPI) | 8000 | Backend API |
| Frontend | 5173 | Interface principale |
| Frontend Compta | 5174 | Interface comptable |
| MySQL | 3306 | Base de données |
| Airflow Web | 8080 | Orchestration des workflows |
| MinIO | 9000 | Stockage d'objets |

### Airflow (`/Airflow`)

Orchestration des pipelines :

#### DAGs disponibles

| DAG | Description |
|-----|-------------|
| `ocr_pipeline_dag` | Pipeline complet d'OCR et d'extraction d'informations |
| `generate_bilan_dag` | Génération automatique de bilans |
| `generate_devis` | Génération de devis |
| `api_justificatifs_dag` | Récupération et traitement via API |

#### Modules OCR

- **analyzer.py** : Analyse de documents
- **classifier.py** : Classification des types de documents
- **llm_extractor.py** : Extraction d'informations avec LLM
- **main.py** : Orchestration du pipeline
- **processors/** : Processeurs spécialisés (facture, devis, attestation, bilan)
- **utils/** : Utilitaires (nettoyage, détection)

### Scripts (`/scripts`)

Scripts autonomes pour génération et traitement :
- `generate_random_bilan_v2.py` : Génération de données (bilans)
- `generate_random_devis_v1.py` : Génération de données (devis)
- `data_augmentation.py` : simulation de donnée mal scannée ETC
- `api_justificatifs.py` : Gestion API justificatifs

## Dépendances principales

### Backend
- **FastAPI** - Framework 
- **PyMySQL** - Client MySQL
- **Minio** - Stockage distribué
- **Pydantic** - Validation des données

### Frontend
- **React 19** - Framework UI
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Material-UI** - Composants
- **Axios** - Client HTTP

### Airflow
- **Apache Airflow** - Orchestration
- **OpenAI** - Extraction LLM
- **Tesseract** - OCR

### Pipeline OCR complet
```
Upload → OCR → extraction → validation → exploitation
```

## API principaux

```
GET    /api/documents          - Lister les documents
POST   /api/documents          - Créer un document
GET    /api/documents/{id}     - Détails d'un document
DELETE /api/documents/{id}     - Supprimer un document
POST   /api/auth/login         - Connexion
POST   /api/auth/register      - Inscription
GET    /api/users/profile      - Profil utilisateur
```

## 👤 Auteur

 Rémy LEGRAS 

 Cloé PETETIN 

 Antoine BLAIN 

 Adrien FOUQUET 

 Clément BASTIEN 

 Yanis HELALI 

 Fatma BOUZID 