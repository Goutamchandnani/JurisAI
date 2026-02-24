"""
Vector Store Module using ChromaDB
"""
import chromadb
import logging
import os
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_dir="./data/vectordb"):
        # Ensure directory exists
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
            
        self.client = chromadb.PersistentClient(path=persist_dir)
        
    def create_collection(self, name, reset=False):
        """
        Get or create a collection
        """
        try:
            if reset:
                try:
                    self.client.delete_collection(name)
                except Exception:
                    pass # Collection didn't exist or couldn't be deleted
            
            # Create new
            return self.client.get_or_create_collection(name=name)
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise

    def add_documents(self, collection, embeddings, documents, metadatas=None):
        """
        Add documents to collection
        """
        if not embeddings:
            return 0
            
        count = len(embeddings)
        ids = [str(uuid.uuid4()) for _ in range(count)]
        
        # Ensure documents is a list matching embeddings length
        if len(documents) != count:
            logger.error(f"Mismatch: {len(documents)} docs vs {count} embeddings")
            raise ValueError("Documents and embeddings counts must match")

        # Filter out failed embeddings (None)
        valid_indices = [i for i, emb in enumerate(embeddings) if emb is not None]
        
        if len(valid_indices) < len(embeddings):
            logger.warning(f"Dropping {len(embeddings) - len(valid_indices)} chunks due to embedding errors")
            
        if not valid_indices:
            logger.error("No valid embeddings to add")
            return 0
            
        # Filter data based on valid indices
        embeddings = [embeddings[i] for i in valid_indices]
        ids = [ids[i] for i in valid_indices]
        documents = [documents[i] for i in valid_indices]
        metadatas = [metadatas[i] for i in valid_indices]
            
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            return len(valid_indices)
            
        except Exception as e:
             logger.error(f"Error adding documents: {str(e)}")
             raise

    def search(self, collection, query_embedding, top_k=5):
        """
        Search for relevant documents
        """
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            # results['documents'][0] is list of strings
            formatted_results = []
            if results['documents']:
                for doc in results['documents'][0]:
                    formatted_results.append(doc)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
