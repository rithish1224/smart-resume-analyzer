from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
import os
import uuid
from backend.utils.security import sanitize_filename, validate_file

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadResponse(BaseModel):
    file_id: str
    original_filename: str
    content_type: str
    size_bytes: int
    parse_ready: bool
    hint: str

@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate file format and size
    try:
        await validate_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Generate unique ID and save
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(safe_filename)[1]
    saved_filename = f"{file_id}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    try:
        file.file.seek(0)
        content = file.file.read()
        size_bytes = len(content)
        with open(saved_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return UploadResponse(
        file_id=file_id,
        original_filename=safe_filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        parse_ready=True,
        hint="Upload PDF, DOCX, TXT, JPG, JPEG, or PNG files. Keep files under 1 MB for best results."
    )
