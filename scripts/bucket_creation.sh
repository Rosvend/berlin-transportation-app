import os
import yaml
from minio import Minio
from minio.error import S3Error

def main():
    """
    Connects to MinIO and creates the required bucket if it doesn't exist.
    """
    with open("/opt/airflow/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    bucket_name = config["storage"]["local"]["bucket"]
    
    # These env vars are available inside the airflow containers from docker-compose
    minio_endpoint = "minio:9000"
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")

    if not all([minio_access_key, minio_secret_key]):
        print("❌ Error: MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set in your .env file.")
        return

    print(f"Attempting to connect to MinIO at {minio_endpoint}...")
    
    try:
        client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
        
        found = client.bucket_exists(bucket_name)
        if not found:
            client.make_bucket(bucket_name)
            print(f"✅ Bucket '{bucket_name}' created successfully.")
        else:
            print(f"⚠️  Bucket '{bucket_name}' already exists.")
            
    except S3Error as exc:
        print(f"❌ Error connecting to MinIO or creating bucket: {exc}")
    except Exception as exc:
        print(f"❌ An unexpected error occurred: {exc}")

if __name__ == "__main__":
    main()