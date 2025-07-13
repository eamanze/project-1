import os
import time
from pinecone import Pinecone

class PineconeManager:
    def __init__(self):
        self._init_pinecone()

    def _init_pinecone(self):
        api_key = os.getenv("PINECONE_API_KEY")
        print("Pinecone Manager: API Key = ", api_key)
        if not api_key:
            raise ValueError("PINECONE_API_KEY is missing. Please set it in your environment or .env file.")
        self.index = Pinecone(api_key=api_key).Index(os.getenv("PINECONE_INDEX", "e5-768d-index"))

    def check_existing_embeddings(self, file_id: str) -> bool:
        try:
            start = time.time()
            fetch_result = self.index.fetch(ids=[f"marker-{file_id}"])
            exists = len(fetch_result.vectors) > 0
            print(f"🔍 Marker check [{file_id}]: {exists} (Checked in {time.time()-start:.2f}s)")
            return exists
        except Exception as e:
            print(f"⚠️ Pinecone fetch error: {e}")
            return False

    def upload_vectors(self, vectors: list) -> float:
        start = time.time()
        self.index.upsert(vectors=vectors)
        return time.time() - start

    def upload_marker(self, file_id: str) -> float:
        start = time.time()
        # ✅ Use small non-zero values
        marker_vector = {
            "id": f"marker-{file_id}",
            "values": [1e-8] * 768,
            "metadata": {"file_id": file_id, "marker": True}
        }
        self.index.upsert(vectors=[marker_vector])
        return time.time() - start
    
    def query_top_k(self, vector: list[float], top_k: int = 5, namespace: str = ""):
        """
        Query Pinecone for the top_k most similar vectors.
        """
        try:
            start = time.time()
            result = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace or None
            )
            print(f"🔍 Pinecone query took {time.time() - start:.2f}s")
            return result
        except Exception as e:
            print(f"❌ Pinecone query error: {e}")
            raise


