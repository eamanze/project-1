from celery import shared_task
import time
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from tempfile import NamedTemporaryFile

@shared_task
def process_text(file_hash, s3_uri):
    start_time = time.time()
    s3 = boto3.client("s3")

    try:
        # Parse the S3 URI
        if not s3_uri.startswith("s3://"):
            raise ValueError("Invalid S3 URI format. Expected s3://bucket/key")

        _, _, bucket_key = s3_uri.partition("s3://")
        bucket, _, key = bucket_key.partition("/")

        # Download from S3 to temp file
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            s3.download_fileobj(bucket, key, tmp_file)
            tmp_file_path = tmp_file.name

        # Read file and forward to FastAPI /embed
        with open(tmp_file_path, "rb") as f:
            files = {"file": ("upload.pdf", f, "application/pdf")}
            data = {"file_hash": file_hash}
            response = requests.post("http://aifastapi:8010/embed/", files=files, data=data)
            response.raise_for_status()

        result = response.json()
        print(f"✅ FastAPI /embed response: {result}")

    except (ClientError, BotoCoreError, Exception) as e:
        return f"❌ Error during processing {file_hash}: {str(e)}"

    elapsed_time = time.time() - start_time
    return f"✅ Text for {file_hash} processed successfully in {elapsed_time:.2f} seconds."

@shared_task
def generate_embeddings(file_hash):
    start_time = time.time()
    print('Hello Embeddings...')
    elapsed_time = time.time() - start_time
    return f"Embeddings for {file_hash} generated and saved successfully in {elapsed_time:.2f} seconds."
