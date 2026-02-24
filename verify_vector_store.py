import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from vector_store import VectorStore
    print("Successfully imported VectorStore")
    
    # Initialize (will create directory)
    vs = VectorStore(persist_directory="./data/vectordb_test")
    print("Successfully initialized VectorStore")
    
    # Create collection
    col = vs.create_collection("test_collection", reset=True)
    print("Successfully created collection")
    
    # Add dummy data
    chunks = [{
        'chunk_id': '1',
        'text': 'This is a test document',
        'embedding': [0.1] * 384, # Dummy embedding size typical for basic models
        'metadata': {'source': 'test'}
    }]
    # We need to make sure embedding length matches what Chroma expects if using default? 
    # Actually we disabled default embedding function by passing embeddings directly.
    # But wait, in vector_store.py we are passing embeddings.
    # We should make sure we pass valid data.
    
    # For this test, we might fail if we don't have embeddings. 
    # The user code expects us to pass embeddings in the chunks.
    # Let's just test import and init for now to verify structure and dependencies.
    
except ImportError as e:
    print(f"ImportError: {e}")
    print("Please install requirements: pip install -r requirements.txt")
except Exception as e:
    print(f"Error: {e}")
