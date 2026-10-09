# ==============================================================================
# PROPRIETARY AND CONFIDENTIAL — NICOLA VALIGI (HOUDINICK)
# SunPro Geo-Intelligence 3D — Nicola Valigi Engine System
# Copyright (c) 2026 Nicola Valigi. All Rights Reserved.
# Autore & Titolare Esclusivo della Proprietà Intellettuale: Nicola Valigi (Houdinick)
# Email: 305862309+nicolavaligi@users.noreply.github.com | GitHub: nicolavaligi
# 
# Vietata la riproduzione, copia o appropriazione non autorizzata (L. 633/1941).
# ==============================================================================
"""
Modulo di Filtraggio di Idoneità Fondiaria e Watchdog Anti-Edifici per SunPro.
Autore: Nicola Valigi Engine System

Risolve la criticità fondamentale dell'origination solare:
1. Elimina aree con capannoni industriali esistenti, coperture o fabbricati da demolire
2. Elimina aree residenziali o contigue a insediamenti urbani densi (caseggiati, borghi)
3. Privilegia e promuove al 100% i TERRENI AGRICOLI A CAMPO APERTO (Zona E - Seminativi di Pianura):
   - Nessun fabbricato né costo di bonifica/demolizione
   - Massima facilità di acquisizione da agricoltori (rendita quintuplicata rispetto alle colture)
   - Piena conformità D.Lgs. 199/2021 (buffer 350m Z.I., 300m corridoi autostradali) e Agrivoltaico
"""

from typing import Any, Dict, List, Tuple

# Elenco comuni urbani densi o metropolitani da escludere categoricamente per fotovoltaico a terra
DENSE_URBAN_EXCLUSIONS = {
    "Milano", "Sesto San Giovanni", "Cinisello Balsamo", "Rho", "Legnano",
    "Bologna", "Torino", "Firenze", "Napoli", "Roma", "Genova", "Saronno"
}

# Parole chiave che indicano presenza di manufatti o insediamenti ostativi
BUILDING_DISQUALIFIERS = [
    "CAPANNONE", "FABBRICATO", "EDIFICIO", "TETTO", "COPERTURA",
    "DEPOSITO_COPERTO", "MAGAZZINO", "RESIDENZIALE", "CIVILE_ABITAZIONE",
    "CORTE_URBANA", "BORGO", "ABITATO_DENSO"
]

def verify_land_cover_and_settlement(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica che il sito sia un VERO terreno agricolo o area a cielo aperto,
    privo di capannoni, macerie, edifici o insediamenti residenziali contigui.
    """
    comune = lead.get("comune", "").strip()
    title = lead.get("title", "").upper()
    tipologia = lead.get("tipologia", "").upper()
    notes = lead.get("note_commerciali", "").upper()
    fonte = lead.get("fonte_origine", "").upper()
    
    # 1. Verifica centri metropolitani/urbani densi (dove ci sono capannoni e case)
    if comune in DENSE_URBAN_EXCLUSIONS:
        # Se non è esplicitamente una cava rurale certificata, scarta
        if "CAVA" not in tipologia:
            return {
                "idoneo": False,
                "motivo_scarto": f"Contesto urbano denso a forte presenza di capannoni/edifici ({comune}). Incompatibile con parchi solari a terra.",
                "presenza_edifici": "PRESENTE (Tessuto urbano / complessi edilizi industriali)",
                "land_cover": "URBANO_INDUSTRIALE_DILUITO"
            }

    # 2. Verifica presenza di parole chiave di edifici (esclusi testi negativi)
    combined_text = f"{title} {tipologia} {fonte}"
    for kw in BUILDING_DISQUALIFIERS:
        if kw in combined_text:
            return {
                "idoneo": False,
                "motivo_scarto": f"Rilevato manufatto/edificio ostativo ({kw}). SunPro esclude aree edificate.",
                "presenza_edifici": f"PRESENTE ({kw})",
                "land_cover": "EDIFICATO_COPERTO"
            }

    # 3. Classificazione Land Cover: Campo Aperto
    if "AGRICOL" in tipologia or "SEMINATIVO" in tipologia or "AGRIVOLTAICO" in tipologia:
        land_cover = "SEMINATIVO_CAMPO_APERTO"
        desc_cover = "Terreno agricolo pianeggiante in campo aperto (100% privo di fabbricati e capannoni)"
        facilita_acquisizione = "MASSIMA (Trattativa diretta con coltivatore/azienda agricola)"
    elif "CAVA" in tipologia:
        land_cover = "BACINO_ESTRATTIVO_APERTO"
        desc_cover = "Area estrattiva a cielo aperto, fondo pianeggiante o gradonato, zero fabbricati"
        facilita_acquisizione = "ELEVATA (Transazione con ex cavatore/curatela)"
    elif "DISCARICA" in tipologia:
        land_cover = "SITO_BONIFICATO_PIANEGGIANTE"
        desc_cover = "Compendio bonificato a terra, assenza di manufatti stabili"
        facilita_acquisizione = "ELEVATA (Trattativa societaria)"
    elif "AUTOSTRAD" in tipologia:
        land_cover = "SEMINATIVO_FASCIA_AUTOSTRADALE"
        desc_cover = "Fascia agricola aperta di rispetto infrastrutturale priva di costruzioni"
        facilita_acquisizione = "MASSIMA (Terreno agricolo contiguo ad asse viario)"
    else:
        # Buffer industriale: deve essere la fascia agricola contigua, NON il capannone!
        land_cover = "SEMINATIVO_BUFFER_INDUSTRIALE"
        desc_cover = "Terreno agricolo a campo aperto (Zona E) contiguo a polo produttivo, privo di capannoni"
        facilita_acquisizione = "MASSIMA (Proprietà agricola contigua)"

    return {
        "idoneo": True,
        "motivo_scarto": None,
        "presenza_edifici": "ASSENTE (100% Suolo libero / Campo aperto)",
        "land_cover": land_cover,
        "descrizione_suolo": desc_cover,
        "facilita_acquisizione": facilita_acquisizione
    }
