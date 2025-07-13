import environ
import os
import vertexai

env = environ.Env(
    GCP_PROJECT=(str, "your-project-id"),
    GCP_LOCATION=(str, "us-central1"),
    GOOGLE_APPLICATION_CREDENTIALS=(str, None),  # Add this
)

environ.Env.read_env()

GCP_PROJECT = env("GCP_PROJECT")
GCP_LOCATION = env("GCP_LOCATION")

# Set GCP credentials from environment
google_creds = env("GOOGLE_APPLICATION_CREDENTIALS")
if google_creds:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds

# Initialize Vertex AI
vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

# Pinecone
PINECONE_API_KEY = env("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = env("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = env("PINECONE_INDEX_NAME")

