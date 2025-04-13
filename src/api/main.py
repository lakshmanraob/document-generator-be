# src/api/main.py
from fastapi import FastAPI, Response, status
from .endpoints import uploads, generate
import os

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)


app = FastAPI(title="GxP Document Generator API")

app.include_router(uploads.router)
app.include_router(generate.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the GxP Document Generator API"}

# New Health Check Endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """
    Simple health check endpoint. Returns 200 OK if the service is running.
    """
    return {"status": "ok"}

# Optional: If you want to run directly using python src/api/main.py
# You'd typically use uvicorn src.api.main:app --reload
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)