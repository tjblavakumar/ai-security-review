# Quick Start Guide: Document Upload Feature

## Prerequisites

1. Backend and frontend servers running
2. Database migrated with new columns
3. PyPDF2 installed (already in requirements.txt)

## Step 1: Database Migration

```bash
cd backend

# Option A: Manual SQL
sqlite3 app.db
ALTER TABLE submissions ADD COLUMN uploaded_document_path VARCHAR(500);
ALTER TABLE submissions ADD COLUMN uploaded_document_name VARCHAR(255);
ALTER TABLE submissions ADD COLUMN uploaded_document_content TEXT;
.exit

# Option B: Alembic (recommended)
alembic revision --autogenerate -m "Add document upload fields"
alembic upgrade head
```

## Step 2: Test Document Processing

```bash
cd backend
python test_document_upload.py
```

This will verify:
- TXT file extraction works
- PyPDF2 is installed
- Uploads directory can be created

## Step 3: Create a Test Document

Create a sample project document (save as `test_project.txt`):

```
Project Name: Customer Analytics AI Platform

Project Description:
We are building an AI-powered analytics platform that processes customer transaction data
to provide personalized recommendations. The system uses machine learning models to analyze
purchasing patterns and predict future behavior.

Data Processed:
- Customer names and email addresses
- Transaction history and purchase amounts
- Browsing behavior and click patterns
- Geographic location data

Third-Party Services:
- AWS for cloud hosting
- Stripe for payment processing
- SendGrid for email notifications
- Google Analytics for tracking

Security Measures:
- Data encrypted at rest and in transit
- Role-based access control
- Regular security audits
- GDPR compliance measures

Go-Live Date: Q2 2024
```

## Step 4: Test the Feature

### 4.1 Create Submission with Document

1. Navigate to http://localhost:3000
2. Click "Submit Infosec Request" (blue button)
3. Fill in the form:
   - Project Name: "Customer Analytics AI Platform"
   - Project Description: "AI-powered customer analytics"
   - Your Name: "John Doe"
   - Your Email: "john@example.com"
   - Team/Department: "Data Science"
   - Project Type: "New Project"
4. Click "Choose File (PDF or TXT)"
5. Upload your `test_project.txt` file
6. Verify the file appears with name and size
7. Click "Start Questionnaire"

### 4.2 Test AI Suggestions with Document Context

1. Navigate through the questionnaire
2. On questions about data types, click "AI Suggestion"
3. **Expected Result**: AI should reference the uploaded document
   - Example: "Based on your project document, you process customer names, emails, transaction history..."
4. Try different questions:
   - Data Privacy questions
   - Third-party services questions
   - Security measures questions
5. Verify AI suggestions are more accurate and specific

### 4.3 Verify Backend

```bash
# Check if file was uploaded
ls backend/uploads/submissions/
# Should see: 1_test_project.txt (or similar)

# Check database
sqlite3 backend/app.db
SELECT id, project_name, uploaded_document_name, 
       LENGTH(uploaded_document_content) as content_length 
FROM submissions;
.exit
```

## Step 5: Test Error Handling

### Test Invalid File Type
1. Try uploading a .jpg or .docx file
2. **Expected**: Error message "Only PDF and TXT files are allowed"

### Test Large File
1. Create a file > 10MB
2. Try uploading
3. **Expected**: Error message "File size must be less than 10MB"

### Test Without Document
1. Create a submission without uploading a document
2. **Expected**: Everything works normally
3. AI suggestions work but without document context

## Step 6: Test PDF Upload

Create a PDF version of the test document:
1. Copy the test content to a Word document
2. Save as PDF: `test_project.pdf`
3. Upload the PDF instead of TXT
4. Verify text extraction works
5. Check AI suggestions include PDF content

## Troubleshooting

### File Upload Fails
- Check backend logs for errors
- Verify `uploads/submissions/` directory exists
- Check file permissions
- Ensure PyPDF2 is installed: `pip install PyPDF2`

### AI Doesn't Use Document Content
- Check database: `uploaded_document_content` should have text
- Verify document is under 4000 characters (or truncated)
- Check backend logs for AI service calls
- Ensure LLM provider is configured

### PDF Text Extraction Fails
- Some PDFs may have encoding issues
- Scanned PDFs without OCR won't extract text
- Try converting to TXT first
- Check PyPDF2 version: `pip show PyPDF2`

## API Testing with cURL

```bash
# 1. Create submission
curl -X POST http://localhost:8000/api/submissions \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Test Project",
    "submitter_name": "John Doe",
    "submitter_email": "john@example.com",
    "project_type": "new"
  }'

# Note the submission ID from response (e.g., 1)

# 2. Upload document
curl -X POST http://localhost:8000/api/submissions/1/upload-document \
  -F "file=@test_project.txt"

# 3. Get submission to verify
curl http://localhost:8000/api/submissions/1

# 4. Test AI suggestion with document context
curl -X POST http://localhost:8000/api/ai/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "submission_id": 1
  }'
```

## Success Criteria

✅ File upload UI appears on submission page
✅ Can upload PDF and TXT files
✅ File validation works (type and size)
✅ File appears in uploads directory
✅ Database contains extracted text
✅ AI suggestions reference document content
✅ Error handling works for invalid files
✅ Submission works without document upload

## Next Steps

Once testing is complete:
1. Create sample project documents for common use cases
2. Train users on the document upload feature
3. Monitor AI suggestion quality improvements
4. Consider adding more file type support
5. Implement document preview feature

## Support

For issues or questions:
1. Check `DOCUMENT_UPLOAD_FEATURE.md` for detailed documentation
2. Review `IMPLEMENTATION_SUMMARY.md` for technical details
3. Run `python test_document_upload.py` for diagnostics
4. Check backend logs: `uvicorn app.main:app --reload --log-level debug`
</content>