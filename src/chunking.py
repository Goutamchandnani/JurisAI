"""
Document chunking module for RAG pipeline
Splits large documents into smaller, semantically meaningful chunks
"""

from typing import List, Dict, Optional, Any
import tiktoken
import re
import logging

logger = logging.getLogger(__name__)

class DocumentChunker:
    """
    Handles intelligent chunking of legal documents for RAG
    """
    
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize chunker
        Args:
            chunk_size: Target size of each chunk in tokens
            chunk_overlap: Number of overlapping tokens between chunks
            encoding_name: Tokenizer encoding to use
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            logger.warning(f"Could not load encoding {encoding_name}, falling back to cl100k_base. Error: {e}")
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        Args:
            text: Text to count
        Returns:
            Token count
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def _create_chunk_dict(self, text: str, start_idx: int, metadata: Dict = None) -> Dict:
        """Helper to create a standard chunk dictionary"""
        return {
            "text": text,
            "token_count": self.count_tokens(text),
            "start_char": start_idx,
            "end_char": start_idx + len(text),
            **(metadata or {})
        }

    def chunk_by_tokens(self, text: str) -> List[Dict]:
        """
        Split text into chunks by token count
        Args:
            text: Full document text
        Returns:
            List of chunk dicts with 'text', 'start_idx', 'end_idx', 'token_count'
        """
        # Simplistic token chunking - in a real scenario, we might want to respect word boundaries better
        # but for now we heavily rely on tiktoken decode/encode stability or just string slicing if mapped.
        # A more robust way is to encode all, then slice the token list.
        
        tokens = self.encoding.encode(text)
        total_tokens = len(tokens)
        chunks = []
        
        step = self.chunk_size - self.chunk_overlap
        if step <= 0:
            step = 1 # Avoid infinite loop
            
        for i in range(0, total_tokens, step):
            chunk_tokens = tokens[i : i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Find start_char in original text (approximate if decode changes things, but usually robust)
            # To be exact, we'd need to map tokens back to span indices. 
            # For this implementation, we will search for the substring, which can be ambiguous with repeats.
            # A better approach for exact indices: use a library/method that gives offsets.
            # Here we will do a best-effort find. Assuming sequential processing helps.
            
            # Simple offset tracking not fully implemented for raw token slicing without complex mapping.
            # We'll use a running index for "estimation" or regex based approach if we want exact chars.
            # For now, let's omit exact char indices for pure token chunking or assume the caller matches it up.
            # OR better: Assume this is a fallback and simple text slicing is preferred if token mapping is hard.
            
            # Let's try to do it via text slicing using the decoded text length as proxy, 
            # though this is imperfect for whitespace.
            
            chunks.append(self._create_chunk_dict(chunk_text, -1, {"strategy": "token"}))
            
            if i + self.chunk_size >= total_tokens:
                break
                
        return chunks

    def chunk_by_paragraphs(self, text: str) -> List[Dict]:
        """
        Split text by paragraphs, respecting semantic boundaries
        Args:
            text: Full document text
        Returns:
            List of chunk dicts
        """
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        current_char_start = 0
        
        # Build a map of paragraph start indices
        para_infos = []
        search_start = 0
        for p in paragraphs:
            start = text.find(p, search_start)
            if start == -1: start = search_start # Fallback
            para_infos.append({"text": p, "start": start})
            search_start = start + len(p)

        for i, para in enumerate(para_infos):
            p_text = para["text"]
            p_tokens = self.count_tokens(p_text)
            
            if current_tokens + p_tokens > self.chunk_size and current_chunk:
                # Store current chunk
                combined_text = "\n\n".join([p["text"] for p in current_chunk])
                chunk_start = current_chunk[0]["start"]
                chunks.append(self._create_chunk_dict(combined_text, chunk_start, {"strategy": "paragraph"}))
                
                # Apply overlap logic: keep last N paragraphs that fit within overlap budget
                # For simplicity in this version, we start fresh or keep just the last one if it fits
                overlap_tokens = 0
                new_chunk = []
                for old_p in reversed(current_chunk):
                    p_tok = self.count_tokens(old_p["text"])
                    if overlap_tokens + p_tok <= self.chunk_overlap:
                        new_chunk.insert(0, old_p)
                        overlap_tokens += p_tok
                    else:
                        break
                current_chunk = new_chunk
                current_tokens = overlap_tokens
            
            # If a single paragraph is too huge, we might need to split it (fallback to token chunking for it)
            if p_tokens > self.chunk_size:
                if current_chunk: # Flush current first
                    combined_text = "\n\n".join([p["text"] for p in current_chunk])
                    chunk_start = current_chunk[0]["start"]
                    chunks.append(self._create_chunk_dict(combined_text, chunk_start, {"strategy": "paragraph"}))
                    current_chunk = []
                    current_tokens = 0
                
                # Split this big paragraph
                sub_chunks = self.chunk_by_tokens(p_text)
                # Fix up offsets
                for sc in sub_chunks:
                     # token chunking returns -1 for start, we can't easily fix it without more logic
                     # keep as is or try to approximate
                     sc["start_char"] = para["start"] # Inaccurate but placeholder
                     sc["strategy"] = "paragraph_subsplit"
                     chunks.append(sc)
                continue

            current_chunk.append(para)
            current_tokens += p_tokens
            
        # Flush remainder
        if current_chunk:
            combined_text = "\n\n".join([p["text"] for p in current_chunk])
            chunk_start = current_chunk[0]["start"]
            chunks.append(self._create_chunk_dict(combined_text, chunk_start, {"strategy": "paragraph"}))
            
        return chunks
        
    def chunk_by_sections(self, text: str) -> List[Dict]:
        """
        Split legal document by sections (for contracts/agreements)
        Args:
            text: Full document text
        Returns:
            List of chunk dicts with section metadata
        """
        # Patterns for legal headers
        section_pattern = r'(?:^|\n)(?:SECTION|ARTICLE)\s+([0-9]+|[IVX]+)\.?\s*(.*)(?:\n|$)'
        numbered_pattern = r'(?:^|\n)([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s+(.*?)(?:\n|$)'
        header_caps_pattern = r'(?:^|\n)([A-Z][A-Z\s\(\)]+)(?:\n|$)' # e.g. DEFINITIONS
        
        # We can combine these or try them in priority. 
        # A simple approach: Find all matches, sort by position, and slice text between them.
        
        matches = []
        for pat in [section_pattern, numbered_pattern, header_caps_pattern]:
            for m in re.finditer(pat, text):
                matches.append({
                    "start": m.start(),
                    "end": m.end(),
                    "title": m.group(0).strip(),
                    "match_obj": m
                })
        
        # Sort matches by start position
        matches.sort(key=lambda x: x["start"])
        
        # Filter overlapping matches (greedy take first)
        unique_matches = []
        if matches:
            curr_end = -1
            for m in matches:
                if m["start"] >= curr_end:
                    unique_matches.append(m)
                    curr_end = m["end"]
        
        if not unique_matches:
            return self.chunk_by_paragraphs(text)
            
        chunks = []
        for i in range(len(unique_matches)):
            m = unique_matches[i]
            section_start = m["start"]
            
            # Content goes until next section start
            if i < len(unique_matches) - 1:
                section_end = unique_matches[i+1]["start"]
            else:
                section_end = len(text)
            
            section_text = text[section_start:section_end]
            
            # If section is too big, sub-chunk it
            if self.count_tokens(section_text) > self.chunk_size:
                sub_chunks = self.chunk_by_paragraphs(section_text)
                for sc in sub_chunks:
                    sc["section_title"] = m["title"]
                    # Adjust offsets relative to full text
                    sc["start_char"] += section_start
                    sc["end_char"] += section_start
                    chunks.append(sc)
            else:
                chunks.append(self._create_chunk_dict(section_text, section_start, {
                    "section_title": m["title"],
                    "strategy": "section"
                }))
                
        # Handle preamble if any
        if unique_matches[0]["start"] > 0:
            preamble = text[:unique_matches[0]["start"]]
            if preamble.strip():
                pre_chunks = self.chunk_by_paragraphs(preamble)
                chunks = pre_chunks + chunks
                
        return chunks
        
    def smart_chunk(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Intelligent chunking that tries multiple strategies
        Args:
            text: Full document text
            metadata: Additional metadata to attach to chunks
        Returns:
            List of optimized chunks with metadata
        """
        # Strategy:
        # 1. Try Section chunking. If it finds sections and chunks are reasonable, use it.
        # 2. If 'section' strategy returned just one huge chunk or fallback, try paragraph.
        # 3. Always apply size limits (chunk_by_sections calls sub-chunkers if needed).
        
        chunks = self.chunk_by_sections(text)
        
        # If section chunking completely failed (e.g. no sections found, returned paragraph chunks),
        # it might have already fallen back to paragraphs.
        
        # Post-processing: Enrich with metadata
        final_chunks = []
        for i, chunk in enumerate(chunks):
            # Merge provided metadata
            if metadata:
                chunk.update(metadata)
            
            chunk["chunk_index"] = i
            chunk["chunk_id"] = f"chnk_{i}_{chunk.get('start_char', 0)}" 
            final_chunks.append(chunk)
            
        return self.optimize_chunks(final_chunks)
        
    def optimize_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Post-process chunks to optimize for retrieval
        Args:
            chunks: Initial chunks
        Returns:
            Optimized chunks
        """
        if not chunks:
            return []
            
        optimized = []
        for chunk in chunks:
            # Remove very small chunks (junk)
            if chunk["token_count"] < 10: 
                # Could try to merge with previous, but for now just drop if it's pure noise
                # Be careful not to drop short but important headers
                continue
            
            optimized.append(chunk)
            
        return optimized

