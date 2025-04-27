from minio import Minio
from minio.error import S3Error
import os
import time

# Initialize MinIO client
minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False,
)

# Bucket Name
BUCKET_NAME = "profile-pictures"

# Ensure bucket exists with retries
def ensure_bucket_exists():
    retries = 5
    for i in range(retries):
        try:
            found = minio_client.bucket_exists(BUCKET_NAME)
            if not found:
                minio_client.make_bucket(BUCKET_NAME)
                print(f"Bucket '{BUCKET_NAME}' created.")
            else:
                print(f"Bucket '{BUCKET_NAME}' already exists.")
            break
        except Exception as e:
            print(f"Attempt {i+1}/{retries} failed: {e}")
            time.sleep(3)
    else:
        print(f"Failed to connect to MinIO after {retries} retries")
        raise Exception("MinIO connection failed")

# Call it during service import
ensure_bucket_exists()

def upload_profile_picture(file_data, filename: str) -> str:
    """Uploads file to Minio and returns the public URL."""
    try:
        # Seek to end to get file size
        file_data.seek(0, 2)
        file_size = file_data.tell()
        file_data.seek(0)  # Reset to beginning for upload

        minio_client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=filename,
            data=file_data,
            length=file_size,
            content_type="image/jpeg",  # or "image/png" depending on file
        )

        # Build the URL manually
        file_url = f"http://localhost:9000/{BUCKET_NAME}/{filename}"
        return file_url

    except S3Error as e:
        print("Error uploading to Minio:", e)
        raise e
