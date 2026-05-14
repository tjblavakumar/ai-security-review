# Document Upload Feature

## Overview
This feature allows users to upload project documents (PDF or TXT files) when creating a new security review submission. The AI will automatically use the document content to help populate responses throughout the questionnaire.

## How It Works

### 1. User Flow
1. User creates a new submission on the first page
2. Optionally uploads a PDF or TXT file containing project information
3. File is processed and text is extracted
4. When user clicks "AI Suggestion" on any question, the AI uses:
   - The question context
   - Previous responses
   - Policy documents (RAG)
   - **Uploaded document content** (NEW!)

### 2. Technical Implementation

#### Backend Changes

**Database Schema:**
- Added 3 new columns to `submissions` table:
  - `uploaded_document_path`: File storage path
  - `uploaded_document_name`: Original filename
  - `uploaded_document_content`: Extracted text content

**New Endpoint:**
```
POST /api/submissions/{submission_id}/upload-document
Content-Type: multipart/form-data
```

**Document Processing:**
- New service: `backend/app/services/document_service.py`
- Supports PDF (via PyPDF2) and TXT files
- Extracts and stores text content
- Truncates to 4000 characters for AI context

**AI Enhancement:**
- Modified `ai_service.generate_suggestion()` to accept `document_context`
- Document content is included in AI prompts
- AI can reference uploaded document when generating suggestions

#### Frontend Changes

**File Upload UI:**
- Added file input component to submission creation page
- Shows file name and size after selection
- Remove file option before submission
- Validates file type (PDF/TXT only) and size (max 10MB)

**Upload Process:**
1. Create submission first
2. Upload document if provided
3. Navigate to questionnaire

### 3. File Storage

Files are stored in: `backend/uploads/submissions/`
Format: `{submission_id}_{original_filename}`

### 4. Security Considerations

- File type validation (PDF and TXT only)
- File size limit (10MB)
- Files stored with submission ID prefix
- Consider adding virus scanning in production
- Ensure proper file permissions

### 5. Database Migration

Run the migration to add new columns:
```sql
-- See: backend/migrations/add_document_fields_to_submission.sql
ALTER TABLE submissions ADD COLUMN uploaded_document_path VARCHAR(500);
ALTER TABLE submissions ADD COLUMN uploaded_document_name VARCHAR(255);
ALTER TABLE submissions ADD COLUMN uploaded_document_content TEXT;
```

Or use Alembic:
```bash
cd backend
alembic revision --autogenerate -m "Add document upload fields to submissions"
alembic upgrade head
```

### 6. Environment Setup

Ensure PyPDF2 is installed:
```bash
pip install PyPDF2==3.0.1
```

### 7. Usage Example

**Creating a submission with document:**
```typescript
// 1. Create submission
const submission = await api.post('/submissions', formData);

// 2. Upload document
const fileFormData = new FormData();
fileFormData.append('file', uploadedFile);
await api.post(`/submissions/${submission.id}/upload-document`, fileFormData);

// 3. Navigate to questionnaire
router.push(`/submit/${submission.id}/question/1`);
```

**AI Suggestion with document context:**
```python
# AI service automatically includes document content
result = ai_service.generate_suggestion(
    question_text="What data does your AI system process?",
    question_type="textarea",
    category_name="Data Privacy",
    document_context=submission.uploaded_document_content,
    # ... other params
)
```

### 8. Future Enhancements

- [ ] Support for more file types (DOCX, images with OCR)
- [ ] Document chunking for very large files
- [ ] Document summarization before including in context
- [ ] Multiple document uploads per submission
- [ ] Document preview in UI
- [ ] Automatic question pre-filling option
- [ ] Document version tracking

### 9. Testing

**Manual Testing:**
1. Create a new submission
2. Upload a PDF with project details
3. Navigate through questions
4. Click "AI Suggestion" on various questions
5. Verify AI responses reference the uploaded document

**Test Files:**
- Create a sample project description PDF
- Include details like: project name, data types, third-party services, security measures
- Verify AI extracts and uses this information

### 10. Troubleshooting

**File upload fails:**
- Check file size (< 10MB)
- Verify file type (PDF or TXT)
- Check backend logs for extraction errors
- Ensure `uploads/submissions/` directory exists and is writable

**AI doesn't use document content:**
- Verify document was uploaded successfully
- Check `uploaded_document_content` is populated in database
- Review AI service logs for context inclusion
- Ensure document content is under 4000 characters (truncation)

**PDF extraction issues:**
- Some PDFs may have encoding issues
- Scanned PDFs without OCR won't extract text
- Try converting to text format first
- Check PyPDF2 compatibility with PDF version
</content>