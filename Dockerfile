# 1. Base Image: Use the full version to solve OS dependency conflicts
FROM python:3.10

# 2. Set Environment Variables
ENV PYTHONUNBUFFERED 1
ENV PATH="/usr/src/app/.local/bin:$PATH"

# 3. Set Working Directory
WORKDIR /usr/src/app

# 4. Copy requirements
COPY requirements.txt ./

# 5. Install Dependencies (Combined step for stability)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 6. Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# 7. Copy the rest of the application code
COPY . .

# 8. Command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port", "10000", "--server.address", "0.0.0.0"]
