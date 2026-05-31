# ========== BUILD FRONTEND ==========
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ========== BACKEND ==========
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MONGODB_URI="mongodb://localhost:27017/sistema_ventas"

# Backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code
COPY backend/ .

# Frontend static
COPY --from=frontend-builder /app/build /app/static

# Debug: verify imports
RUN python -c "from fastapi import FastAPI; print('FastAPI OK')" && \
    python -c "import motor.motor_asyncio; print('Motor OK')" && \
    python -c "from pydantic import BaseModel; print('Pydantic OK')" && \
    python -c "from bson import ObjectId; print('BSON OK')" && \
    python -c "import uvicorn; print('Uvicorn OK')" && \
    python -c "import app.main; print(f'App imports: OK')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
