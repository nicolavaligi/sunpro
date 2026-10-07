"""
Modulo di Ingestione e Costruzione del Database Nazionale delle Cabine Primarie.
Scarica il dataset ufficiale nazionale GSE / ARERA (oltre 2.100 Cabine Primarie AC),
esegue il reverse-geocoding con comuni_coords.json e produce:
data/reference/cabine_primarie_italia.json
Autore: Nicola Valigi Engine System
"""

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DATA_DIR
from crawler.spatial_engine import haversine_distance_m

GSE_FEATURE_URL = "https://services2.arcgis.com/pROHh69WvVijk4nR/arcgis/rest/services/AC_Comuni/FeatureServer/21/query"
COMUNI_FILE = DATA_DIR / "reference" / "comuni_coords.json"
OUTPUT_FILE = DATA_DIR / "reference" / "cabine_primarie_italia.json"

# Mappa province a regione per geocodifica accurata
PROV_TO_REGION = {
    "Milano": "Lombardia", "Brescia": "Lombardia", "Bergamo": "Lombardia",
    "Monza e della Brianza": "Lombardia", "Pavia": "Lombardia", "Mantova": "Lombardia",
    "Cremona": "Lombardia", "Varese": "Lombardia", "Como": "Lombardia", "Lecco": "Lombardia",
    "Lodi": "Lombardia", "Sondrio": "Lombardia",
    "Verona": "Veneto", "Vicenza": "Veneto", "Padova": "Veneto", "Treviso": "Veneto",
    "Rovigo": "Veneto", "Venezia": "Veneto", "Belluno": "Veneto",
    "Bologna": "Emilia-Romagna", "Modena": "Emilia-Romagna", "Reggio Emilia": "Emilia-Romagna",
    "Parma": "Emilia-Romagna", "Piacenza": "Emilia-Romagna", "Ravenna": "Emilia-Romagna",
    "Forlì-Cesena": "Emilia-Romagna", "Ferrara": "Emilia-Romagna", "Rimini": "Emilia-Romagna",
    "Torino": "Piemonte", "Alessandria": "Piemonte", "Novara": "Piemonte", "Cuneo": "Piemonte",
    "Asti": "Piemonte", "Vercelli": "Piemonte", "Biella": "Piemonte",
    "Firenze": "Toscana", "Arezzo": "Toscana", "Pisa": "Toscana", "Lucca": "Toscana",
    "Livorno": "Toscana", "Siena": "Toscana", "Pistoia": "Toscana", "Grosseto": "Toscana",
    "Perugia": "Umbria", "Terni": "Umbria",
    "Ancona": "Marche", "Pesaro e Urbino": "Marche", "Macerata": "Marche", "Ascoli Piceno": "Marche",
    "Roma": "Lazio", "Latina": "Lazio", "Frosinone": "Lazio", "Viterbo": "Lazio", "Rieti": "Lazio",
    "Napoli": "Campania", "Salerno": "Campania", "Caserta": "Campania", "Avellino": "Campania", "Benevento": "Campania",
    "Bari": "Puglia", "Lecce": "Puglia", "Taranto": "Puglia", "Foggia": "Puglia", "Brindisi": "Puglia", "Barletta-Andria-Trani": "Puglia",
    "Potenza": "Basilicata", "Matera": "Basilicata",
    "Catanzaro": "Calabria", "Cosenza": "Calabria", "Reggio Calabria": "Calabria", "Crotone": "Calabria", "Vibo Valentia": "Calabria",
    "Palermo": "Sicilia", "Catania": "Sicilia", "Messina": "Sicilia", "Siracusa": "Sicilia", "Ragusa": "Sicilia", "Trapani": "Sicilia", "Agrigento": "Sicilia", "Caltanissetta": "Sicilia", "Enna": "Sicilia",
    "Cagliari": "Sardegna", "Sassari": "Sardegna", "Nuoro": "Sardegna", "Oristano": "Sardegna", "Sud Sardegna": "Sardegna",
    "Genova": "Liguria", "Savona": "Liguria", "La Spezia": "Liguria", "Imperia": "Liguria",
    "Trento": "Trentino-Alto Adige", "Bolzano": "Trentino-Alto Adige",
    "Trieste": "Friuli-Venezia Giulia", "Udine": "Friuli-Venezia Giulia", "Pordenone": "Friuli-Venezia Giulia", "Gorizia": "Friuli-Venezia Giulia",
    "L'Aquila": "Abruzzo", "Pescara": "Abruzzo", "Chieti": "Abruzzo", "Teramo": "Abruzzo",
    "Campobasso": "Molise", "Isernia": "Molise",
    "Aosta": "Valle d'Aosta"
}

def load_comuni() -> List[Dict[str, Any]]:
    if COMUNI_FILE.exists():
        with open(COMUNI_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def find_closest_comune(lat: float, lng: float, comuni: List[Dict[str, Any]]) -> Dict[str, str]:
    best_c = "Comune non identificato"
    min_d = 999999.0
    for c in comuni:
        c_lat = c.get("lat")
        c_lon = c.get("lon")
        if c_lat is not None and c_lon is not None:
            d = haversine_distance_m(lat, lng, c_lat, c_lon)
            if d < min_d:
                min_d = d
                best_c = c.get("name", best_c)
                if d < 1200:
                    break
    reg = PROV_TO_REGION.get(best_c, "Italia")
    return {"comune": best_c, "regione": reg, "distanza_m": int(min_d)}

def fetch_all_gse_substations() -> List[Dict[str, Any]]:
    print("📡 Connessione al FeatureServer ufficiale ARERA / GSE...")
    features = []
    batch_size = 500
    offset = 0
    total_target = 2107

    with httpx.Client(timeout=60.0) as client:
        while offset < total_target:
            params = {
                "where": "1=1",
                "outFields": "OBJECTID,COD_AC,RAG_SOC",
                "returnGeometry": "false",
                "returnCentroid": "true",
                "resultOffset": offset,
                "resultRecordCount": batch_size,
                "f": "json"
            }
            success = False
            for attempt in range(1, 4):
                try:
                    resp = client.get(GSE_FEATURE_URL, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        batch = data.get("features", [])
                        if not batch:
                            success = True
                            break
                        features.extend(batch)
                        print(f"  ✓ Scaricate {len(batch)} cabine (Offset: {offset}, Totale parziale: {len(features)})...")
                        success = True
                        break
                    else:
                        print(f"  ⚠️ Tentativo {attempt}: status {resp.status_code}")
                except Exception as e:
                    print(f"  ⚠️ Tentativo {attempt} fallito (Offset {offset}): {e}")
            
            if not success:
                print(f"  ❌ Impossibile scaricare batch a offset {offset}, interruzione.")
                break
            offset += batch_size

    print(f"📊 Totale Cabine Primarie estratte: {len(features)}")
    return features

def build_national_substations_dataset() -> Path:
    raw_feats = fetch_all_gse_substations()
    comuni = load_comuni()
    print(f"🗺️ Georeferenziazione e reverse lookup su {len(comuni)} comuni italiani...")

    catalog = []
    for f in raw_feats:
        attrs = f.get("attributes", {})
        centroid = f.get("centroid", {})
        lng = centroid.get("x")
        lat = centroid.get("y")
        
        if not lat or not lng:
            continue

        cod_ac = attrs.get("COD_AC", "AC_N/D")
        rag_soc = attrs.get("RAG_SOC", "Distributore Nazionale (DSO)")

        geo_loc = find_closest_comune(lat, lng, comuni)
        comune_name = geo_loc["comune"]
        regione = geo_loc["regione"]

        # Formatta livello tensione standard in base al distributore/zona
        if "areti" in rag_soc.lower() or "unareti" in rag_soc.lower():
            voltage = "132/20 kV"
        elif "inrete" in rag_soc.lower() or "v-reti" in rag_soc.lower():
            voltage = "132/15 kV"
        else:
            voltage = "132/20 kV"

        name = f"CP {comune_name} ({cod_ac})"

        catalog.append({
            "codice_ac": cod_ac,
            "name": name,
            "comune": comune_name,
            "regione": regione,
            "lat": round(lat, 5),
            "lng": round(lng, 5),
            "voltage": voltage,
            "operator": rag_soc,
            "type": "CABINA_PRIMARIA_UFFICIALE_ARERA",
            "fonte": "ARERA_GSE_AREE_CONVENZIONALI_OPEN_DATA"
        })

    # Ordina per regione e comune
    catalog.sort(key=lambda x: (x["regione"], x["comune"]))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(catalog, out, indent=2, ensure_ascii=False)

    print(f"✅ Database Nazionale salvato in: {OUTPUT_FILE} ({len(catalog)} Cabine Primarie)")
    return OUTPUT_FILE

if __name__ == "__main__":
    build_national_substations_dataset()
