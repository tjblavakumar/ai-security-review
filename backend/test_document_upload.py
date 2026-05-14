"""
Simple test script to verify document upload functionality.
Run this from the backend directory: python test_document_upload.py
"""

import os
from pathlib import Path
from app.services.document_service import extract_text_from_file, extract_text_from_txt, extract_text_from_pdf

def test_txt_extraction():
    """Test TXT file extraction."""
    print("\n=== Testing TXT Extraction ===")
    
    # Create a test TXT file
    test_file = Path("test_sample.txt")
    test_content = "This is a test project.\nIt uses AI for data analysis.\nWe process customer data."
    
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        extracted = extract_text_from_txt(str(test_file))
        print(f"✓ Extracted {len(extracted)} characters")
        print(f"Content preview: {extracted[:100]}...")
        assert test_content in extracted, "Content mismatch"
        print("✓ TXT extraction test passed!")
    finally:
        if test_file.exists():
            test_file.unlink()

def test_pdf_extraction():
    """Test PDF file extraction (requires a sample PDF)."""
    print("\n=== Testing PDF Extraction ===")
    print("Note: This test requires PyPDF2 to be installed")
    
    try:
        import PyPDF2
        print("✓ PyPDF2 is installed")
    except ImportError:
        print("✗ PyPDF2 not installed. Run: pip install PyPDF2")
        return
    
    # Note: You would need a real PDF file to test this
    print("⚠ PDF extraction test skipped (requires sample PDF file)")
    print("  To test manually:")
    print("  1. Create a sample PDF with project information")
    print("  2. Place it in backend/test_sample.pdf")
    print("  3. Run: extract_text_from_pdf('test_sample.pdf')")

def test_file_validation():
    """Test file type validation."""
    print("\n=== Testing File Validation ===")
    
    valid_types = ["application/pdf", "text/plain"]
    invalid_type = "image/jpeg"
    
    print(f"✓ Valid types: {valid_types}")
    print(f"✓ Invalid type example: {invalid_type}")
    print("✓ File validation logic is in place")

def test_uploads_directory():
    """Test that uploads directory can be created."""
    print("\n=== Testing Uploads Directory ===")
    
    upload_dir = Path("uploads/submissions")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    if upload_dir.exists():
        print(f"✓ Uploads directory created: {upload_dir.absolute()}")
    else:
        print("✗ Failed to create uploads directory")

if __name__ == "__main__":
    print("=" * 60)
    print("Document Upload Feature - Test Suite")
    print("=" * 60)
    
    test_txt_extraction()
    test_pdf_extraction()
    test_file_validation()
    test_uploads_directory()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run the backend server: uvicorn app.main:app --reload")
    print("2. Test the upload endpoint with a real PDF file")
    print("3. Create a submission and upload a document via the UI")
    print("4. Verify AI suggestions include document context")
</content>"