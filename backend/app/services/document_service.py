"""Service for document processing and text extraction."""

import PyPDF2
from pathlib import Path


def extract_text_from_file(file_path: str, content_type: str) -> str:
    """
    Extract text content from a file (PDF or TXT).
    
    Args:
        file_path: Path to the file
        content_type: MIME type of the file
        
    Returns:
        Extracted text content
        
    Raises:
        Exception: If text extraction fails
    """
    if content_type == "text/plain":
        return extract_text_from_txt(file_path)
    elif content_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a TXT file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyPDF2."""
    text_content = []
    
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
        
        return "\n\n".join(text_content)
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def summarize_document(content: str, max_length: int = 4000) -> str:
    """
    Summarize or truncate document content to fit within token limits.
    
    Args:
        content: Full document content
        max_length: Maximum character length
        
    Returns:
        Truncated or summarized content
    """
    if len(content) <= max_length:
        return content
    
    # Simple truncation with ellipsis
    # In a production system, you might want to use LLM summarization here
    return content[:max_length] + "\n\n... (document truncated for length)"
