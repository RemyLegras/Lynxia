import os
from minio import Minio
from loguru import logger

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "lynxia-docs")
BUCKETS = ["raw", "clean", "curated"]

_client = None

def get_minio_client():
    global _client
    if _client is not None:
        return _client
    
    try:
        _client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        # On essaie d'initialiser les buckets au premier accès
        for bucket in BUCKETS:
            if not _client.bucket_exists(bucket):
                _client.make_bucket(bucket)
                logger.info(f"Bucket '{bucket}' créé avec succès.")
        return _client
    except Exception as e:
        logger.error(f"Erreur de connexion à MinIO: {e}")
        _client = None
        return None

def upload_file_to_minio(object_name: str, file_path: str, bucket_name: str = "raw") -> bool:
    client = get_minio_client()
    if client is None:
        return False
    try:
        # Re-vérification du bucket par sécurité
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            
        client.fput_object(bucket_name, object_name, file_path)
        return True
    except Exception as e:
        logger.error(f"Erreur d'upload vers MinIO ({bucket_name}): {e}")
        return False

def download_file_from_minio(object_name: str, dest_path: str, bucket_name: str = "raw") -> bool:
    client = get_minio_client()
    if client is None:
        return False
    try:
        client.fget_object(bucket_name, object_name, dest_path)
        return True
    except Exception as e:
        logger.error(f"Erreur de téléchargement depuis MinIO ({bucket_name}): {e}")
        return False
