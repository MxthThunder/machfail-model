"""
Unified Launcher for Person 2 (Dashboard) & Person 3 (AI Subsystem)
Starts both the FastAPI AI Backend and the React/Vite Frontend concurrently.
"""

import os
import sys
import subprocess
import time
import webbrowser

def is_port_open(host: str, port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 70)
    print("🚀 INDUSTRIAL MACHINE PREDICTIVE MAINTENANCE SYSTEM")
    print("   Person 2 (Web Dashboard) + Person 3 (AI Microservice)")
    print("=" * 70)

    # 1. Start FastAPI Backend (Person 3)
    print("\n[1/3] Starting Python FastAPI AI Microservice (Person 3)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=root_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 2. Start Vite Frontend (Person 2)
    print("[2/3] Starting INDUSTRIA React Dashboard (Person 2)...")
    frontend_cmd = "npm run dev" if os.name != 'nt' else "cmd.exe /c npm run dev"
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 3. Wait for services to initialize
    print("[3/3] Waiting for services to initialize...")
    backend_ready = False
    frontend_ready = False

    for _ in range(25):
        time.sleep(1)
        if not backend_ready and is_port_open("127.0.0.1", 8000):
            backend_ready = True
            print("  ✓ AI Backend live at http://127.0.0.1:8000 (Swagger: /docs)")
        if not frontend_ready and is_port_open("127.0.0.1", 8443):
            frontend_ready = True
            print("  ✓ INDUSTRIA Dashboard live at http://localhost:8443")
        if backend_ready and frontend_ready:
            break

    print("\n" + "=" * 70)
    print("🌟 SYSTEM CONNECTED & OPERATIONAL")
    print("   • Web Dashboard UI : http://localhost:8443")
    print("   • AI Inference API : http://127.0.0.1:8000/predict")
    print("   • API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 70)
    print("\nPress Ctrl+C to stop both servers.")

    # Open in browser
    webbrowser.open("http://localhost:8443/")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
