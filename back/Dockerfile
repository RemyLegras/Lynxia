FROM python:3.11-slim
WORKDIR /app
# Copier les dépendances
COPY requirements.txt .
# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt
# Copier le code de l'application
COPY . app/
# Créer les dossiers nécessaires
RUN mkdir -p uploads/raw data
# Exposer le port
EXPOSE 8000
# Commande pour lancer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
