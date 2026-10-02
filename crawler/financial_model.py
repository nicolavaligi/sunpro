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

from data.storage import get_all_leads

# Parametri standard Utility-Scale Italia 2026
COST_PER_MWP_EUR = 680_000.0        # CAPEX EPC impianto ground-mounted utility-scale (€/MWp)
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
        capex_allaccio = float(l.get("capex_allaccio_eur", 0))

        # Calcolo CAPEX Impianto Totale
        capex_epc_impianto = mwp * COST_PER_MWP_EUR
        capex_totale_sviluppo = capex_epc_impianto + capex_allaccio + (acquisto_terreno * 0.1) # 10% soft costs

        # Ricavi & Opex
        ricavi_annui_energia = mwh * ENERGY_PRICE_CAPTURE_EUR_MWH
        opex_annuo_om = mwp * OPEX_PER_MWP_YEAR_EUR
        ebitda_annuo_acquisto = ricavi_annui_energia - opex_annuo_om
        ebitda_annuo_diritto_sup = ricavi_annui_energia - opex_annuo_om - canone_annuo_affitto

        # Simple Payback (Anni)
        payback_anni = round(capex_totale_sviluppo / max(1.0, ebitda_annuo_acquisto), 1)

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
            "Produzione Annua (MWh)": int(mwh),
            "Cabina Primaria": cabina,
            "Distanza Cabina (m)": int(dist_cabina),
            "CAPEX Allaccio MT (€)": int(capex_allaccio),
            "CAPEX EPC Impianto (€)": int(capex_epc_impianto),
            "CAPEX Totale Progetto (€)": int(capex_totale_sviluppo),
            "Valore Acquisto Terreno (€)": int(acquisto_terreno),
            "Prezzo Unitario (€/mq)": price_mq,
            "Canone Annuo Diritto Sup. (€/anno)": int(canone_annuo_affitto),
            "Totale Canone 30 Anni (€)": int(canone_30anni),
            "Ricavo Annuo Energia (€)": int(ricavi_annui_energia),
            "EBITDA Annuo con Acquisto (€)": int(ebitda_annuo_acquisto),
            "EBITDA Annuo con Diritto Sup. (€)": int(ebitda_annuo_diritto_sup),
            "Payback Stimato (Anni)": payback_anni,
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
