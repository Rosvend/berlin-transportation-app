#!/usr/bin/env python3
"""
MinIO bucket setup script for Berlin Transport Data Pipeline
Creates the required bucket and initial folder structure if they don't exist.
"""

import os
import sys
import time
import yaml
from minio import Minio
from minio.error import S3Error
from io import BytesIO


def wait_for_minio(client, max_retries=30, delay=2):
    """Wait for MinIO to be ready with exponential backoff."""
    for attempt in range(max_retries):
        try:
            # Try to list buckets to test connectivity
            list(client.list_buckets())
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for MinIO... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay = min(delay * 1.2, 10)  # Exponential backoff, max 10s
            else:
                print(f"❌ Failed to connect to MinIO after {max_retries} attempts: {e}")
                return False
    return False


def create_folder_structure(client, bucket_name, paths):
    """Create folder structure in MinIO bucket."""
    for path_name, path_value in paths.items():
        try:
            # Create a placeholder object to represent the folder
            placeholder_path = f"{path_value}/.keep"
            
            # Convert empty string to bytes and create a BytesIO object
            data = BytesIO(b"")
            
            client.put_object(
                bucket_name, 
                placeholder_path, 
                data=data, 
                length=0
            )
            print(f"✅ Created folder: {path_value}/")
        except S3Error as e:
            print(f"⚠️  Could not create folder {path_value}/: {e}")
        except Exception as e:
            print(f"⚠️  Could not create folder {path_value}/: {e}")


def main():
    """
    Connects to MinIO and creates the required bucket and folder structure.
    """
    try:
        # Load configuration
        config_path = "/opt/airflow/config/config.yaml"
        if not os.path.exists(config_path):
            print(f"❌ Configuration file not found: {config_path}")
            sys.exit(1)
            
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        bucket_name = config["storage"]["local"]["bucket"]
        folder_paths = config["storage"]["local"]["paths"]
        
        # Get credentials from environment
        minio_endpoint = "minio:9000"
        minio_access_key = os.getenv("MINIO_ACCESS_KEY")
        minio_secret_key = os.getenv("MINIO_SECRET_KEY")

        if not all([minio_access_key, minio_secret_key]):
            print("❌ Error: MINIO_ACCESS_KEY and MINIO_SECRET_KEY must be set")
            sys.exit(1)

        print(f"🔗 Connecting to MinIO at {minio_endpoint}...")
        
        client = Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
        
        # Wait for MinIO to be ready
        if not wait_for_minio(client):
            sys.exit(1)
            
        # Check and create bucket
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"⚠️  Bucket '{bucket_name}' already exists")
            
        # Create folder structure
        print("📁 Setting up folder structure...")
        create_folder_structure(client, bucket_name, folder_paths)
        
        print("✅ MinIO setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()