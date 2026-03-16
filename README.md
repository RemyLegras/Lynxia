# Lynxia API

API de gestion de documents avec authentification.

## Stack technique

- **FastAPI** : Framework web Python
- **MySQL** : Base de données (CREATE IF NOT EXISTS)
- **Pydantic** : Validation des données
- **Docker** : Conteneurisation

## Fonctionnalités

- Authentification par token
- Gestion des documents
- API RESTful
- CORS configuré

## Démarrage rapide

### Local
```bash
# Installation dépendances
pip install -r requirements.txt

# Démarrage API
uvicorn app.main:app --reload
```

### Docker
```bash
docker-compose up -d --build
```

## Endpoints

- `POST /api/auth/register` : Inscription
- `POST /api/auth/login` : Connexion
- `GET /api/auth/me` : Profil utilisateur
- `GET /api/documents` : Liste des documents
- `POST /api/documents` : Créer un document

## Configuration

Variables d'environnement :
- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

## Architecture

```
app/
├── api/
│   ├── routes/
│   │   ├── auth/
│   │   └── documents.py
│   └── router.py
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   └── document_service.py
├── schemas/
│   └── document.py
├── utils.py
├── auth_utils.py
├── database.py
└── main.py
```

## Auteur

Remy Legras
