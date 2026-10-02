"""
Modulo Substation Finder per SunPro (Nicola Valigi Engine System).
Ricerca cabine primarie AT/MT, stazioni elettriche Terna ed Enel Distribuzione
entro un raggio specificato da coordinate GPS con calcolo esatto della distanza e stima CAPEX.
Autore: Nicola Valigi Engine System
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import httpx

from crawler.spatial_engine import haversine_distance_m
from config import CABLE_COST_PER_KM, SUBSTATION_BAY_COST

# Catalogo di riferimento georeferenziato per le principali Cabine Primarie del Nord e Centro
PRIMARY_SUBSTATIONS_CATALOG = [
    # Lombardia
    {"name": "CP Montichiari 132/15 kV", "lat": 45.4089, "lng": 10.4001, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Brescia Nord 132/15 kV", "lat": 45.5520, "lng": 10.2210, "voltage": "132/15 kV", "operator": "A2A Reti Elettriche", "type": "CABINA_PRIMARIA"},
    {"name": "CP Brescia Pietra 132/15 kV", "lat": 45.5298, "lng": 10.1943, "voltage": "132/15 kV", "operator": "A2A Reti Elettriche", "type": "CABINA_PRIMARIA"},
    {"name": "STAZIONE AT Terna Ospitaletto", "lat": 45.5428, "lng": 10.0628, "voltage": "132 kV", "operator": "Terna Rete Italia", "type": "STAZIONE_AT"},
    {"name": "CP Sesto San Giovanni 132/20 kV", "lat": 45.5340, "lng": 9.2310, "voltage": "132/20 kV", "operator": "Unareti", "type": "CABINA_PRIMARIA"},
    {"name": "STAZIONE AT Terna Vulcano CDS", "lat": 45.5426, "lng": 9.2469, "voltage": "220/132 kV", "operator": "Terna Rete Italia", "type": "STAZIONE_AT"},
    {"name": "CP Musocco Milano 132/15 kV", "lat": 45.5070, "lng": 9.1245, "voltage": "132/15 kV", "operator": "Unareti", "type": "CABINA_PRIMARIA"},
    {"name": "CP Cologno Monzese 132/15 kV", "lat": 45.5230, "lng": 9.3028, "voltage": "132/15 kV", "operator": "Unareti", "type": "CABINA_PRIMARIA"},
    {"name": "CP Treviglio Ovest 132/15 kV", "lat": 45.5113, "lng": 9.5730, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Mantova Nord 132/20 kV", "lat": 45.1720, "lng": 10.8120, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Roncoferraro 132/20 kV", "lat": 45.1320, "lng": 10.9520, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Pavia Sud 132/15 kV", "lat": 45.1384, "lng": 9.1082, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "Sottostazione RFI Broni", "lat": 45.0610, "lng": 9.2610, "voltage": "132/3 kV", "operator": "Rete Ferroviaria Italiana", "type": "SOTTOSTAZIONE_FERROVIARIA"},
    {"name": "STAZIONE AT Terna Turano Centrale", "lat": 45.2410, "lng": 9.6120, "voltage": "380/132 kV", "operator": "Terna Rete Italia", "type": "STAZIONE_AT"},

    # Veneto
    {"name": "CP Zevio 132/20 kV", "lat": 45.3725, "lng": 11.1350, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Verona Sud 132/20 kV", "lat": 45.4120, "lng": 10.9850, "voltage": "132/20 kV", "operator": "AGSM AIM", "type": "CABINA_PRIMARIA"},
    {"name": "CP Adria 132/20 kV", "lat": 45.0612, "lng": 12.0498, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Padova Industriale 132/20 kV", "lat": 45.3980, "lng": 11.9320, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},

    # Emilia-Romagna
    {"name": "CP Faenza Nord 132/15 kV", "lat": 44.2981, "lng": 11.8741, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Pontenure 132/15 kV", "lat": 44.9984, "lng": 9.7712, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Piacenza Est 132/15 kV", "lat": 45.0420, "lng": 9.7210, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Bologna Roveri 132/15 kV", "lat": 44.5120, "lng": 11.3980, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Ravenna Darsena 132/15 kV", "lat": 44.4250, "lng": 12.2210, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},

    # Piemonte
    {"name": "CP Tortona 132/15 kV", "lat": 44.9082, "lng": 8.8654, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Alessandria Sud 132/15 kV", "lat": 44.8950, "lng": 8.6210, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},

    # Centro Italia (Toscana, Umbria, Marche)
    {"name": "CP Montevarchi 132/15 kV", "lat": 43.5312, "lng": 11.5645, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Arezzo San Leo 132/15 kV", "lat": 43.4680, "lng": 11.8540, "voltage": "132/15 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Marsciano 132/20 kV", "lat": 42.9124, "lng": 12.3389, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"},
    {"name": "CP Jesi Z.I. 132/20 kV", "lat": 43.5284, "lng": 13.2654, "voltage": "132/20 kV", "operator": "Enel Distribuzione", "type": "CABINA_PRIMARIA"}
]

def format_voltage_str(v_raw: Any) -> str:
    if not v_raw:
        return "MT 15/20 kV"
    s = str(v_raw).replace(";", "/").strip()
    try:
        val = int(s.split("/")[0])
        if val >= 1000:
            return f"{int(val/1000)} kV"
        return f"{val} V"
    except Exception:
        return s

def query_overpass_substations(lat: float, lng: float, radius_m: int = 3000) -> List[Dict[str, Any]]:
    """Cerca cabine primarie reali su OpenStreetMap tramite Overpass API."""
    query = f"""
    [out:json][timeout:10];
    (
      node["power"="substation"](around:{radius_m},{lat},{lng});
      way["power"="substation"](around:{radius_m},{lat},{lng});
    );
    out center tags;
    """
    headers = {"User-Agent": "SunPro-SubstationFinder/1.0"}
    mirrors = [
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass-api.de/api/interpreter"
    ]

    for m in mirrors:
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(m, data={"data": query}, headers=headers)
                if resp.status_code == 200:
                    elements = resp.json().get("elements", [])
                    results = []
                    for el in elements:
                        tags = el.get("tags", {})
                        center = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
                        c_lat = center.get("lat")
                        c_lng = center.get("lon")
                        if not c_lat or not c_lng:
                            continue
                        
                        dist = haversine_distance_m(lat, lng, c_lat, c_lng)
                        name = tags.get("name") or tags.get("operator") or tags.get("ref") or f"Cabina {tags.get('substation', 'MT/AT')}"
                        volt = format_voltage_str(tags.get("voltage"))
                        operator = tags.get("operator", "Distributore Locale (DSO)")

                        # Stima CAPEX allaccio
                        dist_km = max(0.15, dist / 1000.0)
                        capex = round((dist_km * CABLE_COST_PER_KM) + SUBSTATION_BAY_COST, 0)

                        results.append({
                            "name": name,
                            "lat": round(c_lat, 5),
                            "lng": round(c_lng, 5),
                            "distanza_m": int(dist),
                            "livello_tensione": volt,
                            "operatore": operator,
                            "capex_allaccio_stimato_eur": capex,
                            "tipo": tags.get("substation", "substation").upper(),
                            "fonte": "OPENSTREETMAP_OVERPASS_LIVE"
                        })
                    return sorted(results, key=lambda x: x["distanza_m"])
        except Exception:
            continue
    return []

def find_substations_around_coords(lat: float, lng: float, radius_m: int = 3000) -> List[Dict[str, Any]]:
    """
    Trova tutte le cabine primarie e stazioni AT entro il raggio specificato.
    Interroga Overpass Live e combina/completa con il catalogo primario di rete.
    """
    found = query_overpass_substations(lat, lng, radius_m)

    # Se overpass ha trovato cabine, le arricchiamo o ritorniamo
    # Includiamo anche cabine dal catalogo di riferimento se entro il raggio
    for cat_sub in PRIMARY_SUBSTATIONS_CATALOG:
        d = haversine_distance_m(lat, lng, cat_sub["lat"], cat_sub["lng"])
        if d <= radius_m:
            # Verifica che non sia già presente un doppione vicino (< 300m)
            if not any(haversine_distance_m(f["lat"], f["lng"], cat_sub["lat"], cat_sub["lng"]) < 300 for f in found):
                dist_km = max(0.15, d / 1000.0)
                capex = round((dist_km * CABLE_COST_PER_KM) + SUBSTATION_BAY_COST, 0)
                found.append({
                    "name": cat_sub["name"],
                    "lat": cat_sub["lat"],
                    "lng": cat_sub["lng"],
                    "distanza_m": int(d),
                    "livello_tensione": cat_sub["voltage"],
                    "operatore": cat_sub["operator"],
                    "capex_allaccio_stimato_eur": capex,
                    "tipo": cat_sub["type"],
                    "fonte": "CATALOGO_RETE_NAZIONALE_AT_MT"
                })

    # Se ancora vuoto (raggio stretto), allarga virtualmente per restituire almeno la più vicina
    if not found:
        closest = None
        min_d = 9999999.0
        for cat_sub in PRIMARY_SUBSTATIONS_CATALOG:
            d = haversine_distance_m(lat, lng, cat_sub["lat"], cat_sub["lng"])
            if d < min_d:
                min_d = d
                closest = cat_sub
        if closest:
            dist_km = max(0.15, min_d / 1000.0)
            capex = round((dist_km * CABLE_COST_PER_KM) + SUBSTATION_BAY_COST, 0)
            found.append({
                "name": closest["name"],
                "lat": closest["lat"],
                "lng": closest["lng"],
                "distanza_m": int(min_d),
                "livello_tensione": closest["voltage"],
                "operatore": closest["operator"],
                "capex_allaccio_stimato_eur": capex,
                "tipo": closest["type"],
                "fonte": "CATALOGO_RETE_NAZIONALE_AT_MT (PIÙ VICINA FUORI RAGGIO)"
            })

    return sorted(found, key=lambda x: x["distanza_m"])
