# agents/db_utils.py
from users.models import TextChunk

def save_chunk_to_db(file_hash: str, chunk_text: str, chunk_number: int, vector_id: str, model_used: str = "titan-embed-text-v1"):
    """Save a text chunk and its vector_id into PostgreSQL."""
    chunk = TextChunk.objects.create(
        file_hash=file_hash,
        chunk_text=chunk_text,
        chunk_number=chunk_number,
        vector_id=vector_id,
        model_used=model_used
    )
    return chunk
