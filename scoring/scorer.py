"""
Motore di Scoring Multicriterio (0-100) per Terreni e Siti Fotovoltaici.
Calibrazione sui criteri specificati: Aree idonee (D.Lgs 199/2021), 350m Z.I., 300m Autostrade,
Ex-cave/discariche, vicinanza cabina AT/MT, target prezzo 8-9 €/mq, reperibilità proprietà.
Autore: Houdinick (Nicola Valigi)
"""

from typing import Any, Dict, Tuple
from config import PRIORITY_REGIONS, WEIGHTS

def calculate_site_score(lead: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
    """
    Calcola il punteggio di idoneità totale (0-100) e i punteggi parziali.
    Restituisce: (score_totale, dettagli_score, classe_rating)
    """
    # 1. Idoneità Normativa D.Lgs. 199/2021 (max 30 pt)
    tipologia = lead.get("tipologia", "")
    dist_ind = lead.get("distanza_zona_industriale_m", 9999)
    dist_auto = lead.get("distanza_autostrada_m", 9999)

    score_normativo = 0.0
    if "CAVA" in tipologia or "DISCARICA" in tipologia or "BROWNFIELD" in tipologia:
        score_normativo = 30.0
    elif dist_ind <= 350:
        score_normativo = 26.0
    elif dist_auto <= 300:
        score_normativo = 22.0
    elif dist_ind <= 500 or dist_auto <= 500:
        score_normativo = 14.0
    else:
        score_normativo = 6.0

    # 2. Prossimità Cabina AT/MT (max 25 pt)
    dist_cabina = lead.get("distanza_cabina_m", 9999)
    score_rete = 0.0
    if dist_cabina <= 500:
        score_rete = 25.0
    elif dist_cabina <= 1000:
        score_rete = 21.0
    elif dist_cabina <= 1500:
        score_rete = 16.0
    elif dist_cabina <= 2500:
        score_rete = 11.0
    elif dist_cabina <= 3500:
        score_rete = 6.0
    else:
        score_rete = 2.0

    # 3. Convenienza Economica Prezzo (max 20 pt) - Target 8-9 €/mq
    prezzo_mq = lead.get("prezzo_mq_eur", 8.5)
    score_prezzo = 0.0
    if prezzo_mq <= 7.5:
        score_prezzo = 20.0  # Ottimo affare sotto benchmark
    elif 7.5 < prezzo_mq <= 9.0:
        score_prezzo = 18.0  # Nel pieno del target 8-9 €/mq
    elif 9.0 < prezzo_mq <= 10.0:
        score_prezzo = 11.0
    elif 10.0 < prezzo_mq <= 12.0:
        score_prezzo = 5.0
    else:
        score_prezzo = 1.0

    # 4. Resa Solare, Dimensione & Morfologia (max 15 pt)
    regione = lead.get("regione", "Lombardia")
    reg_info = PRIORITY_REGIONS.get(regione, {"insolazione_kwh_kwp": 1300})
    insolazione = reg_info.get("insolazione_kwh_kwp", 1300)
    
    # Normalizzazione insolazione: 1200->6pt, 1450->10pt
    score_insolazione = min(10.0, max(5.0, (insolazione - 1200) / 25.0 + 5.0))

    # Bonus superficie (minimo 2 ha = 20.000 mq)
    mq = lead.get("superficie_mq", 20000)
    if mq >= 100_000:
        score_dimensione = 5.0
    elif mq >= 50_000:
        score_dimensione = 4.0
    elif mq >= 20_000:
        score_dimensione = 3.0
    else:
        score_dimensione = 0.0

    score_resa = min(15.0, score_insolazione + score_dimensione)

    # 5. Reperibilità Proprietà & Dati Contatto (max 10 pt)
    prop_tipo = lead.get("proprietario_tipo", "")
    prop_pec = lead.get("proprietario_pec", "")
    prop_tel = lead.get("proprietario_telefono", "")

    score_proprietario = 0.0
    if prop_pec and prop_tel:
        score_proprietario = 10.0
    elif prop_pec or prop_tel:
        score_proprietario = 8.0
    elif prop_tipo in ["PERSONA_GIURIDICA", "CURATELA_FALLIMENTARE"]:
        score_proprietario = 7.0
    elif lead.get("particella"):
        score_proprietario = 4.0
    else:
        score_proprietario = 2.0

    # Punteggio complessivo (0-100)
    totale = round(score_normativo + score_rete + score_prezzo + score_resa + score_proprietario, 1)
    totale = min(100.0, max(0.0, totale))

    # Classe di rating commerciale
    if totale >= 75.0:
        classe = "TOP OPPORTUNITÀ"
    elif totale >= 60.0:
        classe = "QUALIFICATO"
    else:
        classe = "SECONDARIO"

    dettagli = {
        "idoneita_normativa": round(score_normativo, 1),
        "prossimita_rete": round(score_rete, 1),
        "convenienza_prezzo": round(score_prezzo, 1),
        "resa_e_morfologia": round(score_resa, 1),
        "reperibilita_proprieta": round(score_proprietario, 1)
    }

    return totale, dettagli, classe
