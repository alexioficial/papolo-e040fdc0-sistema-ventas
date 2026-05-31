FROM python:3.12-slim

WORKDIR /app

# Instalar Node.js para build del frontend
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY backend/ .

# Build frontend
COPY frontend/ /app/frontend/
RUN cd /app/frontend && npm install && npm run build && \
    rm -rf ../static && cp -r build ../static && \
    rm -rf /app/frontend

# Run
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
