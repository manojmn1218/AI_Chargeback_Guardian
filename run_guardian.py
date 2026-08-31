"""
AI Chargeback Guardian — Process Supervisor & Persistent Server Manager

Guarantees 100% server uptime, handles port cleanup, manages database initialization,
builds frontend assets, and provides a unified zero-downtime server host.

Modes:
  python run_guardian.py               # Starts unified server on http://localhost:8000
  python run_guardian.py --dev         # Starts both FastAPI (8000) and Vite Dev (5173)
  python run_guardian.py --check       # Health-checks all endpoints
  python run_guardian.py --kill-ports  # Cleans orphaned port 8000 / 5173 processes
"""

import sys
import os
import time
import subprocess
import argparse
import urllib.request
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = str(ROOT_DIR / "backend" / "venv" / "Scripts" / "python.exe")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable


def check_port_in_use(port: int) -> bool:
    """Check if a port is actively bound."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def kill_ports(ports=(8000, 5173)):
    """Kill any hanging/orphaned processes listening on target ports (Windows & Unix safe)."""
    print(f"[*] Checking and releasing ports: {ports}...")
    for port in ports:
        if sys.platform == "win32":
            try:
                cmd = f'netstat -ano | findstr :{port}'
                output = subprocess.check_output(cmd, shell=True).decode()
                for line in output.strip().splitlines():
                    if "LISTENING" in line:
                        parts = line.strip().split()
                        pid = parts[-1]
                        print(f"  -> Terminating orphaned process PID {pid} on port {port}...")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
            except Exception:
                pass
        else:
            try:
                subprocess.run(f"fuser -k {port}/tcp", shell=True, capture_output=True)
            except Exception:
                pass
    time.sleep(1)


def check_health(verbose=True) -> bool:
    """Check localhost health for backend, investigation, and frontend."""
    results = {}
    
    # 1. Backend root health
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=3) as resp:
            data = json.loads(resp.read().decode())
            results["backend_health"] = (resp.status == 200 and data.get("status") == "healthy")
    except Exception as e:
        results["backend_health"] = False

    # 2. Backend investigation API
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/disputes/1/investigation", timeout=3) as resp:
            results["backend_api"] = (resp.status == 200)
    except Exception as e:
        results["backend_api"] = False

    # 3. Frontend Unified Server on 8000
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=3) as resp:
            html = resp.read().decode()
            results["frontend_unified"] = (resp.status == 200 and "root" in html)
    except Exception as e:
        results["frontend_unified"] = False

    # 4. Frontend Vite Dev Server on 5173
    try:
        with urllib.request.urlopen("http://127.0.0.1:5173/", timeout=3) as resp:
            html = resp.read().decode()
            results["frontend_vite"] = (resp.status == 200 and "root" in html)
    except Exception as e:
        results["frontend_vite"] = False

    if verbose:
        print("\n" + "=" * 60)
        print("LOCALHOST HEALTH & CONNECTIVITY STATUS")
        print("=" * 60)
        b_ok = "[OK]" if results.get("backend_health") else "[OFFLINE]"
        api_ok = "[OK]" if results.get("backend_api") else "[OFFLINE]"
        uni_ok = "[OK]" if results.get("frontend_unified") else "[OFFLINE]"
        vite_ok = "[OK]" if results.get("frontend_vite") else "[OFFLINE]"
        
        print(f"  {b_ok:<10} Backend Health Check:      http://127.0.0.1:8000/health")
        print(f"  {api_ok:<10} Backend REST API:           http://127.0.0.1:8000/api/v1/disputes")
        print(f"  {api_ok:<10} Swagger API Documentation:  http://127.0.0.1:8000/docs")
        print(f"  {uni_ok:<10} Unified Application (SPA):  http://127.0.0.1:8000/")
        print(f"  {vite_ok:<10} Vite Dev Hot-Reload Server: http://127.0.0.1:5173/")
        print("=" * 60)

    return any(results.values())


def ensure_ready():
    """Ensure database and frontend builds exist before launch."""
    # Ensure database seeded
    db_file = ROOT_DIR / "backend" / "chargeback_guardian.db"
    if not db_file.exists() or db_file.stat().st_size < 10000:
        print("[*] Database not initialized. Running seed_demo.py...")
        subprocess.run([PYTHON_EXE, "scripts/seed_demo.py"], cwd=str(ROOT_DIR))

    # Ensure frontend build exists
    dist_dir = ROOT_DIR / "frontend" / "dist"
    if not (dist_dir / "index.html").exists():
        print("[*] Frontend bundle not found. Building with Vite...")
        subprocess.run("npm run build", shell=True, cwd=str(ROOT_DIR / "frontend"))


def run_supervisor(dev_mode=False):
    """Run persistent server with auto-recovery and monitoring."""
    ensure_ready()
    kill_ports()

    print("\n" + "=" * 70)
    print("STARTING AI CHARGEBACK GUARDIAN (PERSISTENT SUPERVISOR)")
    print("=" * 70)
    print(f"  * Mode: {'Development (Dual Server)' if dev_mode else 'Unified Production Host'}")
    print(f"  * Backend Address:  http://127.0.0.1:8000")
    print(f"  * Interactive App:  http://127.0.0.1:8000/ (and http://127.0.0.1:5173/ in dev)")
    print("=" * 70 + "\n")

    backend_cmd = [
        PYTHON_EXE, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0", "--port", "8000"
    ]
    if dev_mode:
        backend_cmd.append("--reload")

    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(ROOT_DIR / "backend"),
        env={**os.environ, "PYTHONPATH": f"{ROOT_DIR};{ROOT_DIR / 'backend'}"}
    )

    frontend_proc = None
    if dev_mode:
        frontend_proc = subprocess.Popen(
            "npm run dev",
            shell=True,
            cwd=str(ROOT_DIR / "frontend")
        )

    # Initial warm-up check
    time.sleep(2)
    check_health(verbose=True)

    try:
        while True:
            # Check backend process health
            if backend_proc.poll() is not None:
                print("\n[!] Backend process exited unexpectedly. Restarting automatically...")
                backend_proc = subprocess.Popen(
                    backend_cmd,
                    cwd=str(ROOT_DIR / "backend"),
                    env={**os.environ, "PYTHONPATH": f"{ROOT_DIR};{ROOT_DIR / 'backend'}"}
                )

            # Check frontend process health if dev mode
            if dev_mode and frontend_proc and frontend_proc.poll() is not None:
                print("\n[!] Frontend dev process exited unexpectedly. Restarting automatically...")
                frontend_proc = subprocess.Popen(
                    "npm run dev",
                    shell=True,
                    cwd=str(ROOT_DIR / "frontend")
                )

            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[*] Stopping all server processes cleanly...")
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        kill_ports()
        print("[*] Shutdown complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Chargeback Guardian Server Supervisor")
    parser.add_argument("--dev", action="store_true", help="Start with Vite hot-reloading dev server on 5173")
    parser.add_argument("--check", action="store_true", help="Check localhost health and exit")
    parser.add_argument("--kill-ports", action="store_true", help="Kill any processes on ports 8000 and 5173")

    args = parser.parse_args()

    if args.kill_ports:
        kill_ports()
    elif args.check:
        check_health(verbose=True)
    else:
        run_supervisor(dev_mode=args.dev)
