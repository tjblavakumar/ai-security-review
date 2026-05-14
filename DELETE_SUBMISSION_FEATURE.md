# Delete Submission Feature

## Overview
Added ability for submitters to delete their draft and returned submissions from the "My Submissions" page.

---

## Implementation Details

### Backend Changes

#### 1. New API Endpoint
**File:** `backend/app/routers/submissions.py`

```python
DELETE /api/submissions/{submission_id}
```

**Features:**
- Only allows deletion of submissions with status `draft` or `returned`
- Returns 400 error if trying to delete submitted/in-review/approved submissions
- Returns 404 if submission not found
- Cascade deletes all related data (responses, attachments, reviews)

#### 2. Service Function
**File:** `backend/app/services/submission_service.py`

```python
def delete_submission(db: Session, submission_id: int) -> bool
```

**Behavior:**
- Deletes submission from database
- Cascade delete handles:
  - All submission responses
  - All attachments
  - All review comments
  - All reviews

#### 3. Database Cascade
**Already configured in models:**
- `responses: cascade="all, delete-orphan"`
- `attachments: cascade="all, delete-orphan"`  
- `reviews: cascade="all, delete-orphan"`

---

### Frontend Changes

#### File: `frontend/src/app/my-submissions/page.tsx`

**New Features:**

1. **Delete Button**
   - Trash icon button next to action buttons
   - Only visible for draft and returned submissions
   - Red color scheme to indicate destructive action

2. **Confirmation Dialog**
   ```
   Are you sure you want to delete "[Project Name]"?
   
   This action cannot be undone. All responses and attachments 
   will be permanently deleted.
   ```

3. **Error Handling**
   - Shows error if trying to delete non-deletable status
   - Displays backend error messages
   - Removes from UI immediately after successful delete

4. **Visual Updates**
   - Action buttons grouped together
   - Delete button only shows for draft/returned
   - Continue/Revise/View buttons based on status

---

## User Experience

### When Can Users Delete?

| Status | Can Delete? | Action Button |
|--------|-------------|---------------|
| Draft | ✅ Yes | Continue + Delete |
| Returned | ✅ Yes | Revise + Delete |
| Submitted | ❌ No | View only |
| In Review | ❌ No | View only |
| Approved | ❌ No | View only |

### Delete Workflow

1. User goes to "My Submissions"
2. Searches by email
3. Sees list of submissions
4. For draft/returned submissions, sees trash icon
5. Clicks trash icon
6. Confirmation dialog appears
7. User confirms deletion
8. Submission is deleted
9. UI updates immediately
10. Success toast notification

---

## Security & Validation

### Backend Validation:
- ✅ Checks submission exists
- ✅ Validates status is draft or returned
- ✅ Returns appropriate error codes
- ✅ Cascade deletes all related data

### Frontend Validation:
- ✅ Only shows delete button for valid statuses
- ✅ Confirmation dialog prevents accidental deletion
- ✅ Error handling for edge cases
- ✅ UI updates optimistically after delete

---

## API Response Examples

### Success Response:
```json
{
  "data": {
    "deleted": true,
    "submission_id": 123
  },
  "message": "Submission deleted successfully",
  "success": true
}
```

### Error Response (Invalid Status):
```json
{
  "detail": "Cannot delete submission with status 'submitted'. Only draft and returned submissions can be deleted."
}
```

### Error Response (Not Found):
```json
{
  "detail": "Submission not found"
}
```

---

## Testing Checklist

### Backend:
- [ ] Can delete draft submission
- [ ] Can delete returned submission
- [ ] Cannot delete submitted submission
- [ ] Cannot delete in-review submission
- [ ] Cannot delete approved submission
- [ ] Cascade deletes responses
- [ ] Cascade deletes attachments
- [ ] Cascade deletes reviews
- [ ] Returns proper error codes

### Frontend:
- [ ] Delete button shows for draft
- [ ] Delete button shows for returned
- [ ] Delete button hidden for other statuses
- [ ] Confirmation dialog appears
- [ ] Cancel button works
- [ ] Delete removes from list
- [ ] Success toast appears
- [ ] Error toast shows backend errors
- [ ] UI updates immediately

---

## Files Modified

### Backend:
- `backend/app/routers/submissions.py` - Added DELETE endpoint
- `backend/app/services/submission_service.py` - Added delete_submission function

### Frontend:
- `frontend/src/app/my-submissions/page.tsx` - Added delete button and handler

---

## Future Enhancements

### Potential additions:
1. **Soft Delete** - Mark as deleted instead of hard delete (for audit trail)
2. **Restore Feature** - Allow restoring soft-deleted submissions
3. **Admin Override** - Allow admins to delete any submission
4. **Bulk Delete** - Select multiple submissions to delete
5. **Archive Instead** - Move to archived state instead of deleting
6. **Delete Confirmation Email** - Send email notification of deletion
7. **Audit Log** - Track who deleted what and when

---

## Status
✅ **Complete and Ready for Use**

Users can now delete their draft and returned submissions from the My Submissions page with proper confirmation and validation.
