"""
PDF Processing Module
"""
import pdfplumber
import os
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF file using pdfplumber
    Returns dict with success status and text
    """
    try:
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    # Add page marker for context
                    text_content.append(f"--- Page {i+1} ---\n{page_text}")
        
        full_text = "\n\n".join(text_content)
        
        return {
            "success": True,
            "text": full_text,
            "page_count": len(text_content)
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_pdf_metadata(file_path):
    """
    Get metadata from PDF file
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            return pdf.metadata
    except Exception as e:
        logger.error(f"Error getting metadata: {str(e)}")
        return {}
