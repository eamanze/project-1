from celery import shared_task
import time

@shared_task
def process_text(file_hash, s3_uri):
    time.sleep(5)  # simulate delay
    return f"Text for {file_hash} processed successfully!"

@shared_task
def generate_embeddings(file_hash):
    time.sleep(5)  # simulate delay
    return f"Embeddings for {file_hash} generated successfully!"

