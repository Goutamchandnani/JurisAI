"""
Legal Document Q&A System with RAG
Main Streamlit Application
"""

import streamlit as st
import os
from dotenv import load_dotenv
import logging
import time

# Import our modules
from src.pdf_processor import extract_text_from_pdf, get_pdf_metadata
from src.chunking import DocumentChunker
from src.embeddings import GeminiEmbedder
from src.vector_store import VectorStore
from src.gemini_client import GeminiRAGClient
from src.utils import save_uploaded_file, format_file_size
from config.prompts import (
    LEGAL_SYSTEM_PROMPT,
    SAMPLE_QUESTIONS,
    APP_CONFIG,
    CUSTOM_CSS,
    ERROR_MESSAGES,
    LEGAL_DISCLAIMER
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG['page_title'],
    page_icon=APP_CONFIG['page_icon'],
    layout=APP_CONFIG['layout']
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    if 'current_doc_name' not in st.session_state:
        st.session_state.current_doc_name = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'embedder' not in st.session_state:
        st.session_state.embedder = None
    if 'rag_client' not in st.session_state:
        st.session_state.rag_client = None
    if 'chunker' not in st.session_state:
        st.session_state.chunker = None


def initialize_clients():
    """Initialize API clients and components"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error(ERROR_MESSAGES['no_api_key'])
        st.stop()
    
    try:
        # Initialize components if not already done
        if st.session_state.embedder is None:
            st.session_state.embedder = GeminiEmbedder(api_key)
            
        if st.session_state.rag_client is None:
            st.session_state.rag_client = GeminiRAGClient(api_key)
            
        if st.session_state.chunker is None:
            chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
            chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))
            st.session_state.chunker = DocumentChunker(chunk_size, chunk_overlap)
            
        if st.session_state.vector_store is None:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./data/vectordb")
            st.session_state.vector_store = VectorStore(persist_dir)
            
    except Exception as e:
        st.error(f"Initialization error: {str(e)}")
        st.stop()


def process_document(uploaded_file):
    """
    Process uploaded PDF through RAG pipeline
    """
    with st.spinner("Processing document..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Save file
            status_text.text("Saving document...")
            progress_bar.progress(10)
            file_path = save_uploaded_file(uploaded_file)
            
            # Step 2: Extract text
            status_text.text("Extracting text from PDF...")
            progress_bar.progress(20)
            extraction_result = extract_text_from_pdf(file_path)
            
            if not extraction_result['success']:
                st.error(f"Failed to extract text: {extraction_result.get('error', 'Unknown error')}")
                return False
                
            full_text = extraction_result['text']
            
            # Step 3: Chunk document
            status_text.text("Chunking document...")
            progress_bar.progress(40)
            chunks = st.session_state.chunker.smart_chunk(
                full_text,
                metadata={'source_file': uploaded_file.name}
            )
            
            st.info(f"Created {len(chunks)} chunks")
            
            # Step 4: Generate embeddings
            status_text.text("Generating embeddings...")
            progress_bar.progress(60)
            embedded_chunks = st.session_state.embedder.embed_chunks(chunks)
            
            # Step 5: Store in vector database
            status_text.text("Storing in vector database...")
            progress_bar.progress(80)
            
            collection_name = f"doc_{uploaded_file.name.replace('.pdf', '').replace(' ', '_')}"
            collection = st.session_state.vector_store.create_collection(
                collection_name,
                reset=True
            )
            
            num_added = st.session_state.vector_store.add_documents(
                collection,
                embedded_chunks,
                chunks, # Pass the text documents
                metadatas=[{'source': uploaded_file.name}] * len(chunks)
            )
            
            # Update session state
            st.session_state.collection = collection
            st.session_state.current_doc_name = uploaded_file.name
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Document processed successfully!")
            
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            return True
            
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            logger.error(f"Document processing failed: {e}", exc_info=True)
            return False


def answer_question(question: str):
    """
    Answer question using RAG pipeline
    """
    if st.session_state.collection is None:
        st.error(ERROR_MESSAGES['no_document'])
        return
    
    with st.spinner("Searching document and generating answer..."):
        try:
            # Step 1: Generate query embedding
            query_embedding = st.session_state.embedder.embed_query(question)
            
            if query_embedding is None:
                st.error("Failed to generate query embedding")
                return
            
            # Step 2: Search vector database
            top_k = int(os.getenv("TOP_K_RESULTS", 5))
            relevant_chunks = st.session_state.vector_store.search(
                st.session_state.collection,
                query_embedding,
                top_k=top_k
            )
            
            if not relevant_chunks:
                st.warning("No relevant information found in the document")
                return
            
            # Step 3: Generate answer using Gemini
            result = st.session_state.rag_client.generate_answer(
                question=question,
                context_chunks=relevant_chunks,
                system_prompt=LEGAL_SYSTEM_PROMPT
            )
            
            if result['success']:
                # Display answer
                st.markdown("### Answer")
                st.markdown(f"""<div class="answer-box">{result['answer']}</div>""", unsafe_allow_html=True)
                
                # Display sources
                with st.expander("View Sources", expanded=False):
                    for source in result['sources']:
                        st.markdown(f"""
                        **Source {source['source_number']}** - {source['section']} (Page: {source['page']})  
                        Relevance: {source['similarity']:.2%}
                        
                        {source['text_preview']}
                        
                        ---
                        """)
                
                # Add to message history
                st.session_state.messages.append({
                    'question': question,
                    'answer': result['answer'],
                    'sources': result['sources']
                })
                
            else:
                st.error(f"Failed to generate answer: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"Error answering question: {str(e)}")
            logger.error(f"Question answering failed: {e}", exc_info=True)


def main():
    """Main application"""
    
    # Initialize
    initialize_session_state()
    initialize_clients()
    
    # Sidebar
    with st.sidebar:
        st.title("JurisAI")
        st.markdown("### Document Intelligence")
        st.markdown("---")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Legal Document",
            type=['pdf'],
            help="Supported formats: PDF"
        )
        
        if uploaded_file:
            # Show file info
            file_size = len(uploaded_file.getvalue())
            st.info(f"{uploaded_file.name}\nSize: {format_file_size(file_size)}")
            
            # Process button
            if st.button("Analyze Document", type="primary"):
                if process_document(uploaded_file):
                    st.success("Analysis Complete")
                    st.rerun()
        
        # Sample questions
        if st.session_state.current_doc_name:
            st.markdown("---")
            st.markdown("### Suggested Inquiries")
            
            for q in SAMPLE_QUESTIONS['general'][:5]:
                if st.button(q, key=f"sample_{q}"):
                    answer_question(q)
                    
        # Settings
        with st.expander("System Configuration"):
            st.text(f"Chunk Size: {os.getenv('CHUNK_SIZE', 1000)}")
            st.text(f"Top-K: {os.getenv('TOP_K_RESULTS', 5)}")
        
        # Disclaimer
        st.markdown("---")
        st.markdown(f'<div class="disclaimer">{LEGAL_DISCLAIMER}</div>', unsafe_allow_html=True)
    
    # Main area
    st.markdown("# Document Analysis")
    
    if st.session_state.current_doc_name:
        st.success(f"Active Document: **{st.session_state.current_doc_name}**")
        
        # Question input
        question = st.chat_input("Enter your query regarding the document...")
        
        if question:
            # Display user question
            with st.chat_message("user"):
                st.markdown(question)
            
            # Generate and display answer
            with st.chat_message("assistant"):
                answer_question(question)
        
        # Display chat history
        if st.session_state.messages:
            st.markdown("---")
            st.markdown("### Inquiry History")
            
            for i, msg in enumerate(reversed(st.session_state.messages)):
                with st.expander(f"Q: {msg['question'][:100]}...", expanded=(i==0)):
                    st.markdown(f"**Question:** {msg['question']}")
                    st.markdown(f"**Answer:** {msg['answer']}")
                    
    else:
        # Welcome message with modern design
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0 2rem 0;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem;">JurisAI</h1>
            <p style="font-size: 1.2rem; color: var(--text-secondary); margin-bottom: 3rem;">
                Advanced Legal Document Intelligence Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("Upload a legal document from the sidebar to begin your analysis.")
        
        # Feature showcase with modern cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">Semantic Search</h3>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Context-aware retrieval of relevant clauses and provisions using advanced AI embeddings.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">Source Citations</h3>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Every answer includes direct references to source text with page numbers and relevance scores.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon"></div>
                <h3 style="color: var(--accent-gold); margin-bottom: 1rem;">AI Precision</h3>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Powered by advanced RAG architecture and Google's Gemini AI for accurate legal analysis.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional info section
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-subtle);">
                <h4 style="color: var(--accent-gold); margin-bottom: 1rem;">Key Features</h4>
                <ul style="color: var(--text-secondary); line-height: 2;">
                    <li>PDF document processing</li>
                    <li>Intelligent text chunking</li>
                    <li>Vector-based semantic search</li>
                    <li>Natural language Q&A</li>
                    <li>Citation tracking</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-subtle);">
                <h4 style="color: var(--accent-gold); margin-bottom: 1rem;">Use Cases</h4>
                <ul style="color: var(--text-secondary); line-height: 2;">
                    <li>Contract analysis</li>
                    <li>Legal research</li>
                    <li>Compliance review</li>
                    <li>Due diligence</li>
                    <li>Document summarization</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
