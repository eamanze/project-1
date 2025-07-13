from ai_agents import EmbeddingGenerator
from text_processor import TextProcessor
from concurrent.futures import ThreadPoolExecutor
import os
import uuid
import time

class EmbeddingService:
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.embedder._load_model()

    def process_batch(self, chunks, file_id, pinecone_mgr, embedder):
        """Generate embeddings for a batch and upload them"""
        embeddings = embedder.generate_embeddings(chunks, file_id)
        vectors = [{
            "id": f"{file_id}-{str(uuid.uuid4())}",
            "values": emb,
            "metadata": {"text": chunk, "file_id": file_id}
        } for chunk, emb in zip(chunks, embeddings)]

        upload_time = pinecone_mgr.upload_vectors(vectors)
        print(f"↗️ Uploaded {len(vectors)} vectors in {upload_time:.2f}s")

    def process_document(self, pdf_path, pinecone_mgr, file_id=None):
        file_id = file_id or os.path.splitext(os.path.basename(pdf_path))[0]
        # ✅ Check once before starting
        if pinecone_mgr.check_existing_embeddings(file_id):
            print(f"⚠️ Embeddings already exist for {file_id}. Skipping entire process.")
            return file_id

        text_processor = TextProcessor(self.embedder.tokenizer)

        # Extract and chunk text
        text_start = time.time()
        text = text_processor.extract_text(pdf_path)
        chunks = text_processor.chunk_text(text)
        text_time = time.time() - text_start

        # Batch embedding and upload
        embed_start = time.time()
        with ThreadPoolExecutor() as executor:
            futures = []
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                futures.append(executor.submit(
                    self.process_batch,
                    batch_chunks,
                    file_id,
                    pinecone_mgr,
                    self.embedder
                ))

            # Collect batch results
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Batch failed: {e}")
                    return file_id  # Exit early without writing marker

        embed_time = time.time() - embed_start
        print(f"\n⏱️ Embedding processing for {file_id}:")
        print(f"- Text processing: {text_time:.2f}s")
        print(f"- Batch processing: {embed_time:.2f}s")

        # ✅ Upload marker after successful batches
        marker_time = pinecone_mgr.upload_marker(file_id)
        print(f"✅ Marker uploaded for {file_id} in {marker_time:.2f}s")

        return file_id
    
    def vectorize_query(self, query: str) -> list[float]:
        """
        Generate a single embedding vector for the input query.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty.")
        
        return self.embedder.generate_embeddings([query], "query")[0]  # returns a list of floats

