from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from embedding_agent import EmbeddingService
from generative_ai_agent import ResponseService
from text_processor import TextProcessor
from pinecone_manager import PineconeManager
import hashlib
import fitz
import tempfile
import os
import uvicorn
import httpx
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
pinecone_mgr = PineconeManager()
embed_service = EmbeddingService()
response_service = ResponseService()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def compute_bytes_hash(data: bytes) -> str:
    """Generate SHA256 hash of file bytes."""
    return hashlib.sha256(data).hexdigest()

@app.post("/embed")
async def embed_pdf(
    file: UploadFile = File(...),
    file_hash: str = Form(...)
):
    try:
        print(f"📥 Received embed: file={file.filename}, file_hash={file_hash}")

        # ✅ Read PDF into memory
        raw_data = await file.read()

        # ✅ Use provided file_hash (fallback to content hash if needed)
        file_id = file_hash or compute_bytes_hash(raw_data)

        # ✅ Extract text from in-memory PDF
        with fitz.open(stream=raw_data, filetype="pdf") as doc:
            text = " ".join(page.get_text() for page in doc)

        # ✅ Chunk text using tokenizer
        text_processor = TextProcessor(embed_service.embedder.tokenizer)
        chunks = text_processor.chunk_text(text)

        # ✅ Save temp file for embedding
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(raw_data)
            tmp_path = tmp.name

        file_id_result = embed_service.process_document(tmp_path, pinecone_mgr, file_id=file_id)
        os.unlink(tmp_path)

        # ✅ Forward chunks to Django backend
        model_used = os.getenv("EMBEDDING_MODEL", "intfloat/e5-base-v2")
        async with httpx.AsyncClient() as client:
            for i, chunk in enumerate(chunks):
                payload = {
                    "file_hash": file_id,
                    "chunk_text": chunk,
                    "chunk_number": i,
                    "vector_id": None,
                    "model_used": model_used,
                }

                try:
                    response = await client.post(
                        f"{os.getenv('DJANGO_API_BASE_URL', 'http://backend:8000')}/api/data/chunks/",
                        json=payload,
                        timeout=10.0,
                    )
                except httpx.HTTPError as e:
                    print(f"🔥 HTTPX ERROR on chunk {i}: {str(e)}")
                    raise HTTPException(status_code=502, detail=f"Failed to send chunk {i} to Django")

                if response.status_code != 201:
                    print(f"❌ Failed to save chunk {i}: {response.text}")
                    raise HTTPException(status_code=500, detail=f"Chunk {i} rejected by Django")

        return JSONResponse(
            status_code=200,
            content={
                "file_id": file_id_result,
                "num_chunks": len(chunks),
                "status": "embedded"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate")
async def generate_response(file_id: str, text: str):
    try:
        response = response_service.generate_answer(file_id, text)
        return {
            "file_id": file_id,
            "response": response,
            "status": "generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SearchRequest(BaseModel):
    query: str
    top_k: int
    threshold: float = 0.75 

@app.post("/search")
async def generate_response(request: SearchRequest):
    query = request.query
    top_k = request.top_k
    threshold = request.threshold
    print(f"🔎 Using threshold: {threshold}")

    try:
        # Step 1: Vectorize query
        query_vector = embed_service.vectorize_query(query)

        # Step 2: Query Pinecone
        search_result = pinecone_mgr.query_top_k(query_vector, top_k=top_k)
        
        # Step 3: Collect top 3 matches above threshold
        matches = []
        context_chunks = []

        for match in search_result.matches:
            if match.score < threshold:
                continue
            if len(matches) >= 3:
                break
            matches.append(match)
            context_chunks.append(match.metadata.get("text", ""))

        if not matches:
            return JSONResponse(status_code=404, content={"error": "No match found."})

        # Step 4: Prepare context window
        context_window = "\n\n".join(context_chunks)

        # Step 5: Generate response from GenAI
        response_text = response_service.generate_answer_from_context(
            query=query,
            context=context_window,
            file_id="search"
        )

        # Step 6: Return file_id and answer
        file_id = matches[0].metadata.get("file_id")

        return JSONResponse(
            status_code=200,
            content={
                "query": query,
                "file_id": file_id,
                "response": response_text,
                "context_chunks": context_chunks,
                "status": "response_generated"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
