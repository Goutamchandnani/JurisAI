import os
import shutil
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our RAG components
from src.pdf_processor import extract_text_from_pdf
from src.chunking import DocumentChunker
from src.embeddings import GeminiEmbedder
from src.vector_store import VectorStore
from src.gemini_client import GeminiRAGClient
from config import LEGAL_SYSTEM_PROMPT

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="JurisAI Backend API")

# Configure CORS for Vercel and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = "./uploads"
VECTORDB_DIR = "./data/vectordb"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTORDB_DIR, exist_ok=True)

# Initialize global components
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment")

embedder = GeminiEmbedder(api_key)
vector_store = VectorStore(VECTORDB_DIR)
rag_client = GeminiRAGClient(api_key)
chunker = DocumentChunker(
    chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200))
)

class QueryRequest(BaseModel):
    collection_name: str
    query: str
    top_k: int = 5

@app.get("/")
async def health_check():
    return {"status": "online", "message": "JurisAI Backend is running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Handle PDF upload, chunking, and embedding
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        extraction = extract_text_from_pdf(file_path)
        if not extraction['success']:
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {extraction.get('error')}")
        
        # Chunk text
        chunks = chunker.smart_chunk(extraction['text'], metadata={'source': file.filename})
        
        # Embed chunks
        embedded_chunks = embedder.embed_chunks(chunks)
        
        # Store in Vector DB
        collection_name = f"doc_{file.filename.replace('.pdf', '').replace(' ', '_')}"
        collection = vector_store.create_collection(collection_name, reset=True)
        
        vector_store.add_documents(
            collection=collection,
            embeddings=embedded_chunks,
            documents=chunks,
            metadatas=[{'source': file.filename}] * len(chunks)
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "collection_name": collection_name,
            "chunk_count": len(chunks)
        }
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_document(request: QueryRequest):
    """
    Handle RAG query
    """
    try:
        # 1. Get embedding for query
        query_embedding = embedder.embed_query(request.query)
        if query_embedding is None:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # 2. Search Vector DB
        collection = vector_store.client.get_collection(name=request.collection_name)
        relevant_chunks = vector_store.search(collection, query_embedding, top_k=request.top_k)
        
        if not relevant_chunks:
            return {"answer": "No relevant information found in the document.", "sources": []}
        
        # 3. Generate Answer
        result = rag_client.generate_answer(
            question=request.query,
            context_chunks=relevant_chunks,
            system_prompt=LEGAL_SYSTEM_PROMPT
        )
        
        return result
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
