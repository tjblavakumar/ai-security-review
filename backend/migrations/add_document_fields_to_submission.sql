-- Migration: Add document upload fields to submissions table
-- Date: 2024

-- Add columns for document upload
ALTER TABLE submissions ADD COLUMN uploaded_document_path VARCHAR(500);
ALTER TABLE submissions ADD COLUMN uploaded_document_name VARCHAR(255);
ALTER TABLE submissions ADD COLUMN uploaded_document_content TEXT;

-- Create uploads directory structure (handled by application code)
-- uploads/submissions/
</content>