import json
from pathlib import Path
from typing import Any, Dict, List
from fastapi import HTTPException
from .security import validate_path, ensure_data_dir

async def read_file(path: str | Path) -> str:
    """Read file contents safely"""
    path = validate_path(path)
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

async def write_file(path: str | Path, content: str) -> None:
    """Write content to file safely"""
    path = ensure_data_dir(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

async def read_json(path: str | Path) -> Dict[str, Any]:
    """Read and parse JSON file"""
    content = await read_file(path)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON file")

async def write_json(path: str | Path, data: Dict[str, Any]) -> None:
    """Write data as JSON file"""
    try:
        content = json.dumps(data, indent=2)
        await write_file(path, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing JSON: {str(e)}")