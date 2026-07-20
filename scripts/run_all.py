"""Start FastAPI and Streamlit together for local demos."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    api_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.api.main:app",
        "--reload",
        "--port",
        "8000",
    ]
    ui_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app/ui/streamlit_app.py",
    ]
    api = subprocess.Popen(api_cmd, cwd=ROOT)
    ui = subprocess.Popen(ui_cmd, cwd=ROOT)
    try:
        print("FastAPI: http://127.0.0.1:8000/docs")
        print("Streamlit: http://localhost:8501")
        api.wait()
        ui.wait()
    except KeyboardInterrupt:
        api.terminate()
        ui.terminate()


if __name__ == "__main__":
    main()

