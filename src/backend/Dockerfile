FROM python:3.12-slim

WORKDIR /app

# Copy requirements from root (assumes build context is project root)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY src/backend/ ./src/backend/

# Set environment variables
ENV PORT=8000
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "src/backend/agent.py"]
