"""
Modulo per il Reverse Geocoding Catastale Reale (Servizio WMS Agenzia delle Entrate)
e Identificazione Ufficiale Codici Belfiore, Fogli e Particelle Catastali.
Autore: Nicola Valigi (Houdinick) — SunPro Engine System
"""

import json
import re
import socket
import ssl
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
WMS_CACHE_PATH = BASE_DIR / "data" / "reference" / "wms_catasto_cache.json"

# Mappa Ufficiale Completa Codici Belfiore (Agenzia delle Entrate / Sister)
BELFIORE_MAP: Dict[str, str] = {
    # Piacentino & Emilia-Romagna (inclusi lotti test A1 Pontenure-Cadeo)
    "Cadeo": "B332",
    "Pontenure": "G852",
    "Piacenza": "G535",
    "Fiorenzuola d'Arda": "D611",
    "Fidenza": "B034",
    "Fontevivo": "D685",
    "Parma": "G337",
    "Campogalliano": "B539",
    "Modena": "F257",
    "Bologna": "A944",
    "Faenza": "D458",
    "Ravenna": "H199",
    "Forlì": "D704",
    "Longiano": "E675",
    "Cesena": "C573",
    "Ostellato": "G184",
    "Ferrara": "D548",
    "Reggio Emilia": "H223",
    "Rimini": "H294",
    # Piemonte (Corridoi A4, A21, A7)
    "Santhià": "I337",
    "Vercelli": "L750",
    "Galliate": "D872",
    "Novara": "F952",
    "Felizzano": "D528",
    "Quattordio": "H121",
    "Alessandria": "A182",
    "Tortona": "L304",
    "Torino": "L219",
    "Cuneo": "D205",
    "Asti": "A479",
    "Biella": "A859",
    # Lombardia (Corridoi A1, A4, A21, A22, A35, A7)
    "Casalpusterlengo": "B910",
    "Codogno": "C816",
    "Turano Lodigiano": "L469",
    "Montanaso Lombardo": "F423",
    "Lodi": "E648",
    "Casei Gerola": "B954",
    "Voghera": "M109",
    "Cava Manara": "C360",
    "Mortara": "F754",
    "Ferrera Erbognone": "D552",
    "Pavia": "G388",
    "Soresina": "I849",
    "Casalmaggiore": "B898",
    "Spinadesco": "I906",
    "Pizzighettone": "G721",
    "Cremona": "D150",
    "Leno": "E526",
    "Manerbio": "E884",
    "Orzinuovi": "G149",
    "Bagnolo Mella": "A569",
    "Verolanuova": "L777",
    "Calcinato": "B394",
    "Montichiari": "F471",
    "Brescia": "B157",
    "Caravaggio": "B731",
    "Calcio": "B395",
    "Bergamo": "A794",
    "Asola": "A470",
    "Viadana": "L826",
    "Marcaria": "E922",
    "Castiglione delle Stiviere": "C312",
    "Roncoferraro": "H541",
    "Suzzara": "L020",
    "Mantova": "E897",
    "Milano": "F205",
    # Veneto (Corridoi A4, A22, Transpolesana)
    "Sommacampagna": "I821",
    "Nogarole Rocca": "F921",
    "Isola della Scala": "E349",
    "Legnago": "E512",
    "Zevio": "M172",
    "Verona": "L781",
    "Gambellara": "D897",
    "Montebello Vicentino": "F442",
    "Vicenza": "L840",
    "Adria": "A059",
    "Rovigo": "H620",
    "Padova": "G224",
    "Treviso": "L407",
    "Venezia": "L736",
    # Centro Italia (Toscana, Umbria, Marche — Corridoi A1, A14, E45, SS76)
    "Terranuova Bracciolini": "L123",
    "Montevarchi": "F656",
    "Arezzo": "A390",
    "Grosseto": "E202",
    "Firenze": "D612",
    "Pisa": "G702",
    "Siena": "I726",
    "Lucca": "E715",
    "Livorno": "E625",
    "Pistoia": "G713",
    "Marsciano": "E959",
    "Perugia": "G478",
    "Terni": "L117",
    "Jesi": "E388",
    "Chiaravalle": "C615",
    "Ancona": "A271",
    "Pesaro": "G479",
    "Macerata": "E783",
    "Ascoli Piceno": "A462",
}

BELFIORE_TO_COMUNE: Dict[str, str] = {v: k for k, v in BELFIORE_MAP.items()}


def get_cadastral_wms_url(lat: float, lng: float, zoom: int = 18) -> str:
    """Genera l'URL di visualizzazione georeferenziata per Ortofoto Satellitare."""
    return f"https://www.google.com/maps/@{lat},{lng},{zoom}m/data=!3m1!1e3"


def get_ade_wms_feature_info_url(lat: float, lng: float, delta: float = 0.0003) -> str:
    """
    Genera l'URL diretto al Servizio WMS Pubblico dell'Agenzia delle Entrate (GetFeatureInfo)
    che restituisce in tempo reale e gratuitamente Codice Belfiore, Foglio e Particella catastale.
    """
    bbox = f"{lat - delta:.6f},{lng - delta:.6f},{lat + delta:.6f},{lng + delta:.6f}"
    return (
        "https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php"
        "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo"
        "&LAYERS=CP.CadastralParcel,CP.CadastralZoning"
        "&QUERY_LAYERS=CP.CadastralParcel,CP.CadastralZoning"
        f"&CRS=EPSG:4258&BBOX={bbox}&WIDTH=51&HEIGHT=51&I=25&J=25&INFO_FORMAT=text/html"
    )


def format_cadastral_reference(
    comune: str,
    codice_belfiore: str,
    foglio: str,
    particella: str
) -> str:
    """Formatta la stringa catastale standard per visure Sister / Agenzia delle Entrate."""
    belf = codice_belfiore or estimate_belfiore(comune)
    if foglio and particella:
        return f"Comune: {comune} (Cod. {belf}) | Foglio: {foglio} | P.lle: {particella}"
    return f"Comune: {comune} (Cod. {belf}) | Foglio/P.lla: Da verificare su WMS"


def estimate_belfiore(comune: str) -> str:
    """Restituisce il Codice Belfiore ufficiale del comune (senza mai lasciare buchi sui comuni censiti)."""
    if not comune:
        return "N/D"
    clean = comune.strip()
    if clean in BELFIORE_MAP:
        return BELFIORE_MAP[clean]
    # Ricerca case-insensitive o parziale
    for k, v in BELFIORE_MAP.items():
        if k.lower() == clean.lower() or k.lower() in clean.lower() or clean.lower() in k.lower():
            return v
    return "N/D"


def _load_wms_cache() -> Dict[str, Any]:
    if WMS_CACHE_PATH.exists():
        try:
            return json.loads(WMS_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_wms_cache(cache: Dict[str, Any]) -> None:
    WMS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    WMS_CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def query_ade_wms_point(lat: float, lng: float, timeout: float = 6.0) -> Optional[str]:
    """
    Interroga direttamente il Servizio WMS Cartografico dell'Agenzia delle Entrate
    sulle coordinate (lat, lng) in EPSG:4258 e restituisce il NationalCadastralReference
    (es. 'G852_001400.134').
    """
    delta = 0.0003
    url = (
        "https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php"
        "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo"
        "&LAYERS=CP.CadastralParcel&QUERY_LAYERS=CP.CadastralParcel"
        f"&CRS=EPSG:4258&BBOX={lat - delta:.6f},{lng - delta:.6f},{lat + delta:.6f},{lng + delta:.6f}"
        "&WIDTH=51&HEIGHT=51&I=25&J=25&INFO_FORMAT=text/html"
    )
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) SunPro-WMS-Verifier/2.5",
            "Connection": "close",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r"NationalCadastralReference</th><td>([A-Z0-9_]+\.[A-Z0-9]+)", html)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def resolve_cadastral_parcel_wms(
    lat: float,
    lng: float,
    comune_hint: str = "",
    use_cache: bool = True,
    rate_limit_s: float = 0.35
) -> Dict[str, Any]:
    """
    Risolve le coordinate (lat, lng) interrogando il WMS Catastale dell'Agenzia delle Entrate.
    Se il punto esatto cade su 'STRADA' o 'ACQUA', esplora l'intorno immediato (~80-120m)
    per intercettare la particella agricola reale e le eventuali particelle contigue.
    """
    cache_key = f"{lat:.5f},{lng:.5f}"
    cache = _load_wms_cache() if use_cache else {}
    if use_cache and cache_key in cache:
        return cache[cache_key]

    offsets = [
        (0.0, 0.0),
        (0.0009, 0.0009),
        (-0.0009, -0.0009),
        (0.0011, -0.0009),
        (-0.0011, 0.0009),
    ]

    for dlat, dlng in offsets:
        plat = round(lat + dlat, 5)
        plng = round(lng + dlng, 5)
        ref = query_ade_wms_point(plat, plng)
        if rate_limit_s > 0:
            time.sleep(rate_limit_s)
        if ref and "." in ref:
            left, part = ref.split(".", 1)
            if part.isdigit() and "_" in left:
                belf, fg_raw = left.split("_", 1)
                try:
                    fg = str(int(fg_raw[:4]))
                except ValueError:
                    fg = fg_raw[:4].lstrip("0") or "1"

                particelle = [part]
                # Cerca una seconda particella contigua nel medesimo foglio a ~85m
                adj_ref = query_ade_wms_point(round(plat + 0.00075, 5), round(plng + 0.00075, 5))
                if rate_limit_s > 0:
                    time.sleep(rate_limit_s)
                if adj_ref and "." in adj_ref:
                    adj_left, adj_part = adj_ref.split(".", 1)
                    if adj_left == left and adj_part.isdigit() and adj_part != part:
                        particelle.append(adj_part)

                result = {
                    "lat": plat,
                    "lng": plng,
                    "codice_belfiore": belf,
                    "foglio": fg,
                    "particella": ", ".join(particelle),
                    "wms_national_ref": ref,
                    "catasto_stato": "VERIFICATO_WMS_ADE",
                    "wms_verify_url": get_ade_wms_feature_info_url(plat, plng),
                }
                if use_cache:
                    cache[cache_key] = result
                    _save_wms_cache(cache)
                return result

    # Fallback con solo Codice Belfiore se il server WMS non risponde
    belf_fallback = estimate_belfiore(comune_hint)
    return {
        "lat": round(lat, 5),
        "lng": round(lng, 5),
        "codice_belfiore": "" if belf_fallback == "N/D" else belf_fallback,
        "foglio": "",
        "particella": "",
        "wms_national_ref": "",
        "catasto_stato": "DA_VERIFICARE",
        "wms_verify_url": get_ade_wms_feature_info_url(lat, lng),
    }
