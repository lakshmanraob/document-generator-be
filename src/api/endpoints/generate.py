# src/api/endpoints/generate.py
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import os
from pathlib import Path
import traceback # Import for detailed error logging
import asyncio

# Import your generator class
from src.gxp_doc_generator_gemini import GxPDocumentGenerator

# Import the shared state (simple dictionary) and upload directory
from .uploads import uploaded_files, UPLOAD_DIR

router = APIRouter()
# Output directory is handled within the generator class ('output/')

@router.get(
    "/generate",
    tags=["Generation"],
    response_class=FileResponse,
    summary="Generate GxP Document",
    description="Triggers the GxP document generation using previously uploaded user stories and DB schema. Returns the generated document as a downloadable file.",
    responses={
        200: {
            "description": "GxP document generated successfully.",
            "content": {
                "text/plain": {
                    "schema": {
                        "type": "string",
                        "format": "binary"
                    }
                }
                # Add 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' if supporting DOCX
            }
        },
        400: {"description": "Input file(s) not uploaded yet."},
        404: {"description": "Uploaded file(s) not found on server."},
        500: {"description": "Internal server error during generation."},
    }
)
async def generate_gxp_document():
    """
    Triggers the GxP document generation process using the previously
    uploaded files and returns the generated document for download.

    Requires prior successful calls to `/output/userstories` and `/output/databaseschema`.
    """
    user_stories_path_str = uploaded_files.get("user_stories")
    db_schema_path_str = uploaded_files.get("db_schema")

    # Check if paths were stored after upload
    if not user_stories_path_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User stories file has not been uploaded via /output/userstories."
        )
    if not db_schema_path_str:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database schema file has not been uploaded via /output/databaseschema."
        )

    # Convert to Path objects for checking existence
    user_stories_path = Path(user_stories_path_str)
    db_schema_path = Path(db_schema_path_str)

    # Check if the files actually exist at the stored paths
    if not user_stories_path.exists():
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uploaded user stories file not found on server at path: {user_stories_path_str}"
         )
    if not db_schema_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Uploaded database schema file not found on server at path: {db_schema_path_str}"
        )

    try:
        print(f"Starting GxP document generation process...")
        print(f"Using User Stories: {user_stories_path}")
        print(f"Using DB Schema: {db_schema_path}")

        # Instantiate the generator, passing the file paths
        generator = GxPDocumentGenerator(
            user_stories_path=user_stories_path, # Pass Path objects or strings
            db_schema_path=db_schema_path
        )

        # Call the generate method - it handles loading, API call, parsing, saving
        # It returns the Path object to the generated file (e.g., output/GxP_Documentation_....txt)
        output_file_path = await asyncio.to_thread(generator.generate) # Run synchronous generator code in a thread

        # Ensure the generate method returned a path and the file exists
        if not output_file_path or not output_file_path.exists():
             print(f"Generator finished but output file is missing at expected path: {output_file_path}")
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Document generator failed to produce the output file."
            )

        print(f"Generation successful. Preparing file for download: {output_file_path}")
        # Provide the generated file for download
        return FileResponse(
            path=str(output_file_path), # Convert Path object to string for FileResponse
            filename=output_file_path.name, # Get filename from Path object
            media_type='text/plain' # Media type for TXT file
            # Use 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' for docx
        )

    except FileNotFoundError as e:
         # Specific handling for file missing errors during generator execution
         print(f"Generation failed due to missing file inside generator: {e}")
         traceback.print_exc() # Log traceback for debugging
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: Required file missing during generation ({e}). Please check server logs."
         )
    except ValueError as e:
         # Handle known value errors from the generator
         print(f"Generation failed due to invalid input or configuration: {e}")
         traceback.print_exc()
         raise HTTPException(
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=f"Internal server error: {e}. Please check server logs."
         )
    except Exception as e:
        # Catch-all for other errors during generation
        print(f"Unexpected error during generation endpoint execution: {str(e)}")
        traceback.print_exc() # Log traceback for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal server error occurred while generating the document: {str(e)}. Please check server logs."
        )