# src/api/endpoints/uploads.py
from fastapi import APIRouter, File, UploadFile, HTTPException
import aiofiles
import os
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("output")

# In-memory storage for uploaded file paths (simple example)
# For production, consider a more robust way (e.g., database, cache)
uploaded_files = {
    "user_stories": None,
    "db_schema": None
}

@router.post("/upload/userstories", tags=["Uploads"])
async def upload_user_stories(file: UploadFile = File(...)):
    """
    Uploads the user stories file.
    """
    file_path = UPLOAD_DIR / f"user_stories_{file.filename}"
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        uploaded_files["user_stories"] = str(file_path) # Store the path
        return {"filename": file.filename, "content_type": file.content_type, "path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save user stories file: {e}")
    finally:
        await file.close()


@router.post("/upload/databaseschema", tags=["Uploads"])
async def upload_database_schema(file: UploadFile = File(...)):
    """
    Uploads the database schema file.
    """
    file_path = UPLOAD_DIR / f"db_schema_{file.filename}"
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        uploaded_files["db_schema"] = str(file_path) # Store the path
        return {"filename": file.filename, "content_type": file.content_type, "path": str(file_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save database schema file: {e}")
    finally:
        await file.close()