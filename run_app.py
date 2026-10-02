#!/usr/bin/env python3
"""
Launcher per l'applicazione desktop Streamlit Solar Land Origination.
Autore: Houdinick (Nicola Valigi)
"""

import subprocess
import sys
import webbrowser
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    app_py = base_dir / "app.py"
    venv_streamlit = base_dir / ".venv" / "bin" / "streamlit"

    cmd = [
        str(venv_streamlit),
        "run",
        str(app_py),
        "--server.port=8503",
        "--server.headless=false",
        "--browser.gatherUsageStats=false"
    ]

    print(f"☀️ Avvio di Solar Land Origination su http://localhost:8503...")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nApplicazione terminata.")

if __name__ == "__main__":
    main()
