# AI Chargeback Guardian — Deployment Guide

This document outlines local development execution, production build procedures, environment configuration, and container deployment options for **AI Chargeback Guardian**.

---

## 1. Environment Configuration

Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

### Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Environment mode (`development`, `production`, `test`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DATABASE_URL` | `sqlite:///./backend/chargeback_guardian.db` | SQLAlchemy database connection URI |
| `LLM_PROVIDER` | `demo` | Generative provider (`demo`, `openai`, `anthropic`) |
| `LLM_API_KEY` | *(empty)* | Optional API key for external LLM generation |
| `LLM_MODEL` | *(empty)* | Model identifier (e.g. `gpt-4o`, `claude-3-5-sonnet`) |
| `BACKEND_HOST` | `0.0.0.0` | Binding host address |
| `BACKEND_PORT` | `8000` | Binding port for FastAPI server |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend backend API URL |

---

## 2. Local Development Execution

### Backend Server
```bash
# Activate virtual environment
source backend/venv/bin/activate  # On Linux/macOS
backend\venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Seed synthetic SQLite database
python scripts/seed_demo.py

# Start FastAPI backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at: `http://localhost:8000/docs`

### Frontend Dev Server
```bash
cd frontend
npm install
npm run dev
```
Interactive UI will be available at: `http://localhost:5173`

---

## 3. Production Build & Execution

### 1. Build Frontend Static Bundle
```bash
cd frontend
npm run build
```
This outputs optimized, minified production assets into `frontend/dist/`.

### 2. Run Production Backend with Multi-Worker Uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
```

---

## 4. Docker Deployment (Optional)

### `Dockerfile.backend`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python scripts/seed_demo.py
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### `Dockerfile.frontend`
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 5. Health Checks & Verification

Verify system readiness using the health check endpoint:
```bash
curl http://localhost:8000/health
```
Expected output:
```json
{"status":"healthy","app_name":"AI Chargeback Guardian","version":"0.1.0"}
```
