from pathlib import Path
from fastapi import HTTPException
from ..config import ALLOWED_DIRS, DATA_DIR

def validate_path(path: str | Path) -> Path:
    """Validate and sanitize file path"""
    try:
        path = Path(path).resolve()
        
        # Check if path is within allowed directories
        if not any(allowed_dir in path.parents for allowed_dir in ALLOWED_DIRS):
            raise HTTPException(status_code=400, detail="Access denied: Path outside allowed directories")
            
        # Check for path traversal attempts
        if '..' in str(path):
            raise HTTPException(status_code=400, detail="Access denied: Invalid path")
            
        return path
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}")

def ensure_data_dir(path: str | Path) -> Path:
    """Ensure path is within /data directory"""
    path = Path(path)
    if not str(path).startswith(str(DATA_DIR)):
        path = DATA_DIR / path
    return validate_path(path)