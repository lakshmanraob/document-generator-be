# GxP Document Generator API

This project provides a FastAPI-based API for generating GxP (Good Practice) compliant documentation. It allows users to upload necessary input files (like user stories and database schemas) and then trigger a process to generate the documentation, which can be downloaded.

The application is containerized using Docker for easy setup and deployment.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Docker:** The application runs inside Docker containers. You need Docker Engine installed. Follow the official installation guide for your operating system: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
2.  **Git:** Required for cloning the repository. ([https://git-scm.com/downloads](https://git-scm.com/downloads))
3.  **(Optional) `curl` or Postman:** Useful tools for testing the API endpoints.

## Getting Started

Follow these steps to get the application running locally using Docker.

**1. Clone the Repository:**

```bash
# Replace <your-github-repo-url> with the actual URL of your repository
git clone git@github.com:lakshmanraob/document-generator-be.git
cd gxp-generator-api # Or your repository's directory name
```

**2. Build the Docker Image:**

Navigate to the root directory of the project (where the `Dockerfile` is located) and run the build command:

```bash
docker build -t gxp-generator-api .
```

This command builds the Docker image based on the instructions in the `Dockerfile` and tags it with the name `gxp-generator-api`.

**3. Run the Docker Container:**

Once the image is built, run it as a container:

```bash
docker run -d -p 8000:8000 --name gxp-app gxp-generator-api
```

*   `-d`: Runs the container in detached mode (in the background).
*   `-p 8000:8000`: Maps port 8000 on your host machine to port 8000 inside the container (where the FastAPI application listens).
*   `--name gxp-app`: Assigns a convenient name (`gxp-app`) to the running container.
*   `gxp-generator-api`: Specifies the image to run.

**Note on File Persistence:** The current Docker setup does not persist uploaded files or generated documents between container restarts. For development or persistent storage, consider using Docker Volumes by modifying the `docker run` command:

```bash
# Example using volumes (creates 'uploads' and 'generated_docs' in your current directory if they don't exist)
docker run -d \
  -p 8000:8000 \
  --name gxp-app \
  -v ${PWD}/uploads:/app/uploads \
  -v ${PWD}/generated_docs:/app/generated_docs \
  gxp-generator-api
```

## Verifying the Application

Once the container is running, you can verify the application and its endpoints:

**1. Check Container Status:**

Make sure the container is running:

```bash
docker ps
```

You should see `gxp-app` listed with status "Up".

**2. Check Container Logs (Optional):**

If you suspect issues, check the logs:

```bash
docker logs gxp-app
```

**3. Access API Documentation:**

Open your web browser and navigate to:

`http://localhost:8000/docs`

You should see the FastAPI Swagger UI, which provides interactive documentation for all available endpoints.

**4. Check Health Endpoint:**

Use `curl` or your browser to access the health check endpoint:

```bash
curl http://localhost:8000/health
```

You should receive a JSON response:

```json
{"status":"ok"}
```

**5. Test Endpoints (Example using `curl`):**

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
    Check the contents of `generated_doc.txt`.

You can also use tools like Postman to interact with these endpoints more easily.

## Stopping the Container

To stop the running container:

```bash
docker stop gxp-app
```

To remove the stopped container:

```bash
docker rm gxp-app
```
```

Make sure to replace `<your-github-repo-url>` with the actual URL of your GitHub repository.