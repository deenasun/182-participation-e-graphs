"""
PDF processing utilities for extracting text from PDF attachments.
"""

import PyPDF2
import requests
from io import BytesIO
from typing import List

def extract_pdf_text(pdf_url: str, max_pages: int = 3) -> str:
    """
    Download and extract text from PDF (first N pages).
    
    Args:
        pdf_url: URL to PDF file
        max_pages: Maximum number of pages to extract (default: 3)
        
    Returns:
        Extracted text (limited to 5000 chars)
    """
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for i in range(min(len(reader.pages), max_pages)):
            text += reader.pages[i].extract_text()
        
        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        print(f"Error extracting PDF {pdf_url}: {e}")
        return ""

def process_attachments(attachment_urls: List[str]) -> str:
    """
    Extract text from all PDF attachments.
    
    Args:
        attachment_urls: List of attachment URLs
        
    Returns:
        Concatenated text from all PDFs
    """
    summaries = []
    for url in attachment_urls:
        if url.endswith('.pdf'):
            text = extract_pdf_text(url)
            if text:
                summaries.append(text)
    
    return " ".join(summaries)
