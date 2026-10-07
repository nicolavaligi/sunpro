"""
Financial & Investment Model Exporter per SunPro (Nicola Valigi Engine System).
Genera il modello economico esecutivo completo per sviluppatori, EPC e fondi di investimento:
- CAPEX impianto (€/MWp) e allaccio rete
- OPEX stimato e canone diritto di superficie trentennale
- Ricavi annui vendita energia e producibilità PVGIS
- LCOE e metriche finanziarie per ogni singolo terreno censito
Autore: Nicola Valigi Engine System
"""

import csv
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from config import DETOUR_FACTOR_GRID, TRACKER_CAPEX_EXTRA_PER_MWP, TRACKER_BOOST_DEFAULT_PCT
from data.storage import get_all_leads

# Parametri standard Utility-Scale Italia 2026
COST_PER_MWP_EUR = 680_000.0        # CAPEX EPC impianto ground-mounted fisso (€/MWp)
ENERGY_PRICE_CAPTURE_EUR_MWH = 85.0  # Prezzo vendita energia PPA / mercato zonale (€/MWh)
OPEX_PER_MWP_YEAR_EUR = 14_000.0     # O&M, assicurazione, sicurezza, monitoraggio (€/MWp/anno)
DISCOUNT_RATE = 0.065                # WACC per LCOE

def generate_financial_model_csv(output_path: Path) -> Path:
    leads = get_all_leads()
    rows = []

    for l in leads:
        lead_id = l["id"]
        title = l["title"]
        comune = l.get("comune", "")
        prov = l.get("provincia", "")
        reg = l.get("regione", "")
        tipo = l.get("tipologia", "AREA_IDONEA")
        
        ha = float(l.get("superficie_ha", 0))
        mq = float(l.get("superficie_mq", 0))
        mwp = float(l.get("mwp_stimati", 0))
        mwh = float(l.get("produzione_mwh_anno", 0))

        price_mq = float(l.get("prezzo_mq_eur", 8.20))
        acquisto_terreno = float(l.get("prezzo_richiesto_eur", mq * price_mq))
        canone_annuo_affitto = ha * 3000.0
        canone_30anni = canone_annuo_affitto * 30.0

        cabina = l.get("cabina_piu_vicina", "")
        dist_cabina = float(l.get("distanza_cabina_m", 0))
        dist_stradale = int(dist_cabina * DETOUR_FACTOR_GRID)
        capex_allaccio = float(l.get("capex_allaccio_eur", 0))

        # Calcolo CAPEX Impianto Fissa vs Tracker
        capex_epc_impianto = mwp * COST_PER_MWP_EUR
        capex_totale_sviluppo = capex_epc_impianto + capex_allaccio + (acquisto_terreno * 0.1) # 10% soft costs

        # Tracker Monoassiale asse N-S (+20% resa, +70k €/MWp CAPEX)
        boost_pct = float(l.get("boost_tracker_pct", TRACKER_BOOST_DEFAULT_PCT))
        mwh_tracker = round(mwh * (1.0 + (boost_pct / 100.0)), 1)
        capex_epc_tracker = mwp * (COST_PER_MWP_EUR + TRACKER_CAPEX_EXTRA_PER_MWP)
        capex_totale_tracker = capex_epc_tracker + capex_allaccio + (acquisto_terreno * 0.1)

        # Ricavi & Opex
        ricavi_annui_energia = mwh * ENERGY_PRICE_CAPTURE_EUR_MWH
        ricavi_annui_tracker = mwh_tracker * ENERGY_PRICE_CAPTURE_EUR_MWH
        extra_ricavo_tracker = ricavi_annui_tracker - ricavi_annui_energia

        opex_annuo_om = mwp * OPEX_PER_MWP_YEAR_EUR
        ebitda_annuo_acquisto = ricavi_annui_energia - opex_annuo_om
        ebitda_annuo_diritto_sup = ricavi_annui_energia - opex_annuo_om - canone_annuo_affitto

        ebitda_annuo_tracker = ricavi_annui_tracker - (mwp * (OPEX_PER_MWP_YEAR_EUR + 2000.0))

        # Simple Payback (Anni)
        payback_anni = round(capex_totale_sviluppo / max(1.0, ebitda_annuo_acquisto), 1)
        payback_tracker = round(capex_totale_tracker / max(1.0, ebitda_annuo_tracker), 1)

        rows.append({
            "ID Lead": lead_id,
            "Denominazione": title,
            "Comune": comune,
            "Provincia": prov,
            "Regione": reg,
            "Tipologia D.Lgs. 199/21": tipo,
            "Superficie (ha)": ha,
            "Superficie (mq)": int(mq),
            "Potenza FV (MWp)": mwp,
            "Produzione Annua Fissa (MWh)": int(mwh),
            "Produzione Annua Tracker (MWh)": int(mwh_tracker),
            "Boost Tracker (%)": round(boost_pct, 1),
            "Cabina Primaria": cabina,
            "Distanza Linea Aria (m)": int(dist_cabina),
            "Distanza Stradale Cavidotto (m)": dist_stradale,
            "CAPEX Allaccio MT Reale (€)": int(capex_allaccio),
            "CAPEX EPC Fisso (€)": int(capex_epc_impianto),
            "CAPEX EPC Tracker (€)": int(capex_epc_tracker),
            "CAPEX Totale Progetto Fisso (€)": int(capex_totale_sviluppo),
            "CAPEX Totale Progetto Tracker (€)": int(capex_totale_tracker),
            "Valore Acquisto Terreno (€)": int(acquisto_terreno),
            "Prezzo Unitario (€/mq)": price_mq,
            "Canone Annuo Diritto Sup. (€/anno)": int(canone_annuo_affitto),
            "Totale Canone 30 Anni (€)": int(canone_30anni),
            "Ricavo Annuo Energia Fisso (€)": int(ricavi_annui_energia),
            "Ricavo Annuo Energia Tracker (€)": int(ricavi_annui_tracker),
            "Extra Ricavo Annuo Tracker (€)": int(extra_ricavo_tracker),
            "EBITDA Annuo Acquisto Fisso (€)": int(ebitda_annuo_acquisto),
            "EBITDA Annuo Diritto Sup. Fisso (€)": int(ebitda_annuo_diritto_sup),
            "EBITDA Annuo Acquisto Tracker (€)": int(ebitda_annuo_tracker),
            "Payback Fisso (Anni)": payback_anni,
            "Payback Tracker (Anni)": payback_tracker,
            "Score SunPro (0-100)": l.get("score_totale"),
            "Classe Rating": l.get("rating_classe"),
            "Proprietario": l.get("proprietario_nome"),
            "Contatto / PEC": l.get("proprietario_pec") or l.get("proprietario_telefono")
        })

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path

if __name__ == "__main__":
    p = Path("SunPro_Executive_Financial_Model.csv")
    generate_financial_model_csv(p)
    print(f"✓ Modello Finanziario generato: {p}")
