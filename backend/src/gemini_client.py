"""
Gemini Client for RAG Answer Generation
"""
import google.generativeai as genai
import logging
import time

logger = logging.getLogger(__name__)

class GeminiRAGClient:
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def generate_answer(self, question, context_chunks, system_prompt):
        """
        Generate answer using Gemini with retrieved context
        """
        try:
            # Prepare context
            # context_chunks is a list of dicts now
            context_texts = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk in context_chunks]
            context_text = "\n\n---\n\n".join(context_texts)
            
            # Construct prompt
            full_prompt = system_prompt.format(
                context=context_text,
                question=question
            )
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract sources
            sources = []
            for i, chunk in enumerate(context_chunks):
                if isinstance(chunk, dict):
                    text = chunk["text"]
                    similarity = chunk.get("similarity", 0.0)
                    metadata = chunk.get("metadata", {})
                    source_name = metadata.get("source", "N/A")
                else:
                    text = chunk
                    similarity = 0.0
                    source_name = "N/A"
                    
                sources.append({
                    "source_number": i + 1,
                    "section": f"Source: {source_name}",
                    "page": "N/A", 
                    "similarity": similarity, 
                    "text_preview": text[:200] + "..."
                })

            return {
                "success": True,
                "answer": response.text,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
