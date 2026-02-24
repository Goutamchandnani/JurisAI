"""
Configuration and Prompts for Legal Doc RAG
"""

# App Configuration
APP_CONFIG = {
    "page_title": "JurisAI - Legal Intelligence",
    "page_icon": "None",
    "layout": "wide"
}

# Custom CSS for Modern Legal Tech UI
CUSTOM_CSS = """
<style>
    /* Import Premium Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        /* Modern Legal Tech Color Palette */
        --primary-navy: #0A1628;
        --secondary-navy: #1A2942;
        --accent-gold: #C9A961;
        --accent-gold-light: #E5D4A6;
        --accent-blue: #4A90E2;
        --bg-main: #0F1419;
        --bg-card: #1A2332;
        --bg-elevated: #243447;
        --text-primary: #E8EDF4;
        --text-secondary: #A8B5C7;
        --text-muted: #6B7A8F;
        --border-subtle: rgba(201, 169, 97, 0.15);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        --shadow-gold: 0 4px 20px rgba(201, 169, 97, 0.2);
    }

    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #0A1628 0%, #1A2942 50%, #0F1419 100%);
        background-attachment: fixed;
        color: var(--text-primary);
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif;
        color: var(--text-primary);
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    h1 {
        font-size: 2.75rem;
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        text-shadow: 0 2px 10px rgba(201, 169, 97, 0.3);
    }

    /* Sidebar - Premium Dark Design */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-navy) 0%, var(--secondary-navy) 100%);
        border-right: 1px solid var(--border-subtle);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 200px;
        background: radial-gradient(circle at top center, rgba(201, 169, 97, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* Sidebar Text Styling */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: var(--accent-gold) !important;
        font-family: 'Cormorant Garamond', serif !important;
        text-align: center;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] h1 {
        font-size: 2.5rem !important;
        margin: 2rem 0 0.5rem 0;
        text-shadow: 0 2px 20px rgba(201, 169, 97, 0.4);
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
        font-weight: 400;
        letter-spacing: 3px;
        margin-bottom: 2rem;
    }
    
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--accent-gold) 50%, transparent 100%);
        margin: 2rem 0;
        opacity: 0.3;
    }
    
    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton>button {
        background: rgba(201, 169, 97, 0.1);
        border: 1px solid var(--border-subtle);
        color: var(--text-secondary);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        width: 100%;
        margin: 0.3rem 0;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        background: rgba(201, 169, 97, 0.2);
        border-color: var(--accent-gold);
        color: var(--accent-gold);
        transform: translateX(4px);
        box-shadow: var(--shadow-gold);
    }
    
    /* Sidebar Expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: var(--text-secondary) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        font-size: 0.85rem;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(201, 169, 97, 0.1) !important;
        border-color: var(--accent-gold);
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-subtle);
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }

    /* Primary Action Button */
    .stButton>button[kind="primary"],
    .stButton>button[data-baseweb="button"][kind="primary"] {
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
        color: var(--primary-navy);
        border: none;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0.75rem 2rem;
        box-shadow: var(--shadow-gold);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button[kind="primary"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button[kind="primary"]:hover::before {
        left: 100%;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(201, 169, 97, 0.4);
    }

    /* Regular Buttons */
    .stButton>button {
        background: var(--bg-elevated);
        color: var(--text-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .stButton>button:hover {
        background: var(--bg-card);
        border-color: var(--accent-gold);
        color: var(--accent-gold);
        box-shadow: var(--shadow-md);
    }

    /* File Uploader - Glassmorphism */
    [data-testid="stFileUploader"] {
        background: rgba(26, 35, 50, 0.6);
        border: 2px dashed var(--border-subtle);
        border-radius: 16px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-gold);
        background: rgba(26, 35, 50, 0.8);
        box-shadow: var(--shadow-gold);
    }
    
    [data-testid="stFileUploader"] label {
        color: var(--text-secondary) !important;
        font-weight: 500;
        font-size: 0.95rem;
    }

    /* Info/Success/Warning Boxes */
    .stAlert {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-sm);
    }
    
    [data-baseweb="notification"] {
        background: var(--bg-card) !important;
        border-left: 4px solid var(--accent-gold);
        border-radius: 8px;
        box-shadow: var(--shadow-md);
    }

    /* Chat Messages */
    .stChatMessage {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-md);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        border-color: var(--accent-gold);
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, var(--accent-blue) 0%, #5BA3F5 100%);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
        box-shadow: var(--shadow-gold);
    }

    /* Chat Input */
    .stChatInput {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .stChatInput:focus-within {
        border-color: var(--accent-gold);
        box-shadow: var(--shadow-gold);
    }

    /* Answer Box - Premium Card */
    .answer-box {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-elevated) 100%);
        padding: 2rem;
        border-left: 4px solid var(--accent-gold);
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        line-height: 1.8;
        color: var(--text-primary);
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-subtle);
        margin: 1rem 0;
    }
    
    .answer-box strong {
        color: var(--accent-gold);
        font-weight: 600;
    }

    /* Expander - Modern Accordion */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-elevated);
        border-color: var(--accent-gold);
        box-shadow: var(--shadow-md);
    }
    
    .streamlit-expanderContent {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
        border-radius: 10px;
        box-shadow: var(--shadow-gold);
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--accent-gold) !important;
    }

    /* Code Blocks */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(0, 0, 0, 0.3);
        color: var(--accent-gold-light);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
        border: 1px solid var(--border-subtle);
    }

    /* Disclaimer */
    .disclaimer {
        font-size: 0.8rem;
        color: var(--text-muted);
        font-style: italic;
        text-align: justify;
        line-height: 1.6;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
        border: 1px solid rgba(201, 169, 97, 0.1);
    }

    /* Feature Cards */
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-sm);
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: var(--accent-gold);
        box-shadow: var(--shadow-lg);
        background: var(--bg-elevated);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--accent-gold) 0%, var(--accent-gold-light) 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-gold-light);
    }

    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stMarkdown, .stChatMessage, .answer-box {
        animation: fadeInUp 0.5s ease-out;
    }

    /* Responsive Typography */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        [data-testid="stSidebar"] h1 {
            font-size: 1.75rem !important;
        }
    }
</style>
"""

# Error Messages
ERROR_MESSAGES = {
    "no_api_key": "Gemini API Key not found! Please set it in the .env file.",
    "no_document": "Please upload and process a document first.",
    "processing_failed": "Failed to process document.",
    "answer_failed": "Failed to generate answer."
}

# Legal Disclaimer
LEGAL_DISCLAIMER = """
**Disclaimer**: This AI assistant provides information based on the uploaded documents but does NOT constitute legal advice. 
Always consult with a qualified attorney for legal matters.
"""

# System Prompt for Gemini
LEGAL_SYSTEM_PROMPT = """
You are an expert legal assistant AI designed to answer questions based strictly on the provided legal document context.

Instructions:
1.  **Analyze the Context**: Read the provided document chunks carefully.
2.  **Answer the Question**: Answer the user's question using ONLY the information from the context.
3.  **Cite Sources**: You MUST cite the specific section numbers or page numbers from the context in your answer.
4.  **No Outside Knowledge**: Do not use outside knowledge or assumptions. If the answer is not in the context, state "I cannot find the answer in the provided document."
5.  **Legal Tone**: Maintain a professional, objective, and precise tone suitable for legal matters.
6.  **Formatting**: Use Markdown for readability (bullet points, bold text for key terms).

Context:
{context}

Question:
{question}
"""

# Sample Questions
SAMPLE_QUESTIONS = {
    "general": [
        "What is the purpose of this agreement?",
        "What are the termination conditions?",
        "Describe the confidentiality obligations.",
        "What is the governing law?",
        "Are there any indemnification clauses?"
    ]
}
