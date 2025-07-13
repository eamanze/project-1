import pinecone
from config import *
from agents.db_utils import get_chunks_by_file_hash
from vertexai.preview.language_models import TextEmbeddingModel
from agents.base_agent import BaseAgent  # <-- Import BaseAgent

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pinecone.Index(PINECONE_INDEX_NAME)

class EmbedderAgent(BaseAgent):   
    def __init__(self):
        super().__init__(name="EmbedderAgent")  
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")

    def run(self, file_hash):
        """Run method from BaseAgent: Embed and upload vectors."""
        self.embed_and_save_chunks(file_hash)

    def embed_and_save_chunks(self, file_hash):
        """Embed existing chunks, upload to Pinecone, and update vector_ids in PostgreSQL."""
        chunks = get_chunks_by_file_hash(file_hash)
        if not chunks:
            print(f"[{self.name}] No chunks found for {file_hash}.")
            return

        vectors = []
        for chunk in chunks:
            embedding = self.embedding_model.get_embeddings([chunk.chunk_text])[0].values
            vector_id = f"{file_hash}_{chunk.chunk_number}"

            # Save the vector ID back into the DB
            chunk.vector_id = vector_id
            chunk.save(update_fields=["vector_id"])

            vectors.append((vector_id, embedding, {"text": chunk.chunk_text}))
            
        for i in range(0, len(vectors), 100):
            batch = vectors[i:i+100]
            index.upsert(vectors=batch)

        print(f"[{self.name}] Uploaded {len(vectors)} vectors to Pinecone and updated PostgreSQL for file {file_hash}.")
