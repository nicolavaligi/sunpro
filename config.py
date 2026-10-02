"""
Configurazione centrale per Solar Land Acquisition Crawler & Desktop App.
Parametri tecnici, normativi (D.Lgs. 199/2021) e modelli economici per il mercato italiano.
Autore: Houdinick (Nicola Valigi)
"""

from pathlib import Path

# Percorsi base
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
DB_PATH = DATA_DIR / "solar_land_leads.db"

# Creazione cartelle
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# CRITERI TECNICI DI QUALIFICAZIONE (D.Lgs. 199/2021 & Requisiti)
# -------------------------------------------------------------
MIN_SURFACE_MQ = 20_000          # Minimo 2 ettari (20.000 mq)
MAX_SURFACE_MQ = 1_500_000       # Fino a 150 ettari (utility-scale)

# Valutazione economica acquisto e diritto di superficie
TARGET_PRICE_MIN_EUR = 7.0       # €/mq minimo benchmark
TARGET_PRICE_TARGET_EUR = 8.5    # €/mq target (8-9 €/mq)
TARGET_PRICE_MAX_EUR = 9.5       # €/mq massimo ammissibile
ANNUAL_LEASE_PER_HA_EUR = 3_000  # Stima canone annuo diritto di superficie (€/ha/anno)

# Buffer idoneità normativa ex lege (D.Lgs. 199/2021 art. 20)
BUFFER_INDUSTRIAL_M = 350        # Entro 350 metri da zone industriali/artigianali
BUFFER_HIGHWAY_M = 300           # Entro 300 metri da autostrade e raccordi
BUFFER_SUBSTATION_OPTIMAL_M = 1200 # Distanza ottimale cabina primaria (< 1,2 km)
BUFFER_SUBSTATION_MAX_M = 3500   # Distanza massima per allaccio MT economicamente sostenibile

# -------------------------------------------------------------
# REGIONI PRIORITARIE (Nord e Centro Italia)
# -------------------------------------------------------------
PRIORITY_REGIONS = {
    "Lombardia": {
        "macro": "Nord",
        "insolazione_kwh_kwp": 1280,
        "favorabilita_normativa": 0.88,
        "note": "Attuazione LR per aree idonee con forte spinta su ex cave e cave dismesse"
    },
    "Veneto": {
        "macro": "Nord",
        "insolazione_kwh_kwp": 1300,
        "favorabilita_normativa": 0.84,
        "note": "Ottima idoneità su adiacenze autostradali (A4, A31) e Z.I."
    },
    "Emilia-Romagna": {
        "macro": "Nord",
        "insolazione_kwh_kwp": 1350,
        "favorabilita_normativa": 0.92,
        "note": "Regione all'avanguardia su agrivoltaico e recupero aree produttive/discariche"
    },
    "Piemonte": {
        "macro": "Nord",
        "insolazione_kwh_kwp": 1310,
        "favorabilita_normativa": 0.86,
        "note": "Aree risicole marginali, corridoi autostradali A4/A21 e brownfield industriali"
    },
    "Toscana": {
        "macro": "Centro",
        "insolazione_kwh_kwp": 1420,
        "favorabilita_normativa": 0.85,
        "note": "Ottimo irraggiamento; priorità cave dismesse, discariche e fasce industriali"
    },
    "Umbria": {
        "macro": "Centro",
        "insolazione_kwh_kwp": 1410,
        "favorabilita_normativa": 0.87,
        "note": "Focus su bacini estrattivi e adiacenze E45 / zone industriali pianeggianti"
    },
    "Marche": {
        "macro": "Centro",
        "insolazione_kwh_kwp": 1390,
        "favorabilita_normativa": 0.85,
        "note": "Fascia litoranea A14 e valli industriali pianeggianti"
    }
}

# -------------------------------------------------------------
# PARAMETRI IMPIANTISTICI ED ENERGETICI
# -------------------------------------------------------------
SURFACE_PER_MWP_MQ = 12_000      # ~1,2 ettari per 1 MWp installato (strutture fisse o tracker)
PERFORMANCE_RATIO = 0.82         # Efficienza standard BOS (Balance of System)
CABLE_COST_PER_KM = 65_000       # Costo medio cavidotto interrato MT per km (€/km)
SUBSTATION_BAY_COST = 45_000     # Costo stallo e adeguamento cabina primaria (€)

# -------------------------------------------------------------
# STATI COMMERCIALE DEL LEAD
# -------------------------------------------------------------
LEAD_STATUSES = [
    "DA_CONTATTARE",
    "IN_CONTATTO",
    "IN_TRATTATIVA",
    "OPZIONATO",
    "SCARTATO"
]

# -------------------------------------------------------------
# PESI SCORING MULTICRITERIO (Totale 100 pt)
# -------------------------------------------------------------
WEIGHTS = {
    "idoneita_normativa": 30,    # Presenza in aree idonee ex lege (cave, 350m Z.I., 300m autostrada)
    "prossimita_rete": 25,       # Vicinanza a cabina primaria AT/MT
    "convenienza_prezzo": 20,    # Aderenza al target 8-9 €/mq
    "resa_solare": 15,           # Irraggiamento medio annuo e superficie
    "reperibilita_proprieta": 10 # Contatti diretti, persona giuridica, telefono/PEC
}
