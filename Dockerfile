# Use a slim Python base image suitable for production deployments
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory inside the container
WORKDIR /app

# Install Python dependencies first to leverage Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy static assets explicitly so tutorial videos are bundled in the image
COPY static/ ./static/

# Copy the rest of the application source code
COPY . .

# Configure the default port used by Google Cloud Run and other GCP services
EXPOSE 8080
ENV PORT=8080

# Use Gunicorn as the production WSGI server
CMD ["python", "app.py"]