# GxP Document Generator API

This project provides a FastAPI-based API for generating GxP (Good Practice) compliant documentation. It allows users to upload necessary input files (like user stories and database schemas) and then trigger a process to generate the documentation, which can be downloaded.

The application can be run using Docker (recommended for easy setup and deployment consistency) or directly on your local machine using Python.

## Prerequisites

### Common:
1.  **Git:** Required for cloning the repository. ([https://git-scm.com/downloads](https://git-scm.com/downloads))
2.  **Google API Key:** You need a Google API key with the Gemini API enabled. This should be stored in a `.env` file (see setup steps).
3.  **(Optional) `curl` or Postman:** Useful tools for testing the API endpoints.

### For Docker Setup:
1.  **Docker:** Docker Engine installed. Follow the official installation guide for your operating system: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

### For Local Setup (Without Docker):
1.  **Python:** Version 3.10 or later recommended (check compatibility with `requirements.txt`). Download from [python.org](https://www.python.org/).
2.  **Pip:** Python's package installer (usually included with Python).

## Getting Started - Running with Docker (Recommended)

Follow these steps to get the application running locally using Docker.

**1. Clone the Repository:**

```bash
# Replace with your repository URL if different
git clone git@github.com:lakshmanraob/document-generator-be.git
cd document-generator-be # Or your repository's directory name
```

**2. Create `.env` File:**

Create a file named `.env` in the project root and add your Google API key:
```.env
GOOGLE_API_KEY=your_actual_api_key_here
```
*(Ensure `.env` is in your `.gitignore`)*

**3. Create `prompt/system.txt` File:**

Ensure the `prompt` directory exists and create a `system.txt` file inside it with your desired Gemini system prompt.

```bash
mkdir -p prompt
# Add your system prompt content to prompt/system.txt
echo "You are an assistant helping generate GxP documentation." > prompt/system.txt
```

**4. Build the Docker Image:**

Navigate to the root directory of the project (where the `Dockerfile` is located) and run the build command:

```bash
docker build -t gxp-generator-api .
```

This command builds the Docker image based on the instructions in the `Dockerfile` and tags it with the name `gxp-generator-api`.

**5. Run the Docker Container:**

Once the image is built, run it as a container:

```bash
# Basic run
docker run -d -p 8000:8000 --name gxp-app --env-file .env gxp-generator-api

# Run with volume mapping for uploads/outputs persistence
# docker run -d \
#   -p 8000:8000 \
#   --name gxp-app \
#   --env-file .env \
#   -v ${PWD}/uploads:/app/uploads \
#   -v ${PWD}/output:/app/output \
#   -v ${PWD}/prompt:/app/prompt \
#   gxp-generator-api
```

*   `-d`: Runs the container in detached mode.
*   `-p 8000:8000`: Maps host port 8000 to container port 8000.
*   `--name gxp-app`: Assigns a name to the container.
*   `--env-file .env`: Loads environment variables from the `.env` file.
*   `-v ...` (Optional): Maps local directories (uploads, output, prompt) into the container for persistence and easier access.
*   `gxp-generator-api`: Specifies the image to run.

## Getting Started - Running Locally (Without Docker)

Follow these steps to run the application directly on your local machine.

**1. Clone the Repository (if not already done):**

```bash
# Replace with your repository URL if different
git clone git@github.com:lakshmanraob/document-generator-be.git
cd document-generator-be # Or your repository's directory name
```

**2. Create and Activate Virtual Environment:**

It's highly recommended to use a virtual environment.

```bash
# Create the virtual environment (named 'venv')
python -m venv venv

# Activate the virtual environment:
# On Windows (cmd.exe/powershell):
.\venv\Scripts\activate
# On macOS/Linux (bash/zsh):
source venv/bin/activate
```
*(Your terminal prompt should now show `(venv)`)*

**3. Install Dependencies:**

Install the required Python packages.

```bash
pip install -r requirements.txt
```

**4. Create `.env` File:**

Create a file named `.env` in the project root and add your Google API key:
```.env
GOOGLE_API_KEY=your_actual_api_key_here
```
*(Ensure `.env` is in your `.gitignore`)*

**5. Create `prompt/system.txt` File:**

Ensure the `prompt` directory exists and create a `system.txt` file inside it with your desired Gemini system prompt.

```bash
mkdir -p prompt
# Add your system prompt content to prompt/system.txt
echo "You are an assistant helping generate GxP documentation." > prompt/system.txt
```

**6. Run the FastAPI Application:**

Start the Uvicorn server from the project root directory.

```bash
uvicorn src.api.main:app --reload --port 8000
```

*   `src.api.main:app`: Path to the FastAPI app instance.
*   `--reload`: Enables auto-reload on code changes (useful for development).
*   `--port 8000`: Port to run the server on.

## Verifying the Application (Both Setups)

Once the application is running (either via Docker or locally), you can verify it:

**1. Check Server Status:**
*   **Docker:** `docker ps` (check if `gxp-app` is running). `docker logs gxp-app` (check for errors).
*   **Local:** Check the terminal where you ran `uvicorn` for startup messages and errors.

**2. Access API Documentation:**
Open your web browser and navigate to: `http://localhost:8000/docs`
You should see the FastAPI Swagger UI.

**3. Check Health Endpoint:**
Use `curl` or your browser: `http://localhost:8000/health`
Expected JSON response: `{"status":"ok"}`

**4. Test Endpoints (Example using `curl`):**

*   **Upload User Stories:**
    ```bash
    # Create a dummy user_stories.txt file first
    echo "This is a user story." > user_stories.txt
    curl -X POST -F "file=@user_stories.txt" http://localhost:8000/upload/userstories
    ```

*   **Upload Database Schema:**
    ```bash
    # Create a dummy db_schema.sql file first
    echo "CREATE TABLE example (id INT);" > db_schema.sql
    curl -X POST -F "file=@db_schema.sql" http://localhost:8000/upload/databaseschema
    ```

*   **Generate Document (Download):**
    ```bash
    # This will attempt to generate and download the file (e.g., to generated_doc.txt)
    # Note: Actual filename depends on what your generator produces
    curl -X GET http://localhost:8000/generate -o generated_doc.txt
    ```
    Check the contents of `generated_doc.txt` in your current directory. Files uploaded/generated will be in the `uploads/` and `output/` directories within the project root (or mapped volumes if using Docker volumes).

## Stopping the Application

*   **Docker:**
    ```bash
    docker stop gxp-app
    docker rm gxp-app # Optional: Remove the stopped container
    ```
*   **Local:**
    Press `Ctrl+C` in the terminal where `uvicorn` is running. If you used a virtual environment, you can deactivate it with the command `deactivate`.