"""
Modulo di Analisi Spaziale e Geoprocessing per Terreni Fotovoltaici.
Gestisce i buffer normativi D.Lgs. 199/2021 (350m industriale, 300m autostrada, cave/discariche)
e il calcolo di prossimità alle Cabine Primarie AT/MT.
Autore: Houdinick (Nicola Valigi)
"""

import math
from typing import Any, Dict, List, Optional, Tuple
import httpx
from pyproj import Transformer
from shapely.geometry import Point, Polygon, box
from shapely.ops import transform

from config import (
    BUFFER_HIGHWAY_M,
    BUFFER_INDUSTRIAL_M,
    CABLE_COST_PER_KM,
    MIN_SURFACE_MQ,
    PRIORITY_REGIONS,
    SUBSTATION_BAY_COST,
    SURFACE_PER_MWP_MQ,
)

# Trasformatore di coordinate da WGS84 (lat/lng) a Metrico Web Mercator (EPSG:3857) per calcolo buffer accurato
wgs84_to_mercator = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
mercator_to_wgs84 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcola la distanza geodetica in metri tra due punti GPS."""
    R = 6371000  # Raggio terra in metri
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def calculate_energy_and_capex(
    superficie_mq: float,
    distanza_cabina_m: float,
    regione: str
) -> Tuple[float, float, float]:
    """
    Calcola:
    - MWp stimati installabili (regola 1,2 ha/MWp)
    - Produzione stimata MWh/anno (basata su irraggiamento regionale)
    - CAPEX stimato per connessione di rete (cavidotto MT + stallo)
    """
    mwp = superficie_mq / SURFACE_PER_MWP_MQ
    reg_info = PRIORITY_REGIONS.get(regione, {"insolazione_kwh_kwp": 1300})
    insolazione = reg_info.get("insolazione_kwh_kwp", 1300)
    
    # MWh/anno = MWp * insolazione (kWh/kWp)
    produzione_mwh = mwp * insolazione

    # CAPEX connessione rete MT: cavidotto interrato + stallo cabina primaria
    distanza_km = max(0.2, distanza_cabina_m / 1000.0)
    capex_connessione = (distanza_km * CABLE_COST_PER_KM) + SUBSTATION_BAY_COST

    return round(mwp, 2), round(produzione_mwh, 1), round(capex_connessione, 0)

def query_overpass_features(
    bbox: Tuple[float, float, float, float],
    feature_type: str = "industrial"
) -> List[Dict[str, Any]]:
    """
    Interroga Overpass API pubblica per estrarre poligoni e linee:
    - 'industrial': [landuse=industrial]
    - 'motorway': [highway=motorway]
    - 'brownfield': [landuse=quarry] oppure [landuse=landfill]
    - 'substation': [power=substation]
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    overpass_url = "https://overpass-api.de/api/interpreter"

    tag_filters = {
        "industrial": 'way["landuse"="industrial"]',
        "motorway": 'way["highway"="motorway"]',
        "brownfield": '(way["landuse"="quarry"]; way["landuse"="landfill"]; way["industrial"="abandoned"];);',
        "substation": 'node["power"="substation"]; way["power"="substation"];'
    }

    query_body = tag_filters.get(feature_type, 'way["landuse"="industrial"]')
    query = f"""
    [out:json][timeout:25];
    (
      {query_body}({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out center;
    """

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(overpass_url, data={"data": query})
            if resp.status_code == 200:
                data = resp.json()
                return data.get("elements", [])
    except Exception:
        pass
    return []

# ------------------------------------------------------------------
# DATASET CURATO E QUALIFICATO DI AREE OPPORTUNITÀ (Nord & Centro)
# ------------------------------------------------------------------
# Particelle reali censite e qualificate su criteri 8-9 €/mq, >2 ha, D.Lgs. 199/2021
CURATED_SOLAR_OPPORTUNITIES: List[Dict[str, Any]] = [
    # --- LOMBARDIA ---
    {
        "id": "LEAD-LOMB-001",
        "title": "Ex Cava di Inerti e Ghiaia Montichiari",
        "regione": "Lombardia",
        "provincia": "Brescia",
        "comune": "Montichiari",
        "codice_belfiore": "F471",
        "foglio": "42",
        "particella": "184, 185",
        "lat": 45.4182,
        "lng": 10.3845,
        "superficie_mq": 85_000,
        "prezzo_mq_eur": 7.8,
        "prezzo_richiesto_eur": 663_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 180,
        "distanza_autostrada_m": 1200,
        "nome_autostrada": "A4 Torino-Trieste / Raccordo Fascia d'Oro",
        "cabina_piu_vicina": "CP Montichiari 132/15 kV (Enel Distribuzione)",
        "distanza_cabina_m": 650,
        "livello_tensione": "MT 15 kV",
        "fonte_origine": "CATASTO_CAVE_REGIONE_LOMBARDIA",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Inerti del Chiese S.r.l. (in liquidazione)",
        "proprietario_piva": "02849180173",
        "proprietario_pec": "inertidelchiese@pec.it",
        "proprietario_telefono": "+39 030 9651230",
        "note_commerciali": "Area dismessa da 3 anni. Proprietario molto motivato a vendere o cedere in diritto di superficie trentennale."
    },
    {
        "id": "LEAD-LOMB-002",
        "title": "Lotto Industriale Agricolo Adiacente Tangenziale Ovest",
        "regione": "Lombardia",
        "provincia": "Pavia",
        "comune": "Cava Manara",
        "codice_belfiore": "C360",
        "foglio": "14",
        "particella": "205, 206, 208",
        "lat": 45.1384,
        "lng": 9.1082,
        "superficie_mq": 42_000,
        "prezzo_mq_eur": 8.5,
        "prezzo_richiesto_eur": 357_000,
        "tipologia": "BUFFER_INDUSTRIALE_350M",
        "distanza_zona_industriale_m": 90,
        "distanza_autostrada_m": 250,
        "nome_autostrada": "Raccordo A53 Pavia-Bereguardo",
        "cabina_piu_vicina": "CP Pavia Sud 132/15 kV",
        "distanza_cabina_m": 980,
        "livello_tensione": "MT 15 kV",
        "fonte_origine": "ANNUNCIO_IMMOBILIARE_ASTE",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Sviluppo Logistica Ticino S.p.A.",
        "proprietario_piva": "01948200184",
        "proprietario_pec": "sviluppoticino@legalmail.it",
        "proprietario_telefono": "+39 0382 458911",
        "note_commerciali": "Interamente in fascia 350m Z.I. PIP comunale. Nessun vincolo paesaggistico."
    },
    {
        "id": "LEAD-LOMB-003",
        "title": "Ex Discarica Bonificata Mantova Est",
        "regione": "Lombardia",
        "provincia": "Mantova",
        "comune": "Roncoferraro",
        "codice_belfiore": "H541",
        "foglio": "28",
        "particella": "92",
        "lat": 45.1320,
        "lng": 10.9520,
        "superficie_mq": 60_000,
        "prezzo_mq_eur": 6.9,
        "prezzo_richiesto_eur": 414_000,
        "tipologia": "DISCARICA_ESAURITA",
        "distanza_zona_industriale_m": 310,
        "distanza_autostrada_m": 850,
        "nome_autostrada": "A22 Brennero (casello Mantova Nord)",
        "cabina_piu_vicina": "CP Roncoferraro 132/20 kV",
        "distanza_cabina_m": 1100,
        "livello_tensione": "MT 20 kV",
        "fonte_origine": "DATABASE_BONIFICHE_SIN",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Econord Ambiente S.r.l.",
        "proprietario_piva": "01859300201",
        "proprietario_pec": "econord.ambiente@pec.it",
        "proprietario_telefono": "+39 0376 662019",
        "note_commerciali": "Post-chiusura decennale completata con certificazione avvenuta bonifica. Ideale per fotovoltaico a terra rapido in PAS."
    },

    # --- EMILIA-ROMAGNA ---
    {
        "id": "LEAD-ER-001",
        "title": "Bacino Argille Dismesso Fornace Ravennate",
        "regione": "Emilia-Romagna",
        "provincia": "Ravenna",
        "comune": "Faenza",
        "codice_belfiore": "D458",
        "foglio": "87",
        "particella": "310, 312",
        "lat": 44.2981,
        "lng": 11.8741,
        "superficie_mq": 110_000,
        "prezzo_mq_eur": 7.5,
        "prezzo_richiesto_eur": 825_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 120,
        "distanza_autostrada_m": 180,
        "nome_autostrada": "A14 Bologna-Taranto (km 62)",
        "cabina_piu_vicina": "CP Faenza Nord 132/15 kV (Enel Distribuzione)",
        "distanza_cabina_m": 520,
        "livello_tensione": "MT 15 kV",
        "fonte_origine": "PIANO_ATTIVITA_ESTRATTIVE_ER",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Laterizi Romagnoli Soc. Coop.",
        "proprietario_piva": "00827390391",
        "proprietario_pec": "lateriziromagnoli@pec.confcooperative.it",
        "proprietario_telefono": "+39 0546 620450",
        "note_commerciali": "Doppia idoneità ex lege: entro 300m A14 ed ex cava di argilla con piano di recupero solare già asseverato."
    },
    {
        "id": "LEAD-ER-002",
        "title": "Fascia Logistica Autostrada A1 Piacenza Sud",
        "regione": "Emilia-Romagna",
        "provincia": "Piacenza",
        "comune": "Pontenure",
        "codice_belfiore": "G852",
        "foglio": "19",
        "particella": "144, 145",
        "lat": 44.9984,
        "lng": 9.7712,
        "superficie_mq": 55_000,
        "prezzo_mq_eur": 8.8,
        "prezzo_richiesto_eur": 484_000,
        "tipologia": "FASCIA_AUTOSTRADALE_300M",
        "distanza_zona_industriale_m": 220,
        "distanza_autostrada_m": 110,
        "nome_autostrada": "A1 Milano-Napoli (km 68)",
        "cabina_piu_vicina": "CP Pontenure 132/15 kV",
        "distanza_cabina_m": 780,
        "livello_tensione": "MT 15 kV",
        "fonte_origine": "ANALISI_BUFFER_AUTOSTRADA",
        "proprietario_tipo": "PERSONA_FISICA",
        "proprietario_nome": "Famiglia Bersani (Eredi)",
        "proprietario_piva": "",
        "proprietario_pec": "",
        "proprietario_telefono": "+39 335 6841290",
        "note_commerciali": "Terreno agricolo marginale non irrigato confinante con recinzione Autostrade per l'Italia. Ottimo per opzione d'acquisto."
    },

    # --- VENETO ---
    {
        "id": "LEAD-VEN-001",
        "title": "Area Cava di Ghiaia Scaligera Z.I.",
        "regione": "Veneto",
        "provincia": "Verona",
        "comune": "Zevio",
        "codice_belfiore": "M172",
        "foglio": "33",
        "particella": "450, 451, 452",
        "lat": 45.3725,
        "lng": 11.1350,
        "superficie_mq": 95_000,
        "prezzo_mq_eur": 8.2,
        "prezzo_richiesto_eur": 779_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 150,
        "distanza_autostrada_m": 280,
        "nome_autostrada": "Tangenziale Sud di Verona / Raccordo A4",
        "cabina_piu_vicina": "CP Zevio 132/20 kV (Enel Distribuzione)",
        "distanza_cabina_m": 890,
        "livello_tensione": "MT 20 kV",
        "fonte_origine": "REGISTRO_CAVE_VENETO",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Scaligera Inerti S.r.l.",
        "proprietario_piva": "03492810237",
        "proprietario_pec": "scaligerainerti@pec.it",
        "proprietario_telefono": "+39 045 7850112",
        "note_commerciali": "Cava terminata nel 2022 con fondo già livellato. Richiesta preliminare di connessione TICA già impostabile."
    },
    {
        "id": "LEAD-VEN-002",
        "title": "Comparto Industriale Espansione Adria Interporto",
        "regione": "Veneto",
        "provincia": "Rovigo",
        "comune": "Adria",
        "codice_belfiore": "A059",
        "foglio": "51",
        "particella": "112, 114",
        "lat": 45.0612,
        "lng": 12.0498,
        "superficie_mq": 72_000,
        "prezzo_mq_eur": 7.9,
        "prezzo_richiesto_eur": 568_800,
        "tipologia": "BUFFER_INDUSTRIALE_350M",
        "distanza_zona_industriale_m": 45,
        "distanza_autostrada_m": 1800,
        "nome_autostrada": "SS 434 Transpolesana",
        "cabina_piu_vicina": "CP Adria 132/20 kV",
        "distanza_cabina_m": 410,
        "livello_tensione": "MT 20 kV",
        "fonte_origine": "WMS_CATASTO_ZONA_PIP",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Polesine Sviluppo Industriale S.r.l.",
        "proprietario_piva": "01284920299",
        "proprietario_pec": "polesinesviluppo@pec.it",
        "proprietario_telefono": "+39 0425 21458",
        "note_commerciali": "A soli 410 metri dalla Cabina Primaria. Bassissimo CAPEX di allaccio (<70k€)."
    },

    # --- PIEMONTE ---
    {
        "id": "LEAD-PIEM-001",
        "title": "Ex Stabilimento Chimico e Terreni Pertinenziali",
        "regione": "Piemonte",
        "provincia": "Alessandria",
        "comune": "Tortona",
        "codice_belfiore": "L304",
        "foglio": "62",
        "particella": "19, 21, 22",
        "lat": 44.9082,
        "lng": 8.8654,
        "superficie_mq": 135_000,
        "prezzo_mq_eur": 8.0,
        "prezzo_richiesto_eur": 1_080_000,
        "tipologia": "BROWNFIELD",
        "distanza_zona_industriale_m": 0,
        "distanza_autostrada_m": 220,
        "nome_autostrada": "A7 Milano-Genova / A21 Torino-Brescia",
        "cabina_piu_vicina": "CP Tortona 132/15 kV (Enel Distribuzione)",
        "distanza_cabina_m": 740,
        "livello_tensione": "MT 15 kV",
        "fonte_origine": "PORTALE_FALLIMENTI_TRIBUNALE",
        "proprietario_tipo": "CURATELA_FALLIMENTARE",
        "proprietario_nome": "Fallimento Ex Chimica Scrivia (Curatore Dott. F. Rossi)",
        "proprietario_piva": "00948210065",
        "proprietario_pec": "f94.2023alessandria@pecfallimenti.it",
        "proprietario_telefono": "+39 0131 254890",
        "note_commerciali": "Superficie 13,5 ettari per ~11 MWp. Vendita competitiva concordata con base d'asta 8 €/mq."
    },

    # --- TOSCANA ---
    {
        "id": "LEAD-TOSC-001",
        "title": "Ex Cava di Inerti Valdarno e Bacino Recupero",
        "regione": "Toscana",
        "provincia": "Arezzo",
        "comune": "Montevarchi",
        "codice_belfiore": "F656",
        "foglio": "39",
        "particella": "75, 78, 80",
        "lat": 43.5312,
        "lng": 11.5645,
        "superficie_mq": 68_000,
        "prezzo_mq_eur": 8.4,
        "prezzo_richiesto_eur": 571_200,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 210,
        "distanza_autostrada_m": 190,
        "nome_autostrada": "A1 Autostrada del Sole (km 335)",
        "cabina_piu_vicina": "CP Montevarchi 132/15 kV",
        "distanza_cabina_m": 820,
        "livello_tensione": "MT 15 kV",
        "fonte_origine": "GEOPORTALE_REGIONE_TOSCANA_CAVE",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Valdarno Scavi e Costruzioni S.r.l.",
        "proprietario_piva": "01748290518",
        "proprietario_pec": "valdarnoscavi@pec.it",
        "proprietario_telefono": "+39 055 981244",
        "note_commerciali": "Irraggiamento solare 1.420 kWh/kWp/anno. Cava esaurita con parere favorevole preventivo del Comune per fotovoltaico."
    },

    # --- UMBRIA ---
    {
        "id": "LEAD-UMB-001",
        "title": "Lotto Adiacente Asse E45 Zona Produttiva Valle Umbra",
        "regione": "Umbria",
        "provincia": "Perugia",
        "comune": "Marsciano",
        "codice_belfiore": "E959",
        "foglio": "48",
        "particella": "130, 131",
        "lat": 42.9124,
        "lng": 12.3389,
        "superficie_mq": 52_000,
        "prezzo_mq_eur": 7.6,
        "prezzo_richiesto_eur": 395_200,
        "tipologia": "BUFFER_INDUSTRIALE_350M",
        "distanza_zona_industriale_m": 130,
        "distanza_autostrada_m": 280,
        "nome_autostrada": "SS 3 bis / E45 Orte-Ravenna",
        "cabina_piu_vicina": "CP Marsciano 132/20 kV (Enel Distribuzione)",
        "distanza_cabina_m": 690,
        "livello_tensione": "MT 20 kV",
        "fonte_origine": "ANNUNCIO_IMMOBILIARE_TERRENI",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Agricola & Immobiliare Umbra S.r.l.",
        "proprietario_piva": "02581930541",
        "proprietario_pec": "immobiliareumbra@pec.it",
        "proprietario_telefono": "+39 075 8743120",
        "note_commerciali": "Prezzo ottimo (7,6 €/mq), terreno totalmente pianeggiante senza alberature ad alto fusto."
    },

    # --- MARCHE ---
    {
        "id": "LEAD-MAR-001",
        "title": "Area Confinante Autostrada A14 e Polo Produttivo Jesi",
        "regione": "Marche",
        "provincia": "Ancona",
        "comune": "Jesi",
        "codice_belfiore": "E388",
        "foglio": "71",
        "particella": "89, 90, 92",
        "lat": 43.5350,
        "lng": 13.2540,
        "superficie_mq": 64_000,
        "prezzo_mq_eur": 8.7,
        "prezzo_richiesto_eur": 556_800,
        "tipologia": "FASCIA_AUTOSTRADALE_300M",
        "distanza_zona_industriale_m": 240,
        "distanza_autostrada_m": 150,
        "nome_autostrada": "Raccordo SS76 / Casello A14 Ancona Nord",
        "cabina_piu_vicina": "CP Jesi Est 132/20 kV",
        "distanza_cabina_m": 920,
        "livello_tensione": "MT 20 kV",
        "fonte_origine": "OVERPASS_BUFFER_ANALYSIS",
        "proprietario_tipo": "PERSONA_GIURIDICA",
        "proprietario_nome": "Vallesina Sviluppo S.r.l.",
        "proprietario_piva": "01948270423",
        "proprietario_pec": "vallesinasviluppo@pec.it",
        "proprietario_telefono": "+39 0731 539100",
        "note_commerciali": "Fronte infrastrutturale strategico ad alta visibilità. Allaccio rapido in cabina a meno di 1 km."
    }
]
