"""
Embeddings module - generates vector embeddings using Gemini
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)


class GeminiEmbedder:
    """
    Handles embedding generation using Gemini text-embedding-004
    """
    
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        """
        Initialize embedder
        Args:
            api_key: Google Gemini API key
            model_name: Embedding model to use
        """
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.embedding_dimension = 768  # Gemini embedding size
        
    def embed_text(self, text: str, task_type: str = "retrieval_document") -> Optional[List[float]]:
        """
        Generate embedding for single text
        Args:
            text: Text to embed
            task_type: Type of embedding task
                - "retrieval_document" for document chunks
                - "retrieval_query" for search queries
        Returns:
            Embedding vector (768 dimensions) or None if failed
        """
        try:
            # Call Gemini embedding API
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type
            )
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
            
    def embed_batch(
        self, 
        texts: List[str], 
        task_type: str = "retrieval_document",
        batch_size: int = 10
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts with batching
        Args:
            texts: List of texts to embed
            task_type: Embedding task type
            batch_size: Process in batches to avoid rate limits
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Generate embeddings for batch
            for text in batch:
                embedding = self.embed_text(text, task_type)
                embeddings.append(embedding)
                
                # Rate limiting - small delay between requests
                time.sleep(0.1)
                
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
        return embeddings
        
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunk dictionaries
        Args:
            chunks: List of chunk dicts (from chunking.py)
        Returns:
            Chunks with 'embedding' field added
        """
        # Extract text from each chunk
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embed_batch(texts, task_type="retrieval_document")
        
        # Add embeddings to chunk dicts
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
            
        # Filter out failed embeddings
        successful_chunks = [c for c in chunks if c['embedding'] is not None]
        
        logger.info(f"Successfully embedded {len(successful_chunks)}/{len(chunks)} chunks")
        
        return successful_chunks
        
    def embed_query(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for search query
        Args:
            query: User's question
        Returns:
            Query embedding vector
        """
        return self.embed_text(query, task_type="retrieval_query")
        
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        magnitude1 = np.linalg.norm(vec1)
        magnitude2 = np.linalg.norm(vec2)
        
        similarity = dot_product / (magnitude1 * magnitude2)
        
        return float(similarity)
