#!/usr/bin/env python3
"""
Launcher per Geo-Intelligence 3D — Solar Land Origination (Houdinick).
Avvia il server ASGI su http://localhost:8503 e apre l'interfaccia nel browser predefinito.
Autore: Houdinick (Nicola Valigi)
"""

import sys
import webbrowser
import uvicorn
from pathlib import Path

# Add current dir to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from server import app

def main():
    port = 8503
    url = f"http://localhost:{port}"
    print(f"\n☀️ ===================================================================")
    print(f"☀️ Geo-Intelligence 3D — Solar Land Origination Platform (Houdinick)")
    print(f"☀️ Server attivo su: {url}")
    print(f"☀️ ===================================================================\n")

    # Avvia uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False, log_level="warning")

if __name__ == "__main__":
    main()
