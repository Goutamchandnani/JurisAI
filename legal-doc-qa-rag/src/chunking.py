"""
Document Chunking Module
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len
        )

    def smart_chunk(self, text, metadata=None):
        """
        Chunk text intelligently
        """
        if metadata is None:
            metadata = {}
            
        chunks = self.splitter.create_documents([text], metadatas=[metadata])
        
        # Post-process chunks to ensure they have content
        valid_chunks = [chunk.page_content for chunk in chunks if chunk.page_content.strip()]
        
        return valid_chunks
