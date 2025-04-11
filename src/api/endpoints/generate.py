# src/api/endpoints/generate.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

# Import your generator class
# Assuming it's adaptable or we adapt the call here
from src.gxp_doc_generator_gemini import GxPDocumentGenerator

# Import the shared state (simple dictionary)
from .uploads import uploaded_files

router = APIRouter()
OUTPUT_DIR = Path("output/generated_docs") # Directory to store generated docs
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.get("/generate", tags=["Generation"], response_class=FileResponse)
async def generate_gxp_document():
    """
    Triggers the GxP document generation process using the previously
    uploaded files and returns the generated document for download.
    """
    user_stories_path = uploaded_files.get("user_stories")
    db_schema_path = uploaded_files.get("db_schema")

    if not user_stories_path or not db_schema_path:
        raise HTTPException(status_code=400, detail="User stories or database schema file not uploaded yet.")

    if not os.path.exists(user_stories_path) or not os.path.exists(db_schema_path):
         raise HTTPException(status_code=404, detail="Uploaded file(s) not found on server.")

    try:
        # Adapt this instantiation/call based on how your GxPDocumentGenerator
        # actually takes input (e.g., file paths, config objects)
        # Option 1: Generator reads from known paths (like 'uploads/') implicitly
        # generator = GxPDocumentGenerator()
        # Option 2: Pass paths to the generator (requires modification)
        # generator = GxPDocumentGenerator(user_stories_path=user_stories_path, db_schema_path=db_schema_path)

        # For now, let's assume the generator works like in main_check.py
        # and we might need to adjust GxPDocumentGenerator or how it finds files.
        # Let's stick to the original simple call for now.
        generator = GxPDocumentGenerator()

        # Assume generate() saves the file and returns its path
        # We might need to modify generate() to save to OUTPUT_DIR
        # and return the full path.
        # Let's assume it returns a path relative to the project root for now.
        # Example: output_file = "generated_gxp_doc.txt"
        output_file_rel_path = generator.generate()

        # Ensure the output file exists
        if not os.path.exists(output_file_rel_path):
             raise HTTPException(status_code=500, detail=f"Generator failed to produce output file at: {output_file_rel_path}")

        # Provide the file for download
        # FileResponse needs the absolute path or path relative to where uvicorn is run
        return FileResponse(
            path=output_file_rel_path,
            filename=os.path.basename(output_file_rel_path), # Suggests a filename to the browser
            media_type='text/plain' # Adjust if it's not a plain text file
        )

    except Exception as e:
        # Log the exception for debugging
        print(f"Error during generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating GxP document: {str(e)}")