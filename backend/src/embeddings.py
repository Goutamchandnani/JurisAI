"""
Embeddings Module using Gemini
"""
import google.generativeai as genai
import logging
import time

logger = logging.getLogger(__name__)

class GeminiEmbedder:
    def __init__(self, api_key, model_name="models/text-embedding-004"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        # Check if the requested model is in the list of available models, or use a fallback.
        # However, list_models can be slow, so we'll just try and catch.

        
    def embed_chunks(self, chunks, batch_size=10):
        """
        Embed a list of text chunks with batching and rate limiting
        """
        embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            try:
                # Attempt to use the configured model
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
                logger.warning(f"Error embedding batch {i} with {self.model_name}: {str(e)}. Attempting fallback...")
                
                # Logic to determine which model to try for fallback
                fallback_models = ["models/gemini-embedding-001", "models/embedding-001"]
                
                success = False
                for fallback_model in fallback_models:
                    try:
                        res = genai.embed_content(
                            model=fallback_model,
                            content=batch,
                            task_type="retrieval_document"
                        )
                        embeddings.extend(res['embedding'])
                        success = True
                        logger.info(f"Successfully used fallback model: {fallback_model}")
                        break
                    except Exception as fallback_e:
                        logger.warning(f"Fallback to {fallback_model} failed: {str(fallback_e)}")
                        continue
                
                if not success:
                    logger.error(f"All batch embedding attempts failed for batch {i}. Trying individual chunks...")
                    # Fallback of fallbacks: try one by one if batch fails completely
                    for text in batch:
                        try:
                            res = genai.embed_content(
                                model="models/gemini-embedding-001",
                                content=text,
                                task_type="retrieval_document"
                            )
                            embeddings.append(res['embedding'])
                            time.sleep(0.2)
                        except Exception as inner_e:
                            logger.error(f"Failed to embed individual chunk: {inner_e}")
                            embeddings.append(None) # Keep index alignment

                        
        return embeddings

    def embed_query(self, query):
        """
        Embed a single query string with a fallback to a stable model
        """
        models_to_try = [self.model_name, "models/gemini-embedding-001", "models/embedding-001"]
        
        last_error = None
        for model in models_to_try:
            try:
                logger.info(f"Attempting query embedding with model: {model}")
                result = genai.embed_content(
                    model=model,
                    content=query,
                    task_type="retrieval_query"
                )
                return result['embedding']
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to embed query with {model}: {str(e)}")
                continue
        
        logger.error(f"All embedding attempts failed. Last error: {str(last_error)}")
        return None

