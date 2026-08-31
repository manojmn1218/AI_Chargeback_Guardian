"""
AI Chargeback Guardian — Production & Local Server Entry Point

Starts the FastAPI server with embedded static assets from frontend/dist.
Accessible at:
  - Application UI: http://localhost:8000
  - Swagger Docs:   http://localhost:8000/docs
  - Health Check:   http://localhost:8000/health
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

import uvicorn
from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 70)
    print(f"AI CHARGEBACK GUARDIAN — ACTIVE ON http://localhost:{port}")
    print(f"  * Interactive Frontend: http://localhost:{port}/")
    print(f"  * Swagger API Docs:     http://localhost:{port}/docs")
    print(f"  * System Health:        http://localhost:{port}/health")
    print("=" * 70)
    uvicorn.run(app, host=host, port=port, log_level="info")
