# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies, with special handling for PyMuPDF
RUN pip install --no-cache-dir --only-binary :all: PyMuPDF && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]