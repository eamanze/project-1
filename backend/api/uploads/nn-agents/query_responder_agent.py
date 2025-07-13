
import pinecone
from config import *
from vertexai.preview.language_models import ChatModel, TextEmbeddingModel

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pinecone.Index(PINECONE_INDEX_NAME)

class QueryResponderAgent:
    def __init__(self):
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
        self.chat_model = ChatModel.from_pretrained("chat-bison@latest")

    def embed_query(self, query):
        embeddings = self.embedding_model.get_embeddings([query])
        return embeddings[0].values

    def retrieve_context(self, query, top_k=3):
        query_embedding = self.embed_query(query)
        response = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
        matches = response.get('matches', [])
        return "\n\n".join([match['metadata']['text'] for match in matches]) if matches else ""

    def generate_answer(self, context, query):
        prompt = f"""You are an assistant. Use the following context to answer the question accurately.

Context:
{context}

Question:
{query}

Answer:"""

        chat = self.chat_model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    