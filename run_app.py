#!/usr/bin/env python3
"""
Launcher per Geo-Intelligence 3D — Solar Land Origination (Nicola Valigi Engine System).
Avvia il server ASGI su http://localhost:8503 e apre l'interfaccia nel browser predefinito.
Autore: Nicola Valigi Engine System
"""

import sys
import threading
import webbrowser
import uvicorn
from pathlib import Path

# Add current dir to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from server import app

def open_browser(url: str):
    try:
        webbrowser.open(url)
    except Exception:
        pass

def main():
    port = 8503
    url = f"http://localhost:{port}"
    print(f"\n☀️ ===================================================================")
    print(f"☀️ Geo-Intelligence 3D — Solar Land Origination Platform (Nicola Valigi Engine System)")
    print(f"☀️ Piattaforma attiva su: {url}")
    print(f"☀️ Apertura browser in corso...")
    print(f"☀️ ===================================================================\n")

    # Apertura browser automatica dopo 1 secondo
    threading.Timer(1.0, open_browser, args=[url]).start()

    # Avvia uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False, log_level="warning")

if __name__ == "__main__":
    main()
