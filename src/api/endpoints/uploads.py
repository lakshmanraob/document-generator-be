# src/api/endpoints/uploads.py
from fastapi import APIRouter, File, UploadFile, HTTPException, status
import aiofiles
import os
from pathlib import Path
import shutil # For potentially moving files if needed
import logging # Use standard logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Define UPLOAD_DIR relative to the project root (where main.py/Docker runs)
UPLOAD_DIR = Path("output")
# Ensure the directory exists (main.py also does this, but doesn't hurt here)
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError as e:
    logger.error(f"Could not create upload directory {UPLOAD_DIR}: {e}")
    # Depending on severity, you might want to prevent the app from starting

# In-memory storage for uploaded file paths (simple example).
# WARNING: Not suitable for production! Lost on restart, not scalable.
# Consider using Redis, a database, or returning IDs mapping to cloud storage.
uploaded_files = {
    "user_stories": None,
    "db_schema": None
}

@router.post(
    "/upload/userstories",
    tags=["Uploads"],
    summary="Upload User Stories File",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "File uploaded successfully"},
        400: {"description": "No file provided"},
        500: {"description": "Could not save file"}
    }
)
async def upload_user_stories(file: UploadFile = File(..., description="The user stories file (e.g., .txt)")):
    """
    Uploads the user stories file. Replaces any previously uploaded user stories file.
    """
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No upload file sent.")

    # Define save path. Using a fixed name overwrites previous uploads.
    # Alternatively, generate unique names if history is needed.
    # filename = f"user_stories_{file.filename}" # Keep original filename part
    filename = "uploaded_user_stories.txt" # Fixed name for simplicity
    file_path = UPLOAD_DIR / filename

    try:
        logger.info(f"Attempting to save user stories file '{file.filename}' to: {file_path}")
        # Use a temporary file path during write for atomicity? (More complex)
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # Read file in chunks (e.g., 1MB)
                await out_file.write(content)

        # Store the absolute or relative path (relative to project root works well here)
        # Storing the string representation of the Path object.
        uploaded_files["user_stories"] = str(file_path.resolve()) # Store absolute path
        logger.info(f"User stories file '{file.filename}' saved successfully. Path stored: {uploaded_files['user_stories']}")
        return {
            "message": "User stories file uploaded successfully.",
            "filename": file.filename,
            "content_type": file.content_type,
            "saved_path": str(file_path) # Return relative path for info
        }
    except Exception as e:
        logger.error(f"Error saving user stories file '{file.filename}' to {file_path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save user stories file on the server: {e}"
        )
    finally:
        # Ensure file handle is closed if an error occurs during read/write
        # (aiofiles context manager handles this)
        await file.close()


@router.post(
    "/upload/databaseschema",
    tags=["Uploads"],
    summary="Upload Database Schema File",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "File uploaded successfully"},
        400: {"description": "No file provided"},
        500: {"description": "Could not save file"}
    }
)
async def upload_database_schema(file: UploadFile = File(..., description="The database schema file (e.g., .sql, .txt)")):
    """
    Uploads the database schema file. Replaces any previously uploaded schema file.
    """
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No upload file sent.")

    # Fixed name for simplicity, overwrites previous upload
    filename = "uploaded_db_schema.sql"
    file_path = UPLOAD_DIR / filename

    try:
        logger.info(f"Attempting to save DB schema file '{file.filename}' to: {file_path}")
        async with aiofiles.open(file_path, 'wb') as out_file:
             while content := await file.read(1024 * 1024): # Read in chunks
                await out_file.write(content)

        # Store the path (absolute recommended for clarity if paths are passed around)
        uploaded_files["db_schema"] = str(file_path.resolve()) # Store absolute path
        logger.info(f"DB schema file '{file.filename}' saved successfully. Path stored: {uploaded_files['db_schema']}")
        return {
            "message": "Database schema file uploaded successfully.",
            "filename": file.filename,
            "content_type": file.content_type,
            "saved_path": str(file_path) # Return relative path for info
        }
    except Exception as e:
        logger.error(f"Error saving database schema file '{file.filename}' to {file_path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save database schema file on the server: {e}"
        )
    finally:
        await file.close()
