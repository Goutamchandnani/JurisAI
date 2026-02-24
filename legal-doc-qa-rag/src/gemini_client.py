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
            # context_chunks is a list of strings
            context_text = "\n\n---\n\n".join(context_chunks)
            
            # Construct prompt
            full_prompt = system_prompt.format(
                context=context_text,
                question=question
            )
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract sources (Mock logic for now as we don't have metadata tracking in the simplistic vector store search return yet)
            # In a real system, we'd look at match metadata. 
            # Check source format from vector store search.
            
            # For now, sources are just the chunks themselves
            sources = []
            for i, chunk in enumerate(context_chunks):
                sources.append({
                    "source_number": i + 1,
                    "section": "Retrieved Section",
                    "page": "N/A", # Metadata lost in current pipeline
                    "similarity": 0.0, # Similarity score lost in current pipeline
                    "text_preview": chunk[:200] + "..."
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
