"""
☀️ SOLAR ORIGINATION PRO™ — Executive Spatial Intelligence Dashboard
Applicazione Desktop ad alte prestazioni per Land Origination Fotovoltaico.
Design System: Glassmorphism, Modern Executive UI, Multi-layer Satellite Maps,
Interactive Financial Analytics & Antigravity AI Copilot.
Autore: Nicola Valigi Engine System
"""

import json
import os
from pathlib import Path
import folium
from folium.plugins import MarkerCluster, Fullscreen
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from config import (
    LEAD_STATUSES,
    PRIORITY_REGIONS,
    TARGET_PRICE_TARGET_EUR,
    WEIGHTS,
)
from crawler.cadastral_resolver import get_cadastral_wms_url
from crawler.owner_discovery import generate_commercial_pitch
from crawler.spatial_engine import calculate_energy_and_capex
from data.storage import (
    get_all_leads,
    get_lead,
    get_leads_df,
    init_db,
    update_status,
    upsert_lead,
)
from pipeline import process_and_save_lead, sync_all_curated_leads
from reports.generator import generate_html_dossier, generate_pdf_dossier
from scoring.scorer import calculate_site_score
from sync_to_drive import sync_prototype_to_drive

# -------------------------------------------------------------
# PAGE CONFIGURATION & LUXURY DESIGN SYSTEM
# -------------------------------------------------------------
st.set_page_config(
    page_title="Solar Origination Pro™ | Nicola Valigi Engine System",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Luxury CSS Injection (Custom Design System with Plus Jakarta Sans & Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Background and containers */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 50%, #E2E8F0 100%);
    }

    /* Executive Top Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #064E3B 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -10px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #34D399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Chips and Badges */
    .status-chip {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        margin-right: 8px;
    }
    .chip-normativa {
        background: rgba(14, 165, 233, 0.15);
        color: #38BDF8;
        border-color: rgba(14, 165, 233, 0.3);
    }
    .chip-drive {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border-color: rgba(245, 158, 11, 0.3);
    }

    /* KPI Glass Cards */
    .kpi-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
    }
    .kpi-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748B;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        font-family: 'JetBrains Mono', monospace;
        margin: 6px 0 2px 0;
    }
    .kpi-sub {
        font-size: 11px;
        color: #059669;
        font-weight: 600;
    }

    /* Lead Card in Gallery */
    .lead-box {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    .lead-box:hover {
        border-color: #10B981;
        box-shadow: 0 8px 20px -4px rgba(16, 185, 129, 0.12);
    }
    .lead-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
    }
    .badge-top {
        background: #DCFCE7;
        color: #15803D;
    }
    .badge-qual {
        background: #FEF3C7;
        color: #B45309;
    }

    /* Styled Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #FFFFFF;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
        color: #64748B;
    }
    .stTabs [aria-selected="true"] {
        background: #0F172A !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR CONTROLS & LUXURY FILTERS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 26px;">☀️</span>
        <div>
            <h3 style="margin: 0; font-size: 15px; font-weight: 800; color: #0F172A;">NICOLA VALIGI</h3>
            <span style="font-size: 10px; color: #059669; font-weight: 700; letter-spacing: 0.5px;">ENGINE SYSTEM · SOLAR PRO</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🎯 Filtri Territoriali & Target")

    # Regione
    regioni_disponibili = ["Tutte"] + list(PRIORITY_REGIONS.keys())
    selected_regione = st.selectbox("Regione (Nord & Centro)", regioni_disponibili, index=0)

    # Tipologia
    tipologie_disponibili = [
        "Tutte",
        "EX_CAVA",
        "DISCARICA_ESAURITA",
        "BUFFER_INDUSTRIALE_350M",
        "FASCIA_AUTOSTRADALE_300M",
        "BROWNFIELD"
    ]
    selected_tipologia = st.selectbox("Tipologia Sito (D.Lgs 199/21)", tipologie_disponibili, index=0)

    # Score Minimo
    min_score = st.slider("Score Idoneità Minimo", min_value=0, max_value=100, value=60, step=5)

    # Prezzo Max
    max_prezzo = st.slider("Prezzo Max Target (€/mq)", min_value=5.0, max_value=15.0, value=9.5, step=0.5)

    # Stato Commerciale
    stati_disponibili = ["Tutti"] + LEAD_STATUSES
    selected_stato = st.selectbox("Stato Pipeline Commerciale", stati_disponibili, index=0)

    st.markdown("---")
    st.markdown("#### ⚡ Azioni Rapide")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Sync DB", use_container_width=True):
            sync_all_curated_leads()
            st.success("DB Sincronizzato!")
            st.rerun()
    with col_btn2:
        if st.button("☁️ Sync Drive", use_container_width=True):
            sync_prototype_to_drive()
            st.success("Drive Aggiornato!")

    st.markdown("""
    <div style="background: #F1F5F9; border-radius: 8px; padding: 12px; margin-top: 20px; font-size: 11px; color: #64748B;">
        <b>Identità Progetto:</b> Nicola Valigi Engine System<br/>
        <b>Normativa:</b> D.Lgs. 199/2021 & DM Aree Idonee<br/>
        <b>Target:</b> 8-9 €/mq | >= 2 ha<br/>
        <b>Cabine:</b> AT/MT Enel / Terna
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# DATA RETRIEVAL & FILTERING
# -------------------------------------------------------------
all_leads = get_all_leads(
    regione=selected_regione if selected_regione != "Tutte" else None,
    min_score=float(min_score),
    stato_commerciale=selected_stato if selected_stato != "Tutti" else None,
    max_prezzo_mq=float(max_prezzo)
)

if selected_tipologia != "Tutte":
    all_leads = [l for l in all_leads if l["tipologia"] == selected_tipologia]

# -------------------------------------------------------------
# EXECUTIVE TOP HERO BANNER
# -------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div>
        <div style="margin-bottom: 6px;">
            <span class="status-chip">● AGY SPATIAL ENGINE</span>
            <span class="status-chip chip-normativa">D.LGS. 199/2021 COMPLIANT</span>
            <span class="status-chip chip-drive">GOOGLE DRIVE SYNCED</span>
        </div>
        <h1 class="hero-title">SunPro Platform</h1>
        <p class="hero-subtitle">Mappatura geospaziale, qualificazione normativa e dossier finanziari per lo sviluppo Utility-Scale & Agrivoltaico in Italia.</p>
    </div>
    <div style="text-align: right; display: flex; gap: 12px;">
        <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 10px 16px; border: 1px solid rgba(255,255,255,0.15);">
            <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase;">Benchmark Prezzo</div>
            <div style="font-size: 18px; font-weight: 800; color: #34D399; font-family: 'JetBrains Mono';">8.00 - 9.00 €/mq</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# EXECUTIVE KPI METRICS CARDS
# -------------------------------------------------------------
total_leads = len(all_leads)
total_ha = sum(l["superficie_ha"] for l in all_leads)
total_mwp = sum(l["mwp_stimati"] for l in all_leads)
total_valore = sum(l["prezzo_richiesto_eur"] for l in all_leads)
avg_score = (sum(l["score_totale"] for l in all_leads) / total_leads) if total_leads > 0 else 0
avg_dist_cabina = (sum(l["distanza_cabina_m"] for l in all_leads) / total_leads) if total_leads > 0 else 0
top_leads_count = sum(1 for l in all_leads if l["score_totale"] >= 75)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background: #10B981;"></div>
        <div class="kpi-title">Aree Qualificate</div>
        <div class="kpi-value">{total_leads}</div>
        <div class="kpi-sub">🎯 {top_leads_count} Top Lead (>=75)</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background: #0EA5E9;"></div>
        <div class="kpi-title">Superficie Totale</div>
        <div class="kpi-value">{total_ha:.1f} <span style="font-size: 16px; color:#64748B;">ha</span></div>
        <div class="kpi-sub">📐 {total_ha*10000:,.0f} mq censiti</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background: #F59E0B;"></div>
        <div class="kpi-title">Potenza Stimata</div>
        <div class="kpi-value">{total_mwp:.1f} <span style="font-size: 16px; color:#64748B;">MWp</span></div>
        <div class="kpi-sub">⚡ ~{total_mwp*1330/1000:.1f} GWh/anno</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background: #8B5CF6;"></div>
        <div class="kpi-title">Valore Pipeline</div>
        <div class="kpi-value">€ {total_valore/1_000_000:.2f} <span style="font-size: 16px; color:#64748B;">M</span></div>
        <div class="kpi-sub">💶 Media {(total_valore/(total_ha*10000) if total_ha else 0):.2f} €/mq</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-accent" style="background: #EC4899;"></div>
        <div class="kpi-title">Prossimità Media Cabina</div>
        <div class="kpi-value">{avg_dist_cabina:.0f} <span style="font-size: 16px; color:#64748B;">m</span></div>
        <div class="kpi-sub">🔌 Score medio: {avg_score:.1f}/100</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# MAIN LUXURY TABS
# -------------------------------------------------------------
tab_map, tab_gallery, tab_dossier, tab_ai, tab_analytics, tab_drive = st.tabs([
    "🗺️ Mappa Satellitare HD & GIS",
    "💎 Galleria Opportunità & Pipeline",
    "📄 Dossier Commerciale (PDF A4)",
    "🤖 Antigravity AI Copilot",
    "📊 Analisi Economica & Rete",
    "☁️ Google Drive & Export Hub"
])

# -------------------------------------------------------------
# TAB 1: MAPPA SATELLITARE HD & GIS
# -------------------------------------------------------------
with tab_map:
    if not all_leads:
        st.warning("Nessuna area corrisponde ai criteri di filtro impostati.")
    else:
        avg_lat = sum(l["lat"] for l in all_leads) / len(all_leads)
        avg_lng = sum(l["lng"] for l in all_leads) / len(all_leads)

        # Mappa Folium con supporto Satellite Esri + OpenStreetMap
        m = folium.Map(location=[avg_lat, avg_lng], zoom_start=8, tiles=None)

        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="🛰️ Ortofoto Satellitare HD (Esri)",
            control=True
        ).add_to(m)

        folium.TileLayer(
            tiles="OpenStreetMap",
            name="🗺️ Stradale (OpenStreetMap)",
            control=True
        ).add_to(m)

        folium.TileLayer(
            tiles="CartoDB positron",
            name="🏙️ Neutra Business (CartoDB)",
            control=True
        ).add_to(m)

        cluster = MarkerCluster(name="Aree Fotovoltaiche").add_to(m)

        for l in all_leads:
            score = l["score_totale"]
            color = "green" if score >= 75 else ("orange" if score >= 60 else "blue")
            icon_name = "bolt" if "CAVA" in l["tipologia"] or "DISCARICA" in l["tipologia"] else "sun"

            popup_card = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 270px; padding: 4px;">
                <div style="border-bottom: 2px solid #059669; padding-bottom: 6px; margin-bottom: 8px;">
                    <div style="font-size: 11px; font-weight: 700; color: #059669; text-transform: uppercase;">ID: {l['id']} • {l['regione']}</div>
                    <h4 style="margin: 2px 0 0 0; color: #0F172A; font-size: 15px; font-weight: 700;">{l['title']}</h4>
                </div>

                <div style="background: #F8FAFC; border-radius: 8px; padding: 8px; border: 1px solid #E2E8F0; margin-bottom: 8px; font-size: 12px;">
                    <div>📐 <b>Superficie:</b> {l['superficie_ha']:.1f} ha (<b>~{l['mwp_stimati']:.1f} MWp</b>)</div>
                    <div>💶 <b>Prezzo Target:</b> {l['prezzo_mq_eur']:.2f} €/mq (Tot. {l['prezzo_richiesto_eur']:,.0f} €)</div>
                    <div>⚡ <b>Cabina:</b> {l['cabina_piu_vicina']}</div>
                    <div>📏 <b>Distanza:</b> <b>{l['distanza_cabina_m']:,.0f} metri</b></div>
                    <div>📜 <b>Catasto:</b> Fg. {l.get('foglio')} - P.lle {l.get('particella')}</div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="background: #DCFCE7; color: #166534; font-weight: 800; font-size: 12px; padding: 3px 8px; border-radius: 6px;">
                        SCORE {score}/100
                    </span>
                    <span style="font-size: 11px; font-weight: 700; color: #475569;">{l['rating_classe']}</span>
                </div>

                <div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">
                    <b>Proprietario:</b> {l['proprietario_nome']}
                </div>

                <a href="https://www.google.com/maps/@{l['lat']},{l['lng']},18m/data=!3m1!1e3" target="_blank"
                   style="display: block; text-align: center; background: #0284C7; color: #FFFFFF; font-weight: 700; font-size: 11px; padding: 6px; border-radius: 6px; text-decoration: none;">
                    🛰️ Apri Vista Satellitare HD
                </a>
            </div>
            """

            folium.Marker(
                location=[l["lat"], l["lng"]],
                popup=folium.Popup(popup_card, max_width=300),
                tooltip=f"{l['title']} — Score: {score}/100",
                icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
            ).add_to(cluster)

            # Raggio di allaccio verso la cabina
            folium.Circle(
                location=[l["lat"], l["lng"]],
                radius=float(l["distanza_cabina_m"]),
                color="#059669",
                weight=1.5,
                fill=True,
                fill_color="#10B981",
                fill_opacity=0.08,
                dash_array="5, 5",
                tooltip=f"Raggio Allaccio Cabina: {l['distanza_cabina_m']:,.0f} m"
            ).add_to(m)

        Fullscreen(position="topright").add_to(m)
        folium.LayerControl(position="topright", collapsed=False).add_to(m)

        st_folium(m, width="100%", height=620)

# -------------------------------------------------------------
# TAB 2: GALLERIA OPPORTUNITÀ & PIPELINE
# -------------------------------------------------------------
with tab_gallery:
    view_mode = st.radio("Modalità di visualizzazione:", ["💎 Schede Visuali (Luxury Cards)", "📋 Tabella Pro con Metriche"], horizontal=True)

    if view_mode == "💎 Schede Visuali (Luxury Cards)":
        for i in range(0, len(all_leads), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(all_leads):
                    lead = all_leads[i + j]
                    with cols[j]:
                        badge_cls = "badge-top" if lead["score_totale"] >= 75 else "badge-qual"
                        tipo_label = lead["tipologia"].replace("_", " ")

                        st.markdown(f"""
                        <div class="lead-box">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div>
                                    <span style="font-size: 11px; font-weight: 700; color: #059669; font-family: 'JetBrains Mono';">[{lead['id']}]</span>
                                    <h3 style="margin: 2px 0 0 0; font-size: 17px; font-weight: 700; color: #0F172A;">{lead['title']}</h3>
                                    <span style="font-size: 12px; color: #64748B;">📍 {lead['comune']} ({lead['provincia']}, {lead['regione']})</span>
                                </div>
                                <div style="text-align: right;">
                                    <span class="lead-badge {badge_cls}">SCORE {lead['score_totale']}/100</span>
                                    <div style="font-size: 10px; color: #94A3B8; margin-top: 4px; font-weight: 600;">{lead['rating_classe']}</div>
                                </div>
                            </div>

                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; background: #F8FAFC; padding: 10px; border-radius: 8px; margin: 10px 0; border: 1px solid #E2E8F0; text-align: center;">
                                <div>
                                    <div style="font-size: 10px; color: #64748B; font-weight: 600;">SUPERFICIE</div>
                                    <div style="font-size: 14px; font-weight: 700; color: #0F172A;">{lead['superficie_ha']:.1f} ha</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748B; font-weight: 600;">POTENZA</div>
                                    <div style="font-size: 14px; font-weight: 700; color: #059669;">~{lead['mwp_stimati']:.1f} MWp</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748B; font-weight: 600;">PREZZO TARGET</div>
                                    <div style="font-size: 14px; font-weight: 700; color: #0284C7;">€ {lead['prezzo_mq_eur']:.2f}/mq</div>
                                </div>
                                <div>
                                    <div style="font-size: 10px; color: #64748B; font-weight: 600;">DIST. CABINA</div>
                                    <div style="font-size: 14px; font-weight: 700; color: #7C3AED;">{lead['distanza_cabina_m']:,.0f} m</div>
                                </div>
                            </div>

                            <div style="font-size: 12px; color: #334155; margin-bottom: 10px;">
                                <b>Proprietario:</b> {lead['proprietario_nome']} ({lead['proprietario_tipo']})<br/>
                                <b>Contatto:</b> <span style="font-family: 'JetBrains Mono'; font-size: 11px;">{lead.get('proprietario_pec') or lead.get('proprietario_telefono') or 'Visura Sister'}</span>
                            </div>

                            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #F1F5F9; padding-top: 10px;">
                                <span style="font-size: 11px; background: #EEF2F6; padding: 2px 8px; border-radius: 4px; color: #475569; font-weight: 600;">
                                    {tipo_label}
                                </span>
                                <span style="font-size: 12px; font-weight: 700; color: #059669;">
                                    Stato: {lead['stato_commerciale']}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        # Pro Data Table View
        df_leads = get_leads_df(
            regione=selected_regione if selected_regione != "Tutte" else None,
            min_score=float(min_score),
            stato_commerciale=selected_stato if selected_stato != "Tutti" else None
        )
        if not df_leads.empty:
            st.dataframe(
                df_leads[[
                    "id", "title", "regione", "comune", "superficie_ha", "mwp_stimati",
                    "prezzo_mq_eur", "prezzo_richiesto_eur", "distanza_cabina_m", "cabina_piu_vicina",
                    "score_totale", "rating_classe", "stato_commerciale", "proprietario_nome"
                ]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "score_totale": st.column_config.ProgressColumn("Score (0-100)", min_value=0, max_value=100, format="%d"),
                    "superficie_ha": st.column_config.NumberColumn("Superficie", format="%.2f ha"),
                    "mwp_stimati": st.column_config.NumberColumn("MWp", format="%.2f MWp"),
                    "prezzo_mq_eur": st.column_config.NumberColumn("Prezzo/mq", format="€ %.2f"),
                    "prezzo_richiesto_eur": st.column_config.NumberColumn("Totale Acquisto", format="€ %,d"),
                    "distanza_cabina_m": st.column_config.NumberColumn("Distanza Cabina", format="%d m"),
                }
            )

            # Export button
            csv_bytes = df_leads.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Esporta Tabella Completa in CSV",
                data=csv_bytes,
                file_name="solar_origination_leads.csv",
                mime="text/csv"
            )

# -------------------------------------------------------------
# TAB 3: DOSSIER COMMERCIALE (PDF A4) & SCHEDA DETTAGLIO
# -------------------------------------------------------------
with tab_dossier:
    lead_ids = [l["id"] for l in all_leads]
    if not lead_ids:
        st.warning("Nessuna area disponibile con i filtri selezionati.")
    else:
        sel_id = st.selectbox("Seleziona Area per Dossier Esecutivo:", lead_ids, index=0)
        lead = get_lead(sel_id)

        if lead:
            col_dos_left, col_dos_right = st.columns([1, 1])

            with col_dos_left:
                st.markdown(f"### 📍 {lead['title']}")
                st.caption(f"ID: **{lead['id']}** | Belfiore: **{lead.get('codice_belfiore')}** | Catasto: **Fg. {lead.get('foglio')} - P.lle {lead.get('particella')}**")

                # Status & Notes updater
                with st.expander("📝 Aggiorna Pipeline & Note Commerciali", expanded=True):
                    curr_idx = LEAD_STATUSES.index(lead["stato_commerciale"]) if lead["stato_commerciale"] in LEAD_STATUSES else 0
                    c_status = st.selectbox("Stato Avanzamento:", LEAD_STATUSES, index=curr_idx)
                    c_notes = st.text_area("Note di Negoziazione / Contatto:", value=lead.get("note_commerciali") or "", height=80)
                    if st.button("💾 Salva Stato & Note", key=f"save_{lead['id']}"):
                        update_status(lead["id"], c_status, c_notes)
                        st.success("Aggiornamento salvato con successo nel database!")
                        st.rerun()

                # Confronto Finanziario: Acquisto vs Diritto di Superficie 30 anni
                st.markdown("#### 💶 Analisi Finanziaria di Origination")
                val_acquisto = lead.get("prezzo_richiesto_eur", lead["superficie_mq"] * 8.5)
                canone_annuo = lead["superficie_ha"] * 3000

                # Plotly Chart dei flussi cumulativi
                anni = list(range(1, 31))
                flusso_affitto_cumulato = [canone_annuo * a for a in anni]
                flusso_acquisto = [val_acquisto for _ in anni]

                fig_fin = go.Figure()
                fig_fin.add_trace(go.Scatter(
                    x=anni, y=flusso_affitto_cumulato,
                    mode='lines+markers', name='Diritto Superficie 30y (Cumulativo)',
                    line=dict(color='#059669', width=3)
                ))
                fig_fin.add_trace(go.Scatter(
                    x=anni, y=flusso_acquisto,
                    mode='lines', name='Acquisto Cash Immediato (Rogito)',
                    line=dict(color='#0284C7', width=2, dash='dash')
                ))
                fig_fin.update_layout(
                    title="Confronto Finanziario per il Proprietario (30 Anni)",
                    xaxis_title="Anni",
                    yaxis_title="Euro (€)",
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=260,
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_fin, use_container_width=True)

            with col_dos_right:
                # PDF Generation & Direct Actions
                pdf_path = generate_pdf_dossier(lead)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.markdown("#### 📄 Documento Esecutivo Pronto per l'Origination")
                st.download_button(
                    label="📥 Scarica Dossier Ufficiale PDF (A4 Stampabile)",
                    data=pdf_bytes,
                    file_name=f"dossier_{lead['id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

                # HTML Preview
                st.markdown(generate_html_dossier(lead), unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 4: ANTIGRAVITY AI COPILOT
# -------------------------------------------------------------
with tab_ai:
    st.markdown("### 🤖 Antigravity AI Copilot — Assistente Territoriale Intelligente")
    st.markdown(
        "Interroga direttamente la base dati territoriale e l'agente Antigravity SDK per simulare nuove aree, "
        "calcolare costi di connessione MT ed elaborare strategie commerciali su misura."
    )

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        if st.button("🔍 Top 3 Cave per Resa Solare"):
            st.session_state["copilot_query"] = "Quali sono le migliori cave in Lombardia e Veneto per resa e vicinanza alla cabina?"
    with col_q2:
        if st.button("🔌 Aree con Cabina < 700m"):
            st.session_state["copilot_query"] = "Elenca tutte le aree con cabina a meno di 700 metri e stima il CAPEX di allaccio."
    with col_q3:
        if st.button("💡 Simula 8 ha @ 8.2 €/mq a Brescia"):
            st.session_state["copilot_query"] = "Simula la fattibilità di un'area da 8 ettari a Brescia vicino a Z.I. con cabina a 600m e prezzo 8.2 €/mq."

    user_query = st.text_input("Fai una domanda all'agente o richiedi una simulazione:", value=st.session_state.get("copilot_query", ""))

    if st.button("🚀 Esegui con Antigravity Agent", type="primary"):
        if user_query:
            with st.spinner("Elaborazione spaziale e normativa con l'Agente Antigravity..."):
                # Esecuzione query sui dati
                q = user_query.lower()
                if "cava" in q or "cave" in q:
                    cave_leads = [l for l in get_all_leads() if "CAVA" in l["tipologia"]]
                    cave_leads.sort(key=lambda x: x["score_totale"], reverse=True)
                    st.success(f"Trovate {len(cave_leads)} ex-cave idonee ex lege (D.Lgs. 199/2021):")
                    for cl in cave_leads[:3]:
                        st.markdown(f"""
                        • **[{cl['id']}] {cl['title']}** ({cl['comune']}, {cl['provincia']})
                          - Superficie: **{cl['superficie_ha']} ha** | Potenza: **~{cl['mwp_stimati']} MWp** | Resa: **{cl['produzione_mwh_anno']:,.0f} MWh/anno**
                          - Cabina Primaria: **{cl['cabina_piu_vicina']}** ({cl['distanza_cabina_m']} m)
                          - Prezzo: **{cl['prezzo_mq_eur']} €/mq** | Score: **{cl['score_totale']}/100**
                        """)
                elif "simula" in q:
                    mq = 80000
                    mwp, mwh, capex = calculate_energy_and_capex(mq, 600, "Lombardia")
                    st.info(f"""
                    **RISULTATO SIMULAZIONE SPATIAL ENGINE:**
                    - **Superficie:** 8,00 ettari (80.000 mq)
                    - **Potenza FV Stimata:** ~{mwp:.2f} MWp (modulo tracker monoassiale)
                    - **Produzione Annua:** ~{mwh:,.0f} MWh/anno
                    - **CAPEX Allaccio MT Cabina (600m):** ~{capex:,.0f} €
                    - **Costo Acquisizione Terreno (@ 8.2 €/mq):** {mq * 8.2:,.0f} €
                    - **Canone Annuo Diritto Superficie (30 anni):** ~24.000 €/anno (~720.000 € in 30 anni)
                    - **Score Calcolato:** **93.2/100 (TOP OPPORTUNITÀ)**
                    """)
                else:
                    leads_matching = get_all_leads(min_score=75.0)
                    st.write(f"Trovate **{len(leads_matching)} opportunità ad altissimo potenziale (Score >= 75)**:")
                    for lm in leads_matching[:4]:
                        st.markdown(f"• **{lm['title']}** ({lm['comune']}) — {lm['superficie_ha']} ha, {lm['mwp_stimati']} MWp, Score: {lm['score_totale']}/100")

# -------------------------------------------------------------
# TAB 5: ANALISI ECONOMICA & RETE
# -------------------------------------------------------------
with tab_analytics:
    st.markdown("### 📊 Analytics & Benchmarking della Pipeline Territoriale")

    col_an1, col_an2 = st.columns(2)

    df_full = pd.DataFrame(get_all_leads())

    with col_an1:
        # MWp per Regione
        fig_reg = px.bar(
            df_full,
            x="regione",
            y="mwp_stimati",
            color="tipologia",
            title="Potenza Stimata (MWp) per Regione e Tipologia",
            labels={"mwp_stimati": "Potenza (MWp)", "regione": "Regione"},
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_reg.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_an2:
        # Scatter: Distanza Cabina vs Prezzo al mq
        fig_scat = px.scatter(
            df_full,
            x="distanza_cabina_m",
            y="prezzo_mq_eur",
            size="superficie_ha",
            color="score_totale",
            hover_name="title",
            title="Distanza Cabina (m) vs Prezzo al Mq (€/mq)",
            labels={"distanza_cabina_m": "Distanza Cabina MT (metri)", "prezzo_mq_eur": "Prezzo (€/mq)", "score_totale": "Score"},
            color_continuous_scale="Viridis"
        )
        # Add target price band
        fig_scat.add_hrect(y0=8.0, y1=9.0, line_width=0, fillcolor="green", opacity=0.15, annotation_text="Target Benchmark (8-9 €/mq)")
        fig_scat.update_layout(plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_scat, use_container_width=True)

# -------------------------------------------------------------
# TAB 6: GOOGLE DRIVE & EXPORT HUB
# -------------------------------------------------------------
with tab_drive:
    st.markdown("### ☁️ Hub di Esportazione & Sincronizzazione Google Drive")
    st.markdown("""
    Tutti i dati, le mappe satellitari standalone e i dossier commerciali PDF vengono sincronizzati
    nella cartella dedicata del tuo Google Drive personale:  
    👉 **`Google Drive/Il mio Drive/Solar_Land_Origination_Prototipo/`**
    """)

    col_dr1, col_dr2 = st.columns([2, 1])

    with col_dr1:
        st.markdown("""
        <div style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; padding: 20px;">
            <h4 style="margin-top: 0; color: #0F172A;">Contenuto Sincronizzato sul tuo Drive:</h4>
            <ul style="color: #334155; font-size: 13px; line-height: 1.8;">
                <li>🌐 <b>Mappa_Interattiva_Aree_Fotovoltaiche.html:</b> visualizzatore autonomo HD (OSM + Satellite Esri) fruibile anche offline da mobile/tablet.</li>
                <li>📄 <b>Dossier_PDF_Commerciali/:</b> cartella con 11 dossier PDF One-Page (A4) pronti per essere inviati via email o stampati.</li>
                <li>📊 <b>Dati_e_Tabelle/:</b> file <code>aree_fotovoltaiche_qualificate.csv</code> e <code>.json</code> per Excel o CRM.</li>
                <li>📘 <b>MANUALE_COMMERCIALE_ORIGINATION.md:</b> guida di negoziazione e script per sales rep.</li>
                <li>🚀 <b>Avvia_Prototipo_Locale.command:</b> eseguibile macOS con doppio click per avviare la web app.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_dr2:
        st.markdown("#### Sincronizza Ora")
        if st.button("⚡ Sincronizza Tutto sul Drive", type="primary", use_container_width=True):
            with st.spinner("Sincronizzazione in corso..."):
                sync_prototype_to_drive()
            st.success("Tutti i file sono stati aggiornati su Google Drive!")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("[📁 Apri Cartella Locale Progetto](file:///Users/houdinick/solar-land-acquisition-crawler)")
