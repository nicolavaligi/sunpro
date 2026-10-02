#!/bin/bash
# ==============================================================================
# Launcher per Geo-Intelligence 3D — Solar Land Origination (Houdinick)
# ==============================================================================

DIR="/Users/houdinick/solar-land-acquisition-crawler"
cd "$DIR" || exit 1

URL="http://localhost:8503"

# Verifica se il server è già in esecuzione
if lsof -i :8503 >/dev/null 2>&1; then
    echo "☀️ Il server Geo-Intelligence 3D è già attivo su $URL"
    echo "🚀 Apertura della piattaforma nel browser..."
    open "$URL"
    exit 0
fi

# Se il server non è attivo, avvialo usando l'ambiente isolato
echo "☀️ Avvio piattaforma Geo-Intelligence 3D su $URL..."
"$DIR/.venv/bin/python3" "$DIR/run_app.py"
