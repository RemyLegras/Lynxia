import os
from minio import Minio

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "lynxia-docs")
BUCKETS = ["raw", "clean", "curated", MINIO_BUCKET_NAME]

try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False  
    )

    # Création automatique des buckets (Zones Data Lake)
    for bucket in BUCKETS:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"Bucket '{bucket}' créé avec succès dans MinIO.")
        else:
            print(f"Bucket '{bucket}' existe déjà dans MinIO.")
except Exception as e:
    print(f"Erreur de connexion à MinIO: {e}")
    minio_client = None

def upload_file_to_minio(object_name: str, file_path: str, bucket_name: str = "raw") -> bool:
    if minio_client is None:
        return False
    try:
        minio_client.fput_object(bucket_name, object_name, file_path)
        return True
    except Exception as e:
        print(f"Erreur d'upload vers MinIO: {e}")
        return False

def download_file_from_minio(object_name: str, dest_path: str, bucket_name: str = "raw") -> bool:
    if minio_client is None:
        return False
    try:
        minio_client.fget_object(bucket_name, object_name, dest_path)
        return True
    except Exception as e:
        print(f"Erreur de téléchargement depuis MinIO: {e}")
        return False
