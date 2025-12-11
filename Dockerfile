# Stage 1: Build Stage - Install dependencies

# Use a stable, slim Python image as the base for smaller size
FROM python:3.11-slim AS builder

# Set environment variables to optimize Python performance inside the container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory for the application
WORKDIR /app

# Install system dependencies needed by some Python libraries (like PyPDF2/unstructured)
# and for installing packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size by not storing installation artifacts
RUN pip install --no-cache-dir -r requirements.txt

# ---
# Stage 2: Runner Stage - Final minimal image for running the app
# ---

# Use a minimal Python runtime image
FROM python:3.11-slim AS runner

# Set the working directory
WORKDIR /app

# Ensure NLTK data is available if used for preprocessing/validation
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files and the data structure
# NOTE: We copy the raw data and vectorstore directories as well.
# Best practice is to use Docker Volumes for 'data/vectorstore' in production,
# but copying here ensures the app runs out-of-the-box.
COPY . /app

# --- Data Ingestion/Preparation Step ---
# This is a critical step: If the vector store doesn't exist, it needs to be created.
# This script (data_processor.py) will populate the data/vectorstore/ directory.
# We run it only once during the image build/initial run.
RUN python src/data_processor.py

# --- Environment Configuration ---

# Expose the default port for Streamlit
EXPOSE 8501

# Set the default entry point to run the Streamlit app
CMD ["streamlit", "run", "app/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
