
import sys
import os

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

from src.chunking import DocumentChunker
import json

SAMPLE_LEGAL_TEXT = """
AGREEMENT OF SERVICES

This Agreement is made on this 1st day of January, 2024.

SECTION 1. DEFINITIONS

1.1 "Services" shall mean the consulting services provided by the Contractor.
1.2 "Client" shall mean the party receiving the Services.

SECTION 2. SCOPE OF WORK

The Contractor agrees to perform the following Services:
(a) Analysis of current systems.
(b) Implementation of new software.

This is a very long paragraph to test paragraph chunking. It contains multiple sentences and should ideally be kept together if it fits within the chunk size. However, if it is too long, it might need to be split. But in this case, it is not actually that long, so it should be fine.

ARTICLE 3. COMPENSATION

3.1 Fees. The Client agrees to pay the Contractor at a rate of $200 per hour.
3.2 Expenses. The Client shall reimburse the Contractor for all reasonable expenses.

SECTION 4. TERMINATION

This Agreement may be terminated by either party with 30 days' written notice.
Upon key termination, all outstanding fees shall become immediately due and payable.

"""

def print_chunks(name, chunks):
    print(f"\n--- {name} ({len(chunks)} chunks) ---")
    for i, c in enumerate(chunks):
        print(f"Chunk {i}: {c['token_count']} tokens")
        print(f"Metadata: {json.dumps({k:v for k,v in c.items() if k != 'text'})}")
        print(f"Text Preview: {c['text'][:50]}...")
        print("-" * 20)

def main():
    print("Initializing DocumentChunker...")
    try:
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return

    print("\n1. Testing chunk_by_tokens")
    tokens_chunks = chunker.chunk_by_tokens(SAMPLE_LEGAL_TEXT)
    print_chunks("Token Chunks", tokens_chunks)

    print("\n2. Testing chunk_by_paragraphs")
    para_chunks = chunker.chunk_by_paragraphs(SAMPLE_LEGAL_TEXT)
    print_chunks("Paragraph Chunks", para_chunks)

    print("\n3. Testing chunk_by_sections")
    sect_chunks = chunker.chunk_by_sections(SAMPLE_LEGAL_TEXT)
    print_chunks("Section Chunks", sect_chunks)
    
    print("\n4. Testing smart_chunk")
    smart_chunks = chunker.smart_chunk(SAMPLE_LEGAL_TEXT, metadata={"doc_id": "123"})
    print_chunks("Smart Chunks", smart_chunks)

if __name__ == "__main__":
    main()
