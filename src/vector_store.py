"""
Vector store module - manages ChromaDB for semantic search
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages vector database operations using ChromaDB
    """
    
    def __init__(self, persist_directory: str = "./data/vectordb"):
        """
        Initialize ChromaDB client
        Args:
            persist_directory: Directory to persist vector database
        """
        self.persist_directory = persist_directory
        
        # Create directory if doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
    def create_collection(self, collection_name: str, reset: bool = False) -> chromadb.Collection:
        """
        Create or get a collection
        Args:
            collection_name: Name for the collection
            reset: If True, delete existing collection first
        Returns:
            ChromaDB collection object
        """
        if reset:
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except:
                pass
                
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"Collection '{collection_name}' ready")
        return collection
        
    def add_documents(
        self, 
        collection: chromadb.Collection,
        chunks: List[Dict]
    ) -> int:
        """
        Add document chunks to collection
        Args:
            collection: ChromaDB collection
            chunks: List of chunk dicts with 'text', 'embedding', 'chunk_id', metadata
        Returns:
            Number of chunks added
        """
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            if chunk.get('embedding') is None:
                continue
                
            ids.append(chunk['chunk_id'])
            embeddings.append(chunk['embedding'])
            documents.append(chunk['text'])
            
            # Prepare metadata (ChromaDB requires dict of str/int/float)
            metadata = {
                'token_count': chunk.get('token_count', 0),
                'chunk_index': chunk.get('chunk_index', 0),
                'section_title': chunk.get('section_title', ''),
                'source_file': chunk.get('source_file', ''),
                'page_number': chunk.get('page_number', 0)
            }
            metadatas.append(metadata)
        
        # Add to collection in batches (ChromaDB has limits)
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            
            collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            
        logger.info(f"Added {len(ids)} chunks to collection")
        return len(ids)
        
    def search(
        self,
        collection: chromadb.Collection,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar chunks
        Args:
            collection: ChromaDB collection
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        Returns:
            List of matching chunks with similarity scores
        """
        # Perform similarity search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata  # Optional filtering
        )
        
        # Format results
        formatted_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                result = {
                    'chunk_id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': results['metadatas'][0][i]
                }
                formatted_results.append(result)
        
        logger.info(f"Found {len(formatted_results)} relevant chunks")
        return formatted_results
        
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection
        Args:
            collection_name: Name of collection to delete
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
            
    def list_collections(self) -> List[str]:
        """
        List all collections
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [c.name for c in collections]
        
    def get_collection_stats(self, collection: chromadb.Collection) -> Dict:
        """
        Get statistics about a collection
        Args:
            collection: ChromaDB collection
        Returns:
            Dict with count and other stats
        """
        count = collection.count()
        
        return {
            'name': collection.name,
            'count': count,
            'metadata': collection.metadata
        }
