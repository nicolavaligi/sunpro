# ==============================================================================
# PROPRIETARY AND CONFIDENTIAL — NICOLA VALIGI (HOUDINICK)
# Generatore HTML per Mappa Dedicata Piacentino A1-A21 (piacentino.html)
# Autore & Titolare Esclusivo della Proprietà Intellettuale: Nicola Valigi (Houdinick)
# ==============================================================================

import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DATA_DIR = BASE_DIR / "data"


def build_piacentino_html():
    lots_path = DATA_DIR / "piacentino_enriched_lots.json"
    lots = json.loads(lots_path.read_text(encoding="utf-8"))
    lots_json = json.dumps(lots, ensure_ascii=False)

    # Statistiche iniziali su Aperta Campagna (90 lotti)
    aperta = [x for x in lots if x["gruppo"] == "APERTA_CAMPAGNA"]
    tot_ha = round(sum(x["sup_tot_ha"] for x in aperta), 1)
    tot_300_ha = round(sum(x["sup_300m_ha"] for x in aperta), 1)
    tot_mwp = round(sum(x["mwp_tot"] for x in aperta), 1)
    tot_mwp_300 = round(sum(x["mwp_300m"] for x in aperta), 1)
    tot_spesa_m = round(sum(x["spesa_max_8eur"] for x in aperta) / 1_000_000, 2)

    html = f"""<!-- =============================================================================
  PROPRIETARY & CONFIDENTIAL — SUNPRO GEO-INTELLIGENCE 3D · CLUSTER PIACENTINO A1-A21
  Autore & Titolare Esclusivo Proprietà Intellettuale: Nicola Valigi (Houdinick)
  Email: 305862309+nicolavaligi@users.noreply.github.com | GitHub: nicolavaligi
  Copyright (c) 2026 Nicola Valigi. All Rights Reserved.
============================================================================= -->
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cluster Piacentino A1 & A21 — Mappa Dedicata & Visure | SunPro Geo-Intelligence 3D</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/maplibre-gl.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/maplibre-gl/4.7.1/maplibre-gl.min.js"></script>
<style>
  :root{{
    --bg:#070c18; --panel:#0d1526; --panel2:#131d34;
    --border:#1c2942; --border2:#2c3d61;
    --txt:#eaf0fa; --muted:#8b9cb8;
    --accent:#38bdf8; --green:#34d399; --amber:#f59e0b; --red:#f87171;
    --brand:#10b981; --brand-dark:#059669; --blue:#2563eb; --pink:#f43f5e;
  }}
  *{{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',system-ui,-apple-system,sans-serif;font-variant-numeric:tabular-nums}}
  .mono{{font-family:'JetBrains Mono',monospace}}
  body{{background:var(--bg);color:var(--txt);height:100vh;display:flex;flex-direction:column;overflow:hidden}}
  svg.ic{{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none;vertical-align:-2px}}

  header{{height:58px;flex:none;padding:0 16px;background:linear-gradient(180deg,#0a1b24,var(--panel));border-bottom:1px solid var(--border2);display:flex;align-items:center;gap:10px;overflow-x:auto}}
  .logo{{width:36px;height:36px;display:flex;align-items:center;justify-content:center;flex:none;filter:drop-shadow(0 0 10px rgba(16,185,129,.45))}}
  header h1{{font-size:14.5px;font-weight:800;letter-spacing:-.3px;white-space:nowrap}}
  header h1 span{{background:linear-gradient(135deg,#38bdf8,#34d399);-webkit-background-clip:text;background-clip:text;color:transparent}}
  header .sub{{font-size:9.5px;letter-spacing:1.3px;text-transform:uppercase;color:var(--muted);font-weight:600;white-space:nowrap}}
  header .sp{{flex:1}}

  .nav-btn{{font-size:11px;font-weight:700;padding:6px 12px;border-radius:8px;text-decoration:none;display:inline-flex;align-items:center;gap:6px;white-space:nowrap;cursor:pointer;transition:all .15s;border:1px solid var(--border2);background:#142236;color:var(--txt)}}
  .nav-btn:hover{{border-color:var(--accent);transform:translateY(-1px)}}
  .nav-btn.primary{{background:linear-gradient(135deg,#059669,#10b981);color:#fff;border-color:#34d399}}
  .nav-btn.excel{{background:linear-gradient(135deg,#1e40af,#2563eb);color:#fff;border-color:#60a5fa}}

  .threshold-box{{display:flex;align-items:center;gap:6px;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.45);padding:4px 10px;border-radius:8px;white-space:nowrap}}
  .threshold-box label{{font-size:10px;font-weight:700;text-transform:uppercase;color:#fbbf24;letter-spacing:.6px}}
  .threshold-box input{{width:62px;background:#09111e;border:1px solid #f59e0b;color:#fde68a;font-family:'JetBrains Mono',monospace;font-weight:800;font-size:12.5px;padding:3px 6px;border-radius:5px;text-align:right;outline:none}}

  #kpis{{flex:none;display:grid;grid-template-columns:repeat(6,1fr);background:var(--panel);border-bottom:1px solid var(--border2)}}
  .kpi{{position:relative;padding:8px 14px 8px 17px;border-right:1px solid var(--border)}}
  .kpi:last-child{{border-right:none}}
  .kpi::after{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--kc,var(--accent))}}
  .kpi .v{{font-size:15.5px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--txt)}}
  .kpi .l{{font-size:9px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);font-weight:600;margin-top:2px}}

  main{{flex:1;display:flex;min-height:0}}
  #map{{flex:1;position:relative}}
  aside{{width:460px;flex:none;background:var(--panel);border-left:1px solid var(--border);overflow-y:auto;padding:14px}}
  aside::-webkit-scrollbar{{width:8px}}
  aside::-webkit-scrollbar-thumb{{background:#1c2942;border-radius:6px}}

  .lbl{{font-size:10.5px;letter-spacing:1.1px;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center}}

  #filters{{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:10px}}
  .pill{{font-size:10px;padding:4px 9px;border-radius:12px;background:#142236;border:1px solid var(--border);color:var(--muted);cursor:pointer;font-weight:600;transition:all .15s}}
  .pill:hover{{border-color:var(--brand);color:var(--txt)}}
  .pill.active{{background:rgba(16,185,129,.18);border-color:var(--brand);color:#34d399}}

  .controls-grid{{display:grid;grid-template-columns:1fr 1fr 1.2fr;gap:6px;margin-bottom:10px}}
  .controls-grid select{{background:#131f33;border:1px solid var(--border);color:var(--txt);font-size:11px;padding:6px 8px;border-radius:7px;outline:none;font-weight:600}}
  .controls-grid select:focus{{border-color:var(--brand)}}

  .search-box{{margin-bottom:10px;position:relative}}
  .search-box input{{width:100%;background:#131f33;border:1px solid var(--border);border-radius:8px;padding:7px 12px 7px 30px;color:var(--txt);font-size:11.5px;outline:none}}
  .search-box input:focus{{border-color:var(--brand)}}
  .search-box svg{{position:absolute;left:9px;top:8px;color:var(--muted);width:14px;height:14px}}

  .card{{background:linear-gradient(180deg,#131f38 0%,var(--panel2) 100%);border:1px solid var(--border);border-radius:10px;padding:12px 13px;margin-bottom:11px;transition:all .16s}}
  .card:hover{{border-color:var(--border2);transform:translateY(-1px);box-shadow:0 6px 16px rgba(0,0,0,.35)}}
  .card.sel{{border-color:var(--brand);box-shadow:0 0 0 1px var(--brand),0 6px 20px rgba(16,185,129,.22)}}
  .card.p1{{border-left:3px solid #38bdf8}}
  .card.p2{{border-left:3px solid #10b981}}
  .card.peri{{border-left:3px solid #f59e0b}}
  .card .row{{display:flex;justify-content:space-between;align-items:flex-start;cursor:pointer;gap:8px}}
  .card .name{{font-weight:800;font-size:13px;color:var(--txt)}}
  .card .subtag{{font-size:10.5px;color:var(--muted);margin-top:3px;display:flex;flex-wrap:wrap;gap:4px;align-items:center}}
  .score{{font-size:19px;font-weight:800;font-family:'JetBrains Mono',monospace;color:var(--green)}}

  .tag{{font-size:9px;font-weight:700;padding:1.5px 6px;border-radius:4px;text-transform:uppercase;letter-spacing:.4px}}
  .tag.p1{{background:rgba(37,99,235,.22);color:#93c5fd;border:1px solid #2563eb}}
  .tag.p2{{background:rgba(16,185,129,.16);color:#6ee7b7;border:1px solid #059669}}
  .tag.peri{{background:rgba(245,158,11,.18);color:#fcd34d;border:1px solid #d97706}}
  .tag.cohort{{background:rgba(148,163,184,.14);color:#cbd5e1;border:1px solid #334155}}

  .note{{font-size:10.5px;color:#cbd5e1;margin-top:6px;line-height:1.4;border-left:2px solid var(--accent);padding-left:8px;background:rgba(15,23,42,.4);padding:4px 8px;border-radius:0 5px 5px 0}}

  .dists{{margin-top:8px;border-top:1px dashed var(--border2);padding-top:7px;display:grid;gap:3.5px}}
  .d-row{{display:flex;justify-content:space-between;align-items:center;gap:6px;color:var(--muted);font-size:10.8px}}
  .d-row b{{color:var(--txt);font-weight:600;font-family:'JetBrains Mono',monospace;text-align:right}}

  .visura-box{{margin-top:8px;background:rgba(254,243,199,.06);border:1px solid rgba(245,158,11,.3);border-radius:7px;padding:7px 8px}}
  .visura-title{{font-size:9.5px;font-weight:700;text-transform:uppercase;color:#fbbf24;margin-bottom:5px;display:flex;justify-content:space-between;align-items:center}}
  .visura-inputs{{display:grid;grid-template-columns:1.5fr 1fr auto;gap:5px;align-items:center}}
  .visura-inputs input{{background:#09111e;border:1px solid var(--border2);color:#fff;font-size:10.5px;padding:4px 6px;border-radius:4px;outline:none;width:100%}}
  .visura-inputs input:focus{{border-color:#f59e0b}}
  .visura-status{{font-size:9.5px;font-weight:800;padding:3px 7px;border-radius:4px;white-space:nowrap;font-family:'JetBrains Mono',monospace}}
  .visura-status.ok{{background:rgba(16,185,129,.2);color:#34d399;border:1px solid #10b981}}
  .visura-status.no{{background:rgba(248,113,113,.2);color:#f87171;border:1px solid #ef4444}}
  .visura-status.wait{{background:rgba(148,163,184,.12);color:var(--muted);border:1px solid var(--border)}}

  .btns{{margin-top:8px;display:flex;gap:6px}}
  .btn{{flex:1;display:flex;align-items:center;justify-content:center;gap:5px;background:#182642;border:1px solid var(--border2);color:var(--txt);font-size:10.8px;padding:6px 7px;border-radius:6px;cursor:pointer;font-weight:600;text-decoration:none;transition:all .15s}}
  .btn:hover{{border-color:var(--accent);transform:translateY(-1px)}}
  .btn.brand{{background:linear-gradient(135deg,#059669,var(--brand));color:#fff;border-color:var(--brand)}}

  .info-panel{{background:linear-gradient(180deg,#1a1528 0%,#120f1d 100%);border:1px solid #4c2d5e;border-radius:10px;padding:12px;margin-top:12px;font-size:10.8px;color:#cbd5e1;line-height:1.5}}
  .info-panel h3{{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#f472b6;margin-bottom:6px}}
  .info-panel ul{{padding-left:15px;display:grid;gap:4px}}

  #tools{{position:absolute;top:12px;left:12px;z-index:10;display:flex;gap:7px;flex-wrap:wrap;max-width:calc(100% - 24px)}}
  .tool{{display:flex;align-items:center;gap:6px;background:rgba(13,21,38,.92);border:1px solid var(--border2);color:var(--txt);font-size:11px;font-weight:600;padding:6px 11px;border-radius:8px;cursor:pointer;backdrop-filter:blur(6px);transition:all .15s}}
  .tool:hover{{border-color:var(--brand)}}
  .tool.on{{border-color:var(--brand);color:#34d399;background:rgba(16,185,129,.14)}}

  #orbitHint{{position:absolute;top:58px;left:50%;transform:translateX(-50%);z-index:10;display:none;align-items:center;gap:7px;background:rgba(15,23,42,.94);border:1px solid var(--brand);color:var(--txt);font-size:11.5px;padding:7px 14px;border-radius:20px}}
  #siteTip{{position:absolute;left:14px;bottom:16px;z-index:11;width:min(460px,calc(100% - 28px));background:linear-gradient(180deg,#131f38,#0b1322);border:1px solid var(--brand);border-radius:12px;padding:13px 15px;box-shadow:0 14px 44px rgba(0,0,0,.75);display:none}}

  .map-pin-wrap{{width:34px;height:48px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:transform .2s,filter .2s;transform-origin:50% 100%;filter:drop-shadow(0 4px 7px rgba(0,0,0,.5))}}
  .map-pin-wrap svg{{width:100%;height:100%;overflow:visible}}
  .map-pin-wrap:hover,.map-pin-wrap.hovered{{transform:translateY(-6px) scale(1.18);z-index:9999 !important}}
  .map-pin-wrap.active{{transform:translateY(-8px) scale(1.26);z-index:10000 !important}}

  footer{{height:26px;flex:none;padding:0 16px;background:var(--panel);border-top:1px solid var(--border);font-size:10px;color:var(--muted);display:flex;align-items:center;justify-content:space-between}}
</style>
</head>
<body>

<header>
  <div class="logo">
    <svg viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="18" fill="#10b981" fill-opacity="0.2" stroke="#10b981" stroke-width="2"/>
      <path d="M20 7L23 16L32 17L25 23L27 32L20 27L13 32L15 23L8 17L17 16L20 7Z" fill="#34d399"/>
      <circle cx="20" cy="20" r="4" fill="#fff"/>
    </svg>
  </div>
  <div>
    <h1>SunPro · <span>Cluster Piacentino A1 & A21</span></h1>
    <div class="sub">Scansione Catastale WMS AdE · 90 Lotti Aperta Campagna + 26 Riserve · Rete AT/MT & PVGIS</div>
  </div>
  <div class="sp"></div>

  <div class="threshold-box" title="Modifica la soglia massima €/mq per ricalcolare in tempo reale tutte le spese massime e la verifica post-visura">
    <label for="thresholdInput">💶 Soglia Max (€/mq):</label>
    <input type="number" id="thresholdInput" value="8.00" step="0.25" min="3.00" max="20.00">
  </div>

  <a href="Quotazioni_Mercato_Reale_e_Comparabili_Piacentino_A1_A21.xlsx" download class="nav-btn excel" title="Scarica il Workbook Excel a 5 fogli con Quotazioni Reali dei 13 Comuni, Pertiche Piacentine, Rogiti CREA, Portali, Zona D e i 116 Lotti">
    📊 Excel Mercato Reale & 116 Lotti (5 Fogli)
  </a>
  <a href="Terreni_FV_Piacentino_A1_A21_Esteso.xlsx" download class="nav-btn" title="Scarica il foglio di calcolo esteso con tutti i 116 lotti">
    📄 Excel Esteso
  </a>
  <a href="SunPro_Piacentino_A1_A21.kml" download class="nav-btn" title="Scarica KML per Google Earth">
    🌍 KML 3D
  </a>
  <button class="nav-btn" onclick="exportVisureCsv()" title="Esporta CSV aggiornato con gli intestatari e i prezzi inseriti da visura">
    💾 Esporta Visure CSV
  </button>
  <a href="index.html" class="nav-btn primary" title="Torna alla Mappa Nazionale SunPro (60 compendi Italia Nord & Centro)">
    🇮🇹 Mappa Nazionale
  </a>
</header>

<div id="kpis">
  <div class="kpi" style="--kc:var(--green)"><div class="v" id="kpiCount">90 lotti</div><div class="l" id="kpiCountSub">Aperta Campagna (116 tot)</div></div>
  <div class="kpi" style="--kc:var(--amber)"><div class="v" id="kpiArea">{tot_ha} ha</div><div class="l" id="kpiAreaSub">di cui {tot_300_ha} ha entro 300m</div></div>
  <div class="kpi" style="--kc:var(--accent)"><div class="v" id="kpiPower">{tot_mwp} MWp</div><div class="l" id="kpiPowerSub">{tot_mwp_300} MWp nella fascia ≤300m</div></div>
  <div class="kpi" style="--kc:#38bdf8"><div class="v" id="kpiGrid">1,8 km</div><div class="l" id="kpiGridSub">Dist. media Stazione AT / Linea AT</div></div>
  <div class="kpi" style="--kc:var(--brand)"><div class="v" id="kpiSpend">€ {tot_spesa_m}M</div><div class="l" id="kpiSpendSub">Spesa max a soglia 8,00 €/mq</div></div>
  <div class="kpi" style="--kc:var(--pink)"><div class="v" id="kpiLease">€ 2,13M/a</div><div class="l" id="kpiLeaseSub">Canone DDS 30y (3.000 €/ha/a)</div></div>
</div>

<main>
  <div id="map">
    <div id="tools">
      <button class="tool on" id="tSat">🛰️ Satellite HD (Esri)</button>
      <button class="tool on" id="tBuf300">🛣️ Fascia 300m A1 & A21</button>
      <button class="tool on" id="tGridAT">⚡ Linee AT (132/380 kV) & Stazioni</button>
      <button class="tool" id="tWmsCatasto" title="Sovrappone in tempo reale i confini catastali WMS dell'Agenzia delle Entrate (visibile ad alto zoom)">🗺️ Confini Catasto WMS Live</button>
      <button class="tool" id="tReset">🔄 Inquadra Piacentino</button>
    </div>
    <div id="orbitHint">🚁 Sopralluogo 3D Orbitale in corso — clicca sulla mappa per fermare</div>
    <div id="siteTip"></div>
  </div>

  <aside>
    <div class="lbl">
      <span>Cluster Piacentino · A1 & A21</span>
      <span class="mono" id="sitesCount" style="color:var(--green)">90 lotti</span>
    </div>

    <div id="filters">
      <button class="pill active" data-filter="APERTA_ALL">🌾 Tutta Aperta Campagna (90)</button>
      <button class="pill" data-filter="PRIORITA_1" style="border-color:#2563eb;color:#93c5fd">🔥 Priorità 1 Visura</button>
      <button class="pill" data-filter="TOP_50_EXCEL">📋 Top 50 Foglio Excel</button>
      <button class="pill" data-filter="ESTENSIONE_WMS_20" style="border-color:#10b981;color:#34d399">➕ +20 Estensione WMS</button>
      <button class="pill" data-filter="RISERVE_APERTA_15">🌾 +15 Extra Aperta</button>
      <button class="pill" data-filter="BENCHMARK_TEST_5">⭐ 5 Test Cadeo-Pontenure</button>
      <button class="pill" data-filter="RISERVA_PERIURBANA" style="border-color:#f59e0b;color:#fcd34d">⚠️ Riserve Periurbane (26)</button>
      <button class="pill" data-filter="TUTTI_116">Tutti (116)</button>
    </div>

    <div class="controls-grid">
      <select id="hwySelect">
        <option value="ALL">🛣️ A1 + A21</option>
        <option value="A1">Solo A1 (Milano-Bologna)</option>
        <option value="A21">Solo A21 (Torino-Brescia)</option>
      </select>
      <select id="comuneSelect">
        <option value="ALL">📍 Tutti i 13 Comuni</option>
      </select>
      <select id="sortSelect">
        <option value="sup_300m">Ordina: Sup. ≤300m (ha) ↓</option>
        <option value="sup_tot">Ordina: Sup. Totale (ha) ↓</option>
        <option value="dist_staz">Ordina: Stazione Elettrica ↑</option>
        <option value="dist_at">Ordina: Linea AT (m) ↑</option>
        <option value="score">Ordina: Score SunPro ↓</option>
      </select>
    </div>

    <div class="search-box">
      <svg class="ic" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
      <input type="text" id="searchInput" placeholder="Cerca comune, foglio, particella, stazione (es. Rottofreno, Fg. 13, 31, Cadeo FS)...">
    </div>

    <div id="cards"></div>

    <div class="info-panel">
      <h3>📋 Metodo, Estensione & Verifiche Pre-Contatto</h3>
      <ul>
        <li><b>Perché il Piacentino (A1 & A21):</b> Pianura irrigua fuori dal comprensorio del Parmigiano Reggiano, VAM 2026 contenuto (<b>5,45–5,85 €/mq</b>, BURERT n. 75 del 02/04/2026) e idoneità ex lege nella fascia <b>≤ 300 m</b> autostradale (D.Lgs. 199/2021).</li>
        <li><b>Estensione Scansione WMS AdE (90 Aperta Campagna + 26 Riserve):</b> Oltre ai <b>50 terreni</b> principali (388,4 ha), la mappa integra i <b>15 lotti extra</b> in aperta campagna del foglio Riserve (70,2 ha), i <b>5 lotti benchmark</b> di Pontenure-Cadeo tagliati dai bordi della prima griglia (34,9 ha) e <b>20 nuovi lotti in aperta campagna</b> (216,1 ha) estratti con scansione WMS a griglia sfalsata anti-taglio. I <b>26 lotti periurbani</b> (&lt;250 m da aree produttive/residenziali o Le Mose) sono isolati nel filtro Riserve.</li>
        <li><b>Rete Elettrica & Cabine:</b> Ogni scheda incrocia la distanza dalla <b>Linea AT (132/220/380 kV)</b> e dalla <b>Stazione Elettrica OSM</b> con la <b>Cabina Primaria ARERA/GSE</b>, il tracciato cavidotto MT (1,30x) e il CAPEX TICA stimato.</li>
        <li><b>Prossimo Passo Operativo (Visure Sister):</b> Conviene partire dai lotti <b>🔥 Priorità 1</b> (i più ampi o a &lt;1,5 km da stazione elettrica / &lt;150 m da linea AT). Prima dell'offerta verificare: <b>destinazione urbanistica (PUG/PSC)</b>, <b>vincoli paesaggistici/fluviali</b> e <b>colture certificate BIO/DOP/IGP</b> (la L.R. Emilia-Romagna 5/2026 su biologico e DOP/IGP ammette solo l'agrivoltaico).</li>
      </ul>
    </div>
  </aside>
</main>

<footer>
  <span>Proprietà Intellettuale © 2026 <b>Nicola Valigi (Houdinick)</b> · Cluster Piacentino A1 & A21</span>
  <span>Fonti: WMS Catasto Agenzia delle Entrate (21/10/2026) · OpenStreetMap Overpass · Database Cabine ARERA/GSE · PVGIS JRC · BURERT VAM 2026</span>
</footer>

<script>
const LOTS = {lots_json};

// Carica stato post-visura salvato nel browser
const VISURA_STORAGE_KEY = "sunpro_piacentino_visure_v1";
let visuraState = {{}};
try {{
  visuraState = JSON.parse(localStorage.getItem(VISURA_STORAGE_KEY) || "{{}}");
}} catch(e) {{ visuraState = {{}}; }}

function saveVisuraField(id, field, val) {{
  if (!visuraState[id]) visuraState[id] = {{ owner: "", price: "" }};
  visuraState[id][field] = val;
  try {{ localStorage.setItem(VISURA_STORAGE_KEY, JSON.stringify(visuraState)); }} catch(e) {{}}
  updateCardVisuraBadge(id);
}}

function getThreshold() {{
  const v = parseFloat(document.getElementById("thresholdInput").value);
  return isNaN(v) || v <= 0 ? 8.0 : v;
}}

function updateCardVisuraBadge(id) {{
  const st = visuraState[id] || {{}};
  const badge = document.getElementById(`vbadge-${{id}}`);
  if (!badge) return;
  const p = parseFloat(st.price);
  const thr = getThreshold();
  if (isNaN(p) || p <= 0) {{
    badge.className = "visura-status wait";
    badge.textContent = "DA VISURA";
  }} else if (p <= thr) {{
    badge.className = "visura-status ok";
    badge.textContent = `✓ SÌ (≤${{thr.toFixed(2)}}€)`;
  }} else {{
    badge.className = "visura-status no";
    badge.textContent = `✗ SOPRA (${{p.toFixed(2)}}€)`;
  }}
}}

// Popola menu Comuni
const comuniCounts = {{}};
LOTS.forEach(l => {{ comuniCounts[l.comune] = (comuniCounts[l.comune] || 0) + 1; }});
const comuneSel = document.getElementById("comuneSelect");
Object.keys(comuniCounts).sort().forEach(c => {{
  const opt = document.createElement("option");
  opt.value = c;
  opt.textContent = `${{c}} (${{comuniCounts[c]}})`;
  comuneSel.appendChild(opt);
}});

// Inizializza Mappa 3D centrata sul Piacentino (A1 - A21)
const map = new maplibregl.Map({{
  container: 'map',
  style: {{
    version: 8,
    sources: {{
      'esri-satellite': {{
        type: 'raster',
        tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}'],
        tileSize: 256,
        attribution: 'Esri World Imagery'
      }},
      'carto-dark': {{
        type: 'raster',
        tiles: ['https://a.basemaps.cartocdn.com/dark_only_labels/{{z}}/{{x}}/{{y}}.png'],
        tileSize: 256
      }},
      'ade-wms': {{
        type: 'raster',
        tiles: [
          'https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=CP.CadastralParcel,fabbricati&STYLES=&CRS=EPSG:3857&BBOX={{bbox-epsg-3857}}&WIDTH=256&HEIGHT=256&FORMAT=image/png&TRANSPARENT=TRUE'
        ],
        tileSize: 256
      }}
    }},
    layers: [
      {{ id: 'satellite-layer', type: 'raster', source: 'esri-satellite', paint: {{ 'raster-opacity': 1 }} }},
      {{ id: 'ade-wms-layer', type: 'raster', source: 'ade-wms', layout: {{ visibility: 'none' }}, paint: {{ 'raster-opacity': 0.65 }} }},
      {{ id: 'carto-labels', type: 'raster', source: 'carto-dark', paint: {{ 'raster-opacity': 0.85 }} }}
    ]
  }},
  center: [9.765, 45.025],
  zoom: 10.3,
  pitch: 38,
  bearing: 0,
  maxPitch: 75
}});

map.addControl(new maplibregl.NavigationControl(), 'bottom-right');

let markers = [];
let activeFilter = "APERTA_ALL";
let activeOrbit = false;
let orbitRaf = null;

map.on('load', async () => {{
  // Carica layer vettoriali A1/A21, Buffer 300m, Linee AT e Stazioni Elettriche
  try {{
    const resp = await fetch("piacentino_vector_layers.geojson");
    const geojson = await resp.json();
    map.addSource("pc-vectors", {{ type: "geojson", data: geojson }});

    // 1. Fascia Buffer 300m A1 e A21
    map.addLayer({{
      id: "pc-buffer-fill",
      type: "fill",
      source: "pc-vectors",
      filter: ["==", ["get", "layer"], "buffer_300m"],
      paint: {{
        "fill-color": "#10b981",
        "fill-opacity": 0.18
      }}
    }}, "carto-labels");

    map.addLayer({{
      id: "pc-buffer-line",
      type: "line",
      source: "pc-vectors",
      filter: ["==", ["get", "layer"], "buffer_300m"],
      paint: {{
        "line-color": "#34d399",
        "line-width": 1.5,
        "line-dasharray": [3, 2],
        "line-opacity": 0.8
      }}
    }}, "carto-labels");

    // 2. Asse Autostradale A1 e A21
    map.addLayer({{
      id: "pc-hwy-axis",
      type: "line",
      source: "pc-vectors",
      filter: ["==", ["get", "layer"], "highway_axis"],
      paint: {{
        "line-color": "#38bdf8",
        "line-width": 2.6,
        "line-opacity": 0.9
      }}
    }}, "carto-labels");

    // 3. Elettrodotti AT (132 / 220 / 380 kV)
    map.addLayer({{
      id: "pc-power-lines",
      type: "line",
      source: "pc-vectors",
      filter: ["==", ["get", "layer"], "power_line"],
      paint: {{
        "line-color": [
          "case",
          [">=", ["get", "kv"], 380], "#f43f5e",
          [">=", ["get", "kv"], 220], "#f59e0b",
          "#eab308"
        ],
        "line-width": [
          "case",
          [">=", ["get", "kv"], 380], 2.6,
          1.8
        ],
        "line-opacity": 0.88
      }}
    }}, "carto-labels");

    // 4. Stazioni Elettriche RTN/AT
    map.addLayer({{
      id: "pc-substations",
      type: "circle",
      source: "pc-vectors",
      filter: ["==", ["get", "layer"], "substation"],
      paint: {{
        "circle-radius": 6.5,
        "circle-color": "#f43f5e",
        "circle-stroke-width": 2,
        "circle-stroke-color": "#ffffff"
      }}
    }});

    map.on("click", "pc-substations", (e) => {{
      const p = e.features[0].properties;
      new maplibregl.Popup({{ closeButton: true, maxWidth: "260px" }})
        .setLngLat(e.lngLat)
        .setHTML(`<div style="color:#0f172a;font-size:12px"><b>⚡ ${{p.name}}</b><br>Tensione: <b>${{p.kv}} kV</b><br>Operatore: ${{p.operator}}</div>`)
        .addTo(map);
    }});
  }} catch (err) {{
    console.warn("GeoJSON vettoriale non caricato:", err);
  }}

  initMarkers();
  renderAll();
}});

function initMarkers() {{
  LOTS.forEach(s => {{
    const isPeri = s.gruppo === "RISERVA_PERIURBANA";
    const isP1 = s.priorita_visura === "PRIORITA_1_TOP";
    const outerColor = isPeri ? "#D97706" : (isP1 ? "#2563EB" : "#059669");
    const ringColor = isPeri ? "#92400E" : (isP1 ? "#1E3A8A" : "#065F46");
    const strokeAttr = isP1 ? 'stroke="#38BDF8" stroke-width="3"' : (isPeri ? 'stroke="#FCD34D" stroke-width="2.5"' : 'stroke="#34D399" stroke-width="2.5"');

    const el = document.createElement("div");
    el.className = "map-pin-wrap";
    el.id = `pin-${{s.id}}`;
    el.title = `${{s.comune}} (${{s.belfiore}}) · Fg.${{s.foglio}} Part.${{s.particella}}\\nSup: ${{s.sup_tot_ha}} ha (${{s.sup_300m_ha}} ha ≤300m da ${{s.autostrada}})\\nLinea AT: ${{s.dist_linea_at_m}} m (${{s.kv_linea}} kV) · Stazione: ${{s.stazione_nome}} (${{s.dist_stazione_km}} km)`;
    el.innerHTML = `
      <svg viewBox="0 0 100 142">
        <ellipse cx="50" cy="138" rx="16" ry="3.5" fill="rgba(15,23,42,0.5)"/>
        <path d="M 50 136 L 9.5 77.6 A 49 49 0 1 1 90.5 77.6 Z" fill="${{outerColor}}"/>
        <circle cx="50" cy="49" r="36" fill="${{ringColor}}"/>
        <circle cx="50" cy="49" r="24" fill="#FFFFFF" ${{strokeAttr}}/>
        <text x="50" y="49" font-family="'JetBrains Mono',sans-serif" font-size="18.5" font-weight="900" fill="#0F172A" text-anchor="middle" dominant-baseline="central">${{s.sup_300m_ha.toFixed(1)}}</text>
      </svg>
    `;
    el.onclick = (e) => {{
      e.stopPropagation();
      focusLot(s.id);
    }};
    const m = new maplibregl.Marker({{ element: el, anchor: 'bottom' }})
      .setLngLat([s.lon, s.lat])
      .addTo(map);
    markers.push({{ id: s.id, marker: m, el: el }});
  }});
}}

function getFilteredLots() {{
  const q = document.getElementById("searchInput").value.trim().toLowerCase();
  const hwy = document.getElementById("hwySelect").value;
  const com = document.getElementById("comuneSelect").value;
  const sortBy = document.getElementById("sortSelect").value;

  let list = LOTS.filter(s => {{
    if (activeFilter === "APERTA_ALL" && s.gruppo !== "APERTA_CAMPAGNA") return false;
    if (activeFilter === "PRIORITA_1" && s.priorita_visura !== "PRIORITA_1_TOP") return false;
    if (activeFilter === "TOP_50_EXCEL" && s.origine !== "TOP_50_EXCEL") return false;
    if (activeFilter === "ESTENSIONE_WMS_20" && s.origine !== "ESTENSIONE_WMS_20") return false;
    if (activeFilter === "RISERVE_APERTA_15" && s.origine !== "RISERVE_APERTA_15") return false;
    if (activeFilter === "BENCHMARK_TEST_5" && s.origine !== "BENCHMARK_TEST_5") return false;
    if (activeFilter === "RISERVA_PERIURBANA" && s.gruppo !== "RISERVA_PERIURBANA") return false;

    if (hwy !== "ALL" && s.autostrada !== hwy) return false;
    if (com !== "ALL" && s.comune !== com) return false;

    if (q) {{
      const hay = `${{s.id}} ${{s.comune}} ${{s.belfiore}} fg.${{s.foglio}} ${{s.foglio}} ${{s.particella}} ${{s.autostrada}} ${{s.stazione_nome}} ${{s.cp_arera_nome}} ${{s.note}}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});

  list.sort((a, b) => {{
    if (sortBy === "sup_300m") return b.sup_300m_ha - a.sup_300m_ha || b.sup_tot_ha - a.sup_tot_ha;
    if (sortBy === "sup_tot") return b.sup_tot_ha - a.sup_tot_ha;
    if (sortBy === "dist_staz") return a.dist_stazione_km - b.dist_stazione_km;
    if (sortBy === "dist_at") return a.dist_linea_at_m - b.dist_linea_at_m;
    if (sortBy === "score") return b.score - a.score;
    return 0;
  }});

  return list;
}}

function renderAll() {{
  const filtered = getFilteredLots();
  const thr = getThreshold();

  // Aggiorna KPI dinamici
  const count = filtered.length;
  const sumTotHa = filtered.reduce((acc, x) => acc + x.sup_tot_ha, 0);
  const sum300Ha = filtered.reduce((acc, x) => acc + x.sup_300m_ha, 0);
  const sumMwpTot = filtered.reduce((acc, x) => acc + x.mwp_tot, 0);
  const sumMwp300 = filtered.reduce((acc, x) => acc + x.mwp_300m, 0);
  const avgStazKm = count > 0 ? (filtered.reduce((acc, x) => acc + x.dist_stazione_km, 0) / count).toFixed(1) : "0.0";
  const avgAtM = count > 0 ? Math.round(filtered.reduce((acc, x) => acc + x.dist_linea_at_m, 0) / count) : 0;
  const sumSpendTotM = (sumTotHa * 10000 * thr) / 1_000_000;
  const sumSpend300M = (sum300Ha * 10000 * thr) / 1_000_000;
  const sumLeaseM = (sumTotHa * 3000) / 1_000_000;

  document.getElementById("kpiCount").textContent = `${{count}} lotti`;
  document.getElementById("kpiCountSub").textContent = `100% Verificati WMS AdE`;
  document.getElementById("kpiArea").textContent = `${{sumTotHa.toFixed(1)}} ha`;
  document.getElementById("kpiAreaSub").textContent = `di cui ${{sum300Ha.toFixed(1)}} ha entro 300m`;
  document.getElementById("kpiPower").textContent = `${{sumMwpTot.toFixed(1)}} MWp`;
  document.getElementById("kpiPowerSub").textContent = `${{sumMwp300.toFixed(1)}} MWp nella fascia ≤300m`;
  document.getElementById("kpiGrid").textContent = `${{avgStazKm}} km`;
  document.getElementById("kpiGridSub").textContent = `Stazione AT · Linea AT media ${{avgAtM}} m`;
  document.getElementById("kpiSpend").textContent = `€ ${{sumSpendTotM.toFixed(2)}}M`;
  document.getElementById("kpiSpendSub").textContent = `a ${{thr.toFixed(2)}} €/mq (€ ${{sumSpend300M.toFixed(2)}}M ≤300m)`;
  document.getElementById("kpiLease").textContent = `€ ${{sumLeaseM.toFixed(2)}}M/a`;
  document.getElementById("kpiLeaseSub").textContent = `Canone DDS 30y (3.000 €/ha/a)`;

  document.getElementById("sitesCount").textContent = `${{count}} lotti`;

  const container = document.getElementById("cards");
  container.innerHTML = "";

  filtered.forEach((s, idx) => {{
    const isPeri = s.gruppo === "RISERVA_PERIURBANA";
    const isP1 = s.priorita_visura === "PRIORITA_1_TOP";
    const cardClass = isPeri ? "peri" : (isP1 ? "p1" : "p2");
    const tagClass = isPeri ? "peri" : (isP1 ? "p1" : "p2");

    const spendTot = Math.round(s.sup_tot_ha * 10000 * thr);
    const spend300 = Math.round(s.sup_300m_ha * 10000 * thr);
    const vst = visuraState[s.id] || {{ owner: "", price: "" }};

    const card = document.createElement("div");
    card.className = `card ${{cardClass}}`;
    card.id = `card-${{s.id}}`;

    card.innerHTML = `
      <div class="row" onclick="focusLot('${{s.id}}')">
        <div>
          <div class="name">#${{idx + 1}} · ${{s.comune}} — Fg. ${{s.foglio}} Part. ${{s.particella}}</div>
          <div class="subtag">
            <span class="mono">${{s.id}}</span>
            <span>· Cod. <b>${{s.belfiore}}</b></span>
            <span>· 🛣️ <b>${{s.autostrada}}</b> (${{s.dist_asse_m}} m)</span>
            <span class="tag ${{tagClass}}">${{s.priorita_label}}</span>
            <span class="tag cohort">${{s.categoria_label}}</span>
          </div>
        </div>
        <div class="score">${{s.score.toFixed(1)}}</div>
      </div>

      <div class="note">${{s.note}}</div>

      <div class="dists">
        <div class="d-row" style="background:rgba(16,185,129,.1);padding:3px 6px;border-radius:4px;border:1px solid rgba(16,185,129,.25)">
          <span style="color:#34d399;font-weight:700">📐 Sup. (Ettari & Pertiche 762mq):</span>
          <b style="color:#34d399">${{s.sup_tot_ha}} ha (${{(s.pertiche_tot || (s.sup_tot_ha*13.123)).toFixed(1)}} pert.) · ${{s.sup_300m_ha}} ha ≤300m</b>
        </div>
        <div class="d-row">
          <span>⚡ Linea AT più vicina (OSM):</span>
          <b style="color:${{s.dist_linea_at_m <= 150 ? '#38bdf8' : 'var(--txt)'}}">${{s.dist_linea_at_m}} m (${{s.kv_linea}} kV)</b>
        </div>
        <div class="d-row">
          <span>🏭 Stazione Elettrica più vicina (OSM):</span>
          <b>${{s.stazione_display}} a ${{s.dist_stazione_km}} km</b>
        </div>
        <div class="d-row">
          <span>🔌 Cabina Primaria ARERA/GSE & CAPEX MT:</span>
          <b>${{s.cp_arera_nome}} (~${{s.cavidotto_mt_m}}m · € ${{s.capex_allaccio_eur.toLocaleString('it-IT')}})</b>
        </div>
        <div class="d-row">
          <span>☀️ Potenza & Producibilità PVGIS Tracker:</span>
          <b>${{s.mwp_tot}} MWp (${{s.mwp_300m}} MWp ≤300m) · ~${{s.mwh_tracker.toLocaleString('it-IT')}} MWh/a</b>
        </div>
        <div class="d-row" style="background:rgba(37,99,235,.14);padding:3px 6px;border-radius:4px;border:1px solid rgba(59,130,246,.3)">
          <span style="color:#93c5fd;font-weight:700">🤝 Rogito Reale Agricolo (${{s.comune}}):</span>
          <b style="color:#93c5fd">${{(s.rogito_med_mq || 5.55).toFixed(2)}} €/mq (${{(s.rogito_pertica_eur || 4230).toLocaleString('it-IT')}} €/pert. · € ${{(s.valore_rogito_reale_eur || Math.round(s.sup_tot_ha*55500)).toLocaleString('it-IT')}})</b>
        </div>
        <div class="d-row">
          <span>🏘️ Portali Immobiliari vs Zona D Ind.:</span>
          <b>Portali ${{s.asking_range_mq || '5.20–6.60'}} €/mq · Zona D ${{s.ind_range_mq || '70–100'}} €/mq</b>
        </div>
        <div class="d-row" style="background:rgba(56,189,248,.08);padding:3px 6px;border-radius:4px;border:1px solid rgba(56,189,248,.22)">
          <span style="color:#38bdf8;font-weight:700">💶 Offerta Cons. ${{(s.fv_buy_cons_mq || 7.30).toFixed(2)}}€ (${{(s.fv_buy_pertica_eur || 5560).toLocaleString('it-IT')}} €/pert.):</span>
          <b style="color:#38bdf8">Max ${{thr.toFixed(2)}}€: € ${{spendTot.toLocaleString('it-IT')}} (VAM ${{s.vam_2026_mq.toFixed(2)}}€)</b>
        </div>
        <div class="d-row">
          <span>🌱 DDS 30y (Esente Prelazione) vs Affitto:</span>
          <b>€ ${{s.canone_dds_tot_eur.toLocaleString('it-IT')}}/a (3.000 €/ha vs ${{s.affitto_agr_ha || 620}} €/ha agr.)</b>
        </div>
      </div>

      <div class="visura-box" onclick="event.stopPropagation()">
        <div class="visura-title">
          <span>🗂️ Check-In Visura Catastale Sister (€ 1,35)</span>
          <span id="vbadge-${{s.id}}" class="visura-status wait">DA VISURA</span>
        </div>
        <div class="visura-inputs">
          <input type="text" placeholder="Intestatario (da visura)..." value="${{(vst.owner || '').replace(/"/g, '&quot;')}}" oninput="saveVisuraField('${{s.id}}', 'owner', this.value)">
          <input type="number" step="0.10" placeholder="Richiesta €/mq" value="${{vst.price || ''}}" oninput="saveVisuraField('${{s.id}}', 'price', this.value)">
          <a href="${{s.wms_url}}" target="_blank" class="btn" style="padding:4px 7px;font-size:10px" title="Interroga live il server WMS dell'Agenzia delle Entrate">WMS AdE</a>
        </div>
      </div>

      <div class="btns">
        <button class="btn brand" onclick="start3DOrbit('${{s.id}}')">🚁 3D Orbit</button>
        <a class="btn" href="${{s.gmaps_url}}" target="_blank">🛰️ Ortofoto HD</a>
        <a class="btn" href="${{s.wms_url}}" target="_blank">🏛️ Mappale AdE</a>
      </div>
    `;

    card.addEventListener("mouseenter", () => {{
      const p = document.getElementById(`pin-${{s.id}}`);
      if (p) p.classList.add("hovered");
    }});
    card.addEventListener("mouseleave", () => {{
      const p = document.getElementById(`pin-${{s.id}}`);
      if (p) p.classList.remove("hovered");
    }});

    container.appendChild(card);
    updateCardVisuraBadge(s.id);
  }});

  // Aggiorna visibilità pin sulla mappa
  const visIds = new Set(filtered.map(x => x.id));
  markers.forEach(m => {{
    m.el.style.display = visIds.has(m.id) ? "flex" : "none";
  }});
}}

function focusLot(id) {{
  stopOrbit();
  const s = LOTS.find(x => x.id === id);
  if (!s) return;

  document.querySelectorAll(".map-pin-wrap").forEach(p => p.classList.remove("active"));
  const pin = document.getElementById(`pin-${{s.id}}`);
  if (pin) pin.classList.add("active");

  document.querySelectorAll(".card").forEach(c => c.classList.remove("sel"));
  const card = document.getElementById(`card-${{s.id}}`);
  if (card) {{
    card.classList.add("sel");
    card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
  }}

  map.flyTo({{
    center: [s.lon, s.lat],
    zoom: 16.2,
    pitch: 55,
    bearing: 30,
    speed: 1.25
  }});

  const thr = getThreshold();
  const spendTot = Math.round(s.sup_tot_ha * 10000 * thr);
  const tip = document.getElementById("siteTip");
  tip.style.display = "block";
  tip.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
      <span style="font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#34d399;font-weight:800">${{s.categoria_label}} · ${{s.priorita_label}}</span>
      <button onclick="document.getElementById('siteTip').style.display='none'" style="background:none;border:none;color:var(--muted);cursor:pointer;font-size:16px">&times;</button>
    </div>
    <div style="font-size:14px;font-weight:800;color:#fff">${{s.comune}} (Cod. ${{s.belfiore}}) — Foglio ${{s.foglio}} · Particella ${{s.particella}}</div>
    <div style="font-size:11.2px;color:#cbd5e1;margin-top:5px;line-height:1.45">
      • <b>Superficie:</b> <b>${{s.sup_tot_ha}} ha</b> totali, di cui <b style="color:#34d399">${{s.sup_300m_ha}} ha entro 300 m</b> da <b>${{s.autostrada}}</b> (dist. min. ${{s.dist_asse_m}} m).<br>
      • <b>Rete AT/MT:</b> Linea AT <b>${{s.kv_linea}} kV a ${{s.dist_linea_at_m}} m</b> · Stazione <b>${{s.stazione_display}} a ${{s.dist_stazione_km}} km</b> · CP ARERA <b>${{s.cp_arera_nome}}</b>.<br>
      • <b>Spesa Max a ${{thr.toFixed(2)}} €/mq:</b> <b style="color:#38bdf8">€ ${{spendTot.toLocaleString('it-IT')}}</b> (VAM 2026: ${{s.vam_2026_mq.toFixed(2)}} €/mq) · Potenza: <b>${{s.mwp_tot}} MWp</b>.<br>
      • <b>Note:</b> <span style="color:#fbbf24">${{s.note}}</span>
    </div>
  `;
}}

function start3DOrbit(id) {{
  focusLot(id);
  document.getElementById("orbitHint").style.display = "flex";
  activeOrbit = true;
  let b = 30;
  function step() {{
    if (!activeOrbit) return;
    b = (b + 0.35) % 360;
    map.setBearing(b);
    orbitRaf = requestAnimationFrame(step);
  }}
  orbitRaf = requestAnimationFrame(step);
}}

function stopOrbit() {{
  activeOrbit = false;
  if (orbitRaf) cancelAnimationFrame(orbitRaf);
  document.getElementById("orbitHint").style.display = "none";
}}

map.on("mousedown", stopOrbit);
map.on("touchstart", stopOrbit);

// Event Listeners Filtri & Controlli
document.querySelectorAll(".pill").forEach(btn => {{
  btn.addEventListener("click", () => {{
    document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    activeFilter = btn.getAttribute("data-filter");
    renderAll();
  }});
}});

document.getElementById("hwySelect").addEventListener("change", renderAll);
document.getElementById("comuneSelect").addEventListener("change", renderAll);
document.getElementById("sortSelect").addEventListener("change", renderAll);
document.getElementById("searchInput").addEventListener("input", renderAll);
document.getElementById("thresholdInput").addEventListener("input", renderAll);

// Toolbar Mappa
let satOn = true;
document.getElementById("tSat").addEventListener("click", (e) => {{
  satOn = !satOn;
  e.currentTarget.classList.toggle("on", satOn);
  map.setLayoutProperty("satellite-layer", "visibility", satOn ? "visible" : "none");
}});

let bufOn = true;
document.getElementById("tBuf300").addEventListener("click", (e) => {{
  bufOn = !bufOn;
  e.currentTarget.classList.toggle("on", bufOn);
  ["pc-buffer-fill", "pc-buffer-line", "pc-hwy-axis"].forEach(id => {{
    if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", bufOn ? "visible" : "none");
  }});
}});

let gridOn = true;
document.getElementById("tGridAT").addEventListener("click", (e) => {{
  gridOn = !gridOn;
  e.currentTarget.classList.toggle("on", gridOn);
  ["pc-power-lines", "pc-substations"].forEach(id => {{
    if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", gridOn ? "visible" : "none");
  }});
}});

let wmsOn = false;
document.getElementById("tWmsCatasto").addEventListener("click", (e) => {{
  wmsOn = !wmsOn;
  e.currentTarget.classList.toggle("on", wmsOn);
  if (map.getLayer("ade-wms-layer")) {{
    map.setLayoutProperty("ade-wms-layer", "visibility", wmsOn ? "visible" : "none");
  }}
}});

document.getElementById("tReset").addEventListener("click", () => {{
  stopOrbit();
  document.getElementById("siteTip").style.display = "none";
  map.flyTo({{ center: [9.765, 45.025], zoom: 10.3, pitch: 38, bearing: 0 }});
}});

function exportVisureCsv() {{
  const thr = getThreshold();
  const rows = [
    ["ID", "Comune", "Belfiore", "Foglio", "Particella", "Coorte", "Priorita_Visura", "Sup_Tot_ha", "Sup_300m_ha", "Autostrada", "Dist_Asse_m", "Linea_AT_m", "kV_Linea", "Stazione_OSM", "Dist_Stazione_km", "Cabina_ARERA", "CAPEX_Allaccio_EUR", "MWp_Tot", "Spesa_Max_Soglia_EUR", "Intestatario_Visura", "Prezzo_Richiesto_EUR_mq", "Entro_Soglia", "Lat", "Lon", "Note"]
  ];
  LOTS.forEach(s => {{
    const vst = visuraState[s.id] || {{ owner: "", price: "" }};
    const p = parseFloat(vst.price);
    const entro = (!isNaN(p) && p > 0) ? (p <= thr ? "SI" : "NO") : "";
    const spend = Math.round(s.sup_tot_ha * 10000 * thr);
    rows.push([
      s.id, s.comune, s.belfiore, s.foglio, s.particella, s.categoria_label, s.priorita_visura,
      s.sup_tot_ha, s.sup_300m_ha, s.autostrada, s.dist_asse_m, s.dist_linea_at_m, s.kv_linea,
      s.stazione_nome, s.dist_stazione_km, s.cp_arera_nome, s.capex_allaccio_eur, s.mwp_tot,
      spend, vst.owner || "", vst.price || "", entro, s.lat, s.lon, `"${{(s.note || '').replace(/"/g, '""')}}"`
    ]);
  }});
  const csvContent = "\\uFEFF" + rows.map(r => r.join(";")).join("\\n");
  const blob = new Blob([csvContent], {{ type: "text/csv;charset=utf-8;" }});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SunPro_Piacentino_Visure_Soglia_${{thr.toFixed(2)}}eur.csv`;
  a.click();
}}
</script>
</body>
</html>
"""
    out_root = BASE_DIR / "piacentino.html"
    out_web = WEB_DIR / "piacentino.html"
    out_root.write_text(html, encoding="utf-8")
    out_web.write_text(html, encoding="utf-8")
    # Copia anche il file Excel originale in web/data/ per il download diretto da GitHub Pages
    (WEB_DIR / "data").mkdir(parents=True, exist_ok=True)
    shutil.copy2(DATA_DIR / "Terreni_FV_Piacentino_A1_A21.xlsx", WEB_DIR / "data" / "Terreni_FV_Piacentino_A1_A21.xlsx")
    print("  ✓ Piattaforma dedicata piacentino.html e web/piacentino.html generata con successo!")


if __name__ == "__main__":
    build_piacentino_html()
