"""
Gemini API client for RAG-based Q&A
"""

import google.generativeai as genai
from typing import List, Dict, Optional, Generator
import logging
import time

logger = logging.getLogger(__name__)


class GeminiRAGClient:
    """
    Gemini client optimized for RAG pipeline
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client
        Args:
            api_key: Google Gemini API key
            model_name: Model to use for generation
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict],
        system_prompt: str,
        max_retries: int = 3,
        max_context_chars: int = 30000 
    ) -> Dict:
        """
        Generate answer using retrieved context
        Args:
            question: User's question
            context_chunks: Relevant chunks from vector search
            system_prompt: System instructions
            max_retries: Number of retry attempts
            max_context_chars: Approximate character limit for context
        Returns:
            Dict with 'answer', 'sources', 'success'
        """
        # Build context from retrieved chunks with limiting
        context = self._build_context(context_chunks, max_chars=max_context_chars)
        
        # Create the full prompt
        full_prompt = f"""{system_prompt}

CONTEXT FROM DOCUMENT:
{context}

QUESTION: {question}

Please answer based on the provided context. Include specific references to the source sections.
"""
        
        # Generate response with retries
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                
                return {
                    'answer': response.text,
                    'sources': self._extract_sources(context_chunks),
                    'success': True,
                    'chunks_used': len(context_chunks) # Note: this might be inaccurate if truncated inside _build_context, but acceptable for now
                }
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {
                        'answer': f"Error generating answer: {str(e)}",
                        'sources': [],
                        'success': False,
                        'error': str(e)
                    }
    
    def stream_answer(
        self,
        question: str,
        context_chunks: List[Dict],
        system_prompt: str,
        max_context_chars: int = 30000
    ) -> Generator[str, None, None]:
        """
        Stream answer generation (for real-time display)
        Args:
            question: User's question
            context_chunks: Retrieved context
            system_prompt: System instructions
            max_context_chars: Approximate character limit for context
        Yields:
            Text chunks as they're generated
        """
        context = self._build_context(context_chunks, max_chars=max_context_chars)
        
        full_prompt = f"""{system_prompt}

CONTEXT: {context}

QUESTION: {question}
"""
        
        try:
            response = self.model.generate_content(full_prompt, stream=True)
            
            for chunk in response:
                yield chunk.text
                
        except Exception as e:
            yield f"Error: {str(e)}"

    def _build_context(self, chunks: List[Dict], max_chars: int = 30000) -> str:
        """
        Build context string from chunks, respecting character limit
        Args:
            chunks: List of retrieved chunks
            max_chars: Maximum characters for the context string
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for i, chunk in enumerate(chunks, 1):
            # Extract metadata
            metadata = chunk.get('metadata', {})
            section = metadata.get('section_title', 'Unknown Section')
            page = metadata.get('page_number', 'N/A')
            similarity = chunk.get('similarity', 0)
            
            # Format chunk with metadata
            context_part = f"""
[Source {i}] (Section: {section}, Page: {page}, Relevance: {similarity:.2f})
{chunk['text']}
---
"""
            # Check if adding this part would exceed the limit
            if current_length + len(context_part) > max_chars:
                break
            
            context_parts.append(context_part)
            current_length += len(context_part)
            
        return "\n".join(context_parts)
        
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract source citations from chunks
        Args:
            chunks: Retrieved chunks
        Returns:
            List of source dicts for citation
        """
        sources = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            
            source = {
                'source_number': i,
                'text_preview': chunk['text'][:200] + "...",
                'section': metadata.get('section_title', ''),
                'page': metadata.get('page_number', ''),
                'similarity': chunk.get('similarity', 0)
            }
            sources.append(source)
            
        return sources
