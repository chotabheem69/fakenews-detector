"""
VeritasAI - Application Launcher.
Starts the FastAPI backend and serves the modern frontend on http://127.0.0.1:8000.
"""

import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def check_dependencies():
    """Verify essential packages are installed."""
    missing = []
    for pkg in ["fastapi", "uvicorn", "pydantic", "requests", "bs4", "dotenv"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("=" * 65)
        print("⚠️  MISSING PYTHON PACKAGES DETECTED")
        print("=" * 65)
        print("Please install the required dependencies using:")
        print("   pip install -r requirements.txt")
        print("=" * 65)
        return False
    return True

def main():
    print("""
    =======================================================
       🛡️  VERITAS AI - FAKE NEWS DETECTION PLATFORM
    =======================================================
       BERT Sequence Classification & LLM Fact-Checking
       UI/UX: Modern Responsive SPA (Dark & Light Mode)
       Backend: FastAPI + SQLite + Transformers / Heuristics
    =======================================================
    """)

    if not check_dependencies():
        sys.exit(1)

    import uvicorn
    from backend.config import HOST, PORT

    url = f"http://{HOST}:{PORT}"
    print(f"🚀 Starting VeritasAI Server on: {url}")
    print("📖 API Documentation available on: " + f"{url}/docs")
    print("Press Ctrl+C to stop the server.\n")

    # Open browser in a deferred thread after 1.2s
    import threading
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)

if __name__ == "__main__":
    main()

