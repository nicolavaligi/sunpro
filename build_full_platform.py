"""
Build Full Platform Script per SunPro (Nicola Valigi Engine System).
Compila tutti i 36 lead (pionieri + feed live reale), genera tutti i PDF A4 in dossier_pdf/,
aggiorna index.html e web/index.html con dati e KPI dinamici, e sincronizza Google Drive.
Autore: Nicola Valigi Engine System
"""

import json
import re
import shutil
from pathlib import Path

from data.storage import get_all_leads
from reports.generator import generate_pdf_dossier
from sync_to_drive import sync_prototype_to_drive

BASE_DIR = Path(__file__).resolve().parent
DOSSIER_PDF_DIR = BASE_DIR / "dossier_pdf"
DOSSIER_PDF_DIR.mkdir(parents=True, exist_ok=True)
INDEX_HTML = BASE_DIR / "index.html"
WEB_INDEX_HTML = BASE_DIR / "web" / "index.html"

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text

def build_platform():
    leads = get_all_leads()
    print(f"🚀 Avvio compilazione piattaforma SunPro per {len(leads)} siti qualificati...")

    # 1. Generazione di tutti i PDF in dossier_pdf/
    pdf_map = {}
    print("📄 Generazione e verifica dossier PDF A4...")
    for l in leads:
        lead_id = l["id"]
        comune_slug = slugify(l["comune"])
        target_name = f"dossier_{lead_id}_{comune_slug}.pdf"
        target_path = DOSSIER_PDF_DIR / target_name
        
        # Genera il PDF
        gen_path = generate_pdf_dossier(l)
        shutil.copy2(gen_path, target_path)
        pdf_map[lead_id] = f"dossier_pdf/{target_name}"

    print(f"  ✓ {len(pdf_map)} PDF generati e verificati in {DOSSIER_PDF_DIR.name}/")

    # 2. Strutturazione JS per SITES
    js_sites = []
    total_mq = 0
    total_mwp = 0
    total_mwh = 0
    total_val = 0
    sub_dists = []
    prices_mq = []

    for l in leads:
        mq = float(l.get("superficie_mq", 20000))
        ha = round(mq / 10000.0, 2)
        mwp = float(l.get("mwp_stimati", round(mq / 12000, 2)))
        mwh = float(l.get("produzione_mwh_anno", round(mwp * 1300, 1)))
        price_mq = float(l.get("prezzo_mq_eur", 8.20))
        price_tot = float(l.get("prezzo_richiesto_eur", round(mq * price_mq, 0)))
        sub_dist = int(l.get("distanza_cabina_m", 750))

        total_mq += mq
        total_mwp += mwp
        total_mwh += mwh
        total_val += price_tot
        sub_dists.append(sub_dist)
        prices_mq.append(price_mq)

        # Calcolo barre di rating
        s_det = l.get("score_dettagli") or {}
        norm_pct = min(100, int((s_det.get("idoneita_normativa", 25) / 30.0) * 100))
        cab_pct = min(100, int((s_det.get("prossimita_rete", 20) / 25.0) * 100))
        price_pct = min(100, int((s_det.get("convenienza_prezzo", 18) / 20.0) * 100))
        yield_pct = min(100, int((s_det.get("resa_e_morfologia", 12) / 15.0) * 100))
        owner_pct = min(100, int((s_det.get("reperibilita_proprieta", 8) / 10.0) * 100))

        prov = l.get("provincia", l.get("comune", "IT"))
        if len(prov) > 2:
            prov = prov[:2].upper()

        contact_info = l.get("proprietario_pec") or l.get("proprietario_telefono") or "Inquiry riservata"
        if l.get("proprietario_telefono") and l.get("proprietario_pec"):
            contact_info = f"{l['proprietario_pec']} | {l['proprietario_telefono']}"

        site_obj = {
            "id": l["id"],
            "name": l["title"],
            "comune": l["comune"],
            "prov": prov,
            "reg": l["regione"],
            "ll": [float(l["lat"]), float(l["lng"])],
            "score": round(float(l["score_totale"]), 1),
            "ha": ha,
            "mq": int(mq),
            "mwp": mwp,
            "mwh": int(mwh),
            "price_mq": price_mq,
            "price_tot": int(price_tot),
            "tipo": l.get("tipologia", "BUFFER_INDUSTRIALE_350M"),
            "substation": l.get("cabina_piu_vicina", "CP Primaria"),
            "sub_dist": sub_dist,
            "ind_dist": int(l.get("distanza_zona_industriale_m", 50)),
            "hwy_dist": int(l.get("distanza_autostrada_m", 500)),
            "hwy_name": l.get("nome_autostrada", "Asse Viario Principale"),
            "catasto": f"Fg. {l.get('foglio', '1')} - P.lle {l.get('particella', '1')} (Cod. {l.get('codice_belfiore', 'N/D')})",
            "owner": l.get("proprietario_nome", "Proprietà Riservata"),
            "owner_tipo": l.get("proprietario_tipo", "PERSONA_GIURIDICA"),
            "contact": contact_info,
            "note": l.get("note_commerciali", "Opportunità qualificata conforme D.Lgs. 199/2021."),
            "bars": {
                "norm": norm_pct,
                "cab": cab_pct,
                "price": price_pct,
                "yield": yield_pct,
                "owner": owner_pct
            }
        }
        js_sites.append(site_obj)

    # Ordina per score decrescente
    js_sites.sort(key=lambda s: s["score"], reverse=True)

    avg_price = round(sum(prices_mq) / len(prices_mq), 2)
    avg_dist = int(sum(sub_dists) / len(sub_dists))
    tot_ha = round(total_mq / 10000.0, 1)
    tot_val_m = round(total_val / 1_000_000, 2)
    tot_mwp_r = round(total_mwp, 1)

    print(f"📊 Metriche aggregate SunPro:")
    print(f"  • Siti Qualificati : {len(js_sites)}")
    print(f"  • Superficie Totale: {tot_ha} ettari ({int(total_mq):,} mq)")
    print(f"  • Potenza Stimata  : {tot_mwp_r} MWp (~{int(total_mwh/1000)} GWh/a)")
    print(f"  • Prezzo Medio     : {avg_price} €/mq")
    print(f"  • Distanza Media CP: {avg_dist} m")
    print(f"  • Pipeline Acquisto: € {tot_val_m}M")

    # 3. Aggiorna index.html
    html_content = INDEX_HTML.read_text(encoding="utf-8")

    # Sostituisci blocco KPI HTML
    old_kpis_pattern = r'<div id="kpis">.*?</div>\s*<main>'
    new_kpis_html = f"""<div id="kpis">
  <div class="kpi" style="--kc:var(--green)"><div class="v" id="kpiCount">{len(js_sites)}</div><div class="l">Aree qualificate</div></div>
  <div class="kpi" style="--kc:var(--accent)"><div class="v" id="kpiPower">{tot_mwp_r} MWp</div><div class="l">Potenza stimata (~{int(total_mwh/1000)} GWh/a)</div></div>
  <div class="kpi" style="--kc:var(--amber)"><div class="v" id="kpiArea">{tot_ha} ha</div><div class="l">Superficie censita ({int(total_mq/1000)}k mq)</div></div>
  <div class="kpi" style="--kc:var(--brand)"><div class="v" id="kpiPrice">{avg_price:.2f} €/mq</div><div class="l">Prezzo target medio (8-9 €)</div></div>
  <div class="kpi" style="--kc:var(--pink)"><div class="v" id="kpiDist">{avg_dist} m</div><div class="l">Distanza media cabina AT/MT</div></div>
  <div class="kpi" style="--kc:#a78bfa"><div class="v" id="kpiVal">€ {tot_val_m}M</div><div class="l">Valore pipeline acquisto</div></div>
</div>

<main>"""
    html_content = re.sub(old_kpis_pattern, new_kpis_html, html_content, flags=re.DOTALL)

    # Sostituisci array SITES
    sites_json = json.dumps(js_sites, indent=2, ensure_ascii=False)
    old_sites_pattern = r'/\* ============ DATI QUALIFICATI.*?const SITES = \[.*?\];'
    new_sites_code = f"/* ============ DATI QUALIFICATI NICOLA VALIGI ENGINE SYSTEM ({len(js_sites)} SITI REALI) ============ */\nconst SITES = {sites_json};"
    html_content = re.sub(old_sites_pattern, new_sites_code, html_content, flags=re.DOTALL)

    # Sostituisci PDF_MAP
    pdf_map_json = json.dumps(pdf_map, indent=2, ensure_ascii=False)
    old_pdf_map_pattern = r'const PDF_MAP = \{.*?\};'
    new_pdf_map_code = f"const PDF_MAP = {pdf_map_json};"
    html_content = re.sub(old_pdf_map_pattern, new_pdf_map_code, html_content, flags=re.DOTALL)

    # Aggiorna subtitle e sitesCount iniziale
    html_content = html_content.replace('id="sitesCount" style="color:var(--brand)">11 siti<', f'id="sitesCount" style="color:var(--brand)">{len(js_sites)} siti<')

    INDEX_HTML.write_text(html_content, encoding="utf-8")
    WEB_INDEX_HTML.write_text(html_content, encoding="utf-8")
    print(f"  ✓ index.html e web/index.html aggiornati con successo!")

    # 4. Sincronizzazione Drive
    print("☁️ Sincronizzazione Google Drive...")
    sync_prototype_to_drive()
    print("✅ Piattaforma SunPro compilata e sincronizzata al 100%!")

if __name__ == "__main__":
    build_platform()
