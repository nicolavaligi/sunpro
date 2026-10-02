"""
Modulo per il Reverse Geocoding Catastale Italiano e Identificazione Particelle.
Autore: Nicola Valigi Engine System
"""

from typing import Dict, Any, Optional

def get_cadastral_wms_url(lat: float, lng: float, zoom: int = 18) -> str:
    """Genera l'URL di visualizzazione georeferenziata per il Catasto / Ortofoto."""
    return f"https://www.google.com/maps/@{lat},{lng},{zoom}m/data=!3m1!1e3"

def format_cadastral_reference(
    comune: str,
    codice_belfiore: str,
    foglio: str,
    particella: str
) -> str:
    """Formatta la stringa catastale standard per visure Sister / Agenzia delle Entrate."""
    return f"Comune: {comune} (Cod. {codice_belfiore}) | Foglio: {foglio} | P.lla: {particella}"

def estimate_belfiore(comune: str) -> str:
    """Tabella di fallback per Codici Belfiore dei comuni principali o censiti."""
    belfiore_map = {
        "Montichiari": "F471",
        "Cava Manara": "C360",
        "Roncoferraro": "H541",
        "Faenza": "D458",
        "Pontenure": "G852",
        "Zevio": "M172",
        "Adria": "A059",
        "Tortona": "L304",
        "Montevarchi": "F656",
        "Marsciano": "E959",
        "Jesi": "E388",
        "Brescia": "B157",
        "Pavia": "G388",
        "Mantova": "E897",
        "Verona": "L781",
        "Ravenna": "H199",
        "Piacenza": "G535",
        "Alessandria": "A182",
        "Arezzo": "A390",
        "Perugia": "G478",
        "Ancona": "A271"
    }
    return belfiore_map.get(comune, "N/D")
