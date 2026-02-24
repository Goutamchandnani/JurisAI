"""
Embeddings Module using Gemini
"""
import google.generativeai as genai
import logging
import time

logger = logging.getLogger(__name__)

class GeminiEmbedder:
    def __init__(self, api_key, model_name="models/gemini-embedding-001"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        
    def embed_chunks(self, chunks, batch_size=10):
        """
        Embed a list of text chunks with batching and rate limiting
        """
        embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            try:
                # Gemini embedding API
                result = genai.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type="retrieval_document"
                )
                
                # Check format of result (can vary by version)
                if 'embedding' in result:
                    embeddings.extend(result['embedding'])
                else:
                    # Handle batch list output
                    for entry in result['embedding']: 
                         embeddings.append(entry)
                         
                # Rate limit safety
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error embedding batch {i}: {str(e)}")
                # If batch fails, try individual? For now, raise or skip
                # Simple fallback: try one by one if batch fails
                for text in batch:
                    try:
                        res = genai.embed_content(
                            model=self.model_name,
                            content=text,
                            task_type="retrieval_document"
                        )
                        embeddings.append(res['embedding'])
                        time.sleep(0.2)
                    except Exception as inner_e:
                        logger.error(f"Failed to embed chunk: {inner_e}")
                        embeddings.append(None) # Keep index alignment
                        
        return embeddings

    def embed_query(self, query):
        """
        Embed a single query string
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            return None
