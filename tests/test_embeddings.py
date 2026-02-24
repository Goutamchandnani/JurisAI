
import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from embeddings import GeminiEmbedder

def test_embeddings():
    print("Testing GeminiEmbedder...")
    
    # API Key provided by user
    api_key = "AIzaSyAjdrjRQ4NU1IFX1UI9YXTv4qvA-XVyhos" 
    
    if not api_key:
        print("Error: No API Key provided.")
        return

    try:
        embedder = GeminiEmbedder(api_key=api_key)
        
        # 1. Test Single Embedding
        print("\n1. Testing Single Embedding...")
        text = "This is a test sentence for embedding generation."
        embedding = embedder.embed_text(text)
        
        if embedding and len(embedding) == 768:
            print("SUCCESS: Generated embedding with correct dimension (768).")
        else:
            print(f"FAILURE: Embedding generation failed or wrong dimension. Result: {type(embedding)}")
            if embedding: print(f"Dimension: {len(embedding)}")

        # 2. Test Batch Embedding
        print("\n2. Testing Batch Embedding...")
        texts = [
            "First sentence.",
            "Second sentence.",
            "Third sentence is a bit longer."
        ]
        embeddings = embedder.embed_batch(texts, batch_size=2)
        
        if len(embeddings) == 3 and all(len(e) == 768 for e in embeddings if e):
            print("SUCCESS: Generated batch embeddings.")
        else:
            print("FAILURE: Batch embedding generation failed.")

        # 3. Test Similarity
        print("\n3. Testing Similarity...")
        vec1 = embedder.embed_text("Apple is a fruit")
        vec2 = embedder.embed_text("Banana is also a fruit")
        vec3 = embedder.embed_text("The sky is blue")
        
        sim1 = embedder.calculate_similarity(vec1, vec2)
        sim2 = embedder.calculate_similarity(vec1, vec3)
        
        print(f"Similarity (Fruit vs Fruit): {sim1:.4f}")
        print(f"Similarity (Fruit vs Sky): {sim2:.4f}")
        
        if sim1 > sim2:
            print("SUCCESS: Semantic similarity logic works (Fruit > Sky).")
        else:
            print("FAILURE: Similarity logic seems off.")

    except Exception as e:
        print(f"CRITICAL ERROR during testing: {e}")

if __name__ == "__main__":
    test_embeddings()
