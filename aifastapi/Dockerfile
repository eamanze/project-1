FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app
COPY . .

# Run Uvicorn (command overridden in docker-compose)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8010"]
