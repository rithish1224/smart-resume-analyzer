from fastapi import UploadFile
import os
import re
import unicodedata

MAX_FILE_SIZE_MB = 1
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".jpg", ".jpeg", ".png"}

async def validate_file(file: UploadFile) -> None:
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File extension {ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Check size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0) # Reset pointer
    
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size exceeds limit of {MAX_FILE_SIZE_MB} MB")

def sanitize_filename(filename: str) -> str:
    # Remove path traversal characters
    filename = os.path.basename(filename)
    # Slugify
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\s.-]', '', filename).strip().lower()
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename

def is_safe_path(base_dir: str, target_path: str) -> bool:
    # Prevent directory traversal
    try:
        base_dir_resolved = os.path.realpath(base_dir)
        target_path_resolved = os.path.realpath(target_path)
        return os.path.commonpath([base_dir_resolved, target_path_resolved]) == base_dir_resolved
    except Exception:
        return False
