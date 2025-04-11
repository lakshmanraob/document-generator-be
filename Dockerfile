# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for certain libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container at /app
# Copy the entire src directory
COPY ./src ./src
# Create necessary directories if they don't exist in the image
# Although the API creates them, it's good practice for permissions etc.
RUN mkdir -p uploads generated_docs

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run your app using uvicorn
# Ensure it listens on 0.0.0.0 to be accessible from outside the container
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]