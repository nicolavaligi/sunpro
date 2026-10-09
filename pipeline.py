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
Pipeline di elaborazione e sincronizzazione Lead per Terreni Fotovoltaici.
Gestisce l'ingestione, l'enrichment, lo scoring e il salvataggio su SQLite.
Autore & Titolare IP: Nicola Valigi (Houdinick)
"""

from typing import Dict, Any, List
from data.storage import init_db, upsert_lead, get_all_leads
from crawler.spatial_engine import (
    CURATED_SOLAR_OPPORTUNITIES,
    calculate_energy_and_capex
)
from crawler.owner_discovery import enrich_owner_profile
from crawler.cadastral_resolver import estimate_belfiore
from scoring.scorer import calculate_site_score

def process_and_save_lead(raw_lead: Dict[str, Any]) -> Dict[str, Any]:
    """Elabora un lead calcolando parametri energetici, catastali, contatti e scoring."""
    lead = dict(raw_lead)

    # 1. Integrazione codice Belfiore catastale
    if not lead.get("codice_belfiore"):
        lead["codice_belfiore"] = estimate_belfiore(lead.get("comune", ""))

    # 2. Calcolo energetico e CAPEX
    superficie_mq = float(lead["superficie_mq"])
    dist_cabina = float(lead.get("distanza_cabina_m", 1500))
    regione = lead.get("regione", "Lombardia")

    mwp, mwh, capex = calculate_energy_and_capex(superficie_mq, dist_cabina, regione)
    lead["mwp_stimati"] = mwp
    lead["produzione_mwh_anno"] = mwh
    lead["capex_allaccio_eur"] = capex
    lead["superficie_ha"] = round(superficie_mq / 10_000, 2)

    # 3. Prezzo al mq
    prezzo_tot = lead.get("prezzo_richiesto_eur", 0)
    prezzo_mq = lead.get("prezzo_mq_eur")
    if not prezzo_mq and prezzo_tot:
        lead["prezzo_mq_eur"] = round(prezzo_tot / superficie_mq, 2)
    elif not prezzo_tot and prezzo_mq:
        lead["prezzo_richiesto_eur"] = round(prezzo_mq * superficie_mq, 0)

    # 4. Scoring Multicriterio
    score_tot, score_det, classe = calculate_site_score(lead)
    lead["score_totale"] = score_tot
    lead["score_dettagli"] = score_det
    lead["rating_classe"] = classe

    # 5. Arricchimento dati proprietario
    owner_info = enrich_owner_profile(lead)
    lead.update(owner_info)

    # 6. Salvataggio su database
    upsert_lead(lead)
    return lead

def sync_all_curated_leads() -> List[Dict[str, Any]]:
    """Inizializza il database e sincronizza tutti i lead qualificati curati."""
    init_db()
    processed = []
    for raw in CURATED_SOLAR_OPPORTUNITIES:
        lead = process_and_save_lead(raw)
        processed.append(lead)
    return processed

if __name__ == "__main__":
    print("Inizializzazione database e sincronizzazione lead...")
    leads = sync_all_curated_leads()
    print(f"Sincronizzati con successo {len(leads)} lead qualificati nel database SQLite.")
