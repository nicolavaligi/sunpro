"""
Applicazione Desktop & Dashboard per l'Acquisizione di Terreni Fotovoltaici.
Mappe geospaziali, scoring multicriterio (D.Lgs. 199/2021), pipeline commerciale e generazione dossier PDF.
Autore: Houdinick (Nicola Valigi)
"""

import json
from pathlib import Path
import folium
from folium.plugins import MarkerCluster
import pandas as pd
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

# Configurazione Pagina Streamlit
st.set_page_config(
    page_title="Solar Land Origination | Houdinick",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inizializza DB
init_db()

# Custom CSS per interfaccia moderna
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .metric-val {
        font-size: 24px;
        font-weight: bold;
        color: #059669;
    }
    .metric-lbl {
        font-size: 12px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-top {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    }
    .badge-qual {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar: Filtri Commerciali
st.sidebar.image("https://images.unsplash.com/photo-1509391365360-2e959784a276?w=400&q=80", use_container_width=True)
st.sidebar.title("☀️ Solar Land Origination")
st.sidebar.markdown("**Filtri di Ricerca & Qualificazione**")

# Selezione Regione
regioni_disponibili = ["Tutte"] + list(PRIORITY_REGIONS.keys())
selected_regione = st.sidebar.selectbox("Regione (Nord & Centro)", regioni_disponibili, index=0)

# Filtro Tipologia
tipologie_disponibili = [
    "Tutte",
    "EX_CAVA",
    "DISCARICA_ESAURITA",
    "BUFFER_INDUSTRIALE_350M",
    "FASCIA_AUTOSTRADALE_300M",
    "BROWNFIELD"
]
selected_tipologia = st.sidebar.selectbox("Tipologia Sito (D.Lgs 199/21)", tipologie_disponibili, index=0)

# Slider Score
min_score = st.sidebar.slider("Score Idoneità Minimo (0-100)", min_value=0, max_value=100, value=50, step=5)

# Slider Prezzo Max
max_prezzo = st.sidebar.slider("Prezzo Max (€/mq)", min_value=5.0, max_value=15.0, value=10.0, step=0.5)

# Filtro Stato Commerciale
stati_disponibili = ["Tutti"] + LEAD_STATUSES
selected_stato = st.sidebar.selectbox("Stato Pipeline Commerciale", stati_disponibili, index=0)

# Sincronizzazione / Reset rapido
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Ricarica Lead Curati"):
    sync_all_curated_leads()
    st.sidebar.success("Database risincronizzato!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Sviluppo proprietario Houdinick (Nicola Valigi) • Antigravity Engine")

# Caricamento Dati
all_leads = get_all_leads(
    regione=selected_regione if selected_regione != "Tutte" else None,
    min_score=float(min_score),
    stato_commerciale=selected_stato if selected_stato != "Tutti" else None,
    max_prezzo_mq=float(max_prezzo)
)

if selected_tipologia != "Tutte":
    all_leads = [l for l in all_leads if l["tipologia"] == selected_tipologia]

# Intestazione Principale
st.markdown('<div class="main-header">⚡ Pipeline Acquisizione Terreni Fotovoltaici</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Mappatura geospaziale, qualificazione D.Lgs. 199/2021 (350m Z.I., 300m autostrade, cave/discariche) e dossier commerciali.</div>',
    unsafe_allow_html=True
)

# KPI Metrics Dashboard
total_leads = len(all_leads)
total_ha = sum(l["superficie_ha"] for l in all_leads)
total_mwp = sum(l["mwp_stimati"] for l in all_leads)
avg_score = (sum(l["score_totale"] for l in all_leads) / total_leads) if total_leads > 0 else 0
top_leads_count = sum(1 for l in all_leads if l["score_totale"] >= 75)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Aree Idonee Trovate", f"{total_leads}")
with col2:
    st.metric("Top Opportunity (>=75)", f"{top_leads_count}", delta=f"{top_leads_count/total_leads*100:.0f}%" if total_leads else None)
with col3:
    st.metric("Superficie Totale", f"{total_ha:.1f} ha")
with col4:
    st.metric("Potenza Stimata", f"{total_mwp:.1f} MWp")
with col5:
    st.metric("Score Medio", f"{avg_score:.1f}/100")

st.markdown("---")

# Tab Principali
tab_map, tab_table, tab_dossier, tab_add = st.tabs([
    "🗺️ Mappa Geospaziale Interattiva",
    "📋 Pipeline & Opportunità",
    "📄 Scheda Lead & Dossier Commerciale",
    "➕ Scansione / Nuovo Lead"
])

# ----------------------------------------------------
# TAB 1: MAPPA GEOSPAZIALE INTERATTIVA
# ----------------------------------------------------
with tab_map:
    if not all_leads:
        st.warning("Nessuna area corrisponde ai filtri selezionati nella barra laterale.")
    else:
        # Centro mappa sulla media delle coordinate
        avg_lat = sum(l["lat"] for l in all_leads) / len(all_leads)
        avg_lng = sum(l["lng"] for l in all_leads) / len(all_leads)

        m = folium.Map(location=[avg_lat, avg_lng], zoom_start=8, tiles="CartoDB positron")

        marker_cluster = MarkerCluster(name="Aree Fotovoltaiche").add_to(m)

        for l in all_leads:
            score = l["score_totale"]
            color = "green" if score >= 75 else ("orange" if score >= 60 else "blue")
            icon_name = "bolt" if "CAVA" in l["tipologia"] or "DISCARICA" in l["tipologia"] else "sun"

            popup_html = f"""
            <div style="font-family: Arial; width: 240px;">
                <h4 style="margin: 0 0 5px 0; color: #1e293b;">{l['title']}</h4>
                <b>ID:</b> {l['id']}<br/>
                <b>Comune:</b> {l['comune']} ({l['provincia']})<br/>
                <b>Superficie:</b> {l['superficie_ha']:.1f} ha ({l['mwp_stimati']:.1f} MWp)<br/>
                <b>Prezzo:</b> {l['prezzo_mq_eur']:.2f} €/mq ({l['prezzo_richiesto_eur']:,.0f} €)<br/>
                <b>Cabina:</b> {l['cabina_piu_vicina']} ({l['distanza_cabina_m']:,.0f} m)<br/>
                <b>Score:</b> <span style="font-size: 14px; font-weight: bold; color: {color};">{score}/100</span> ({l['rating_classe']})<br/>
                <b>Stato:</b> {l['stato_commerciale']}<br/>
                <hr style="margin: 6px 0;"/>
                <i>Fg. {l.get('foglio')} - P.lla {l.get('particella')}</i>
            </div>
            """

            folium.Marker(
                location=[l["lat"], l["lng"]],
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=f"{l['title']} ({score}/100)",
                icon=folium.Icon(color=color, icon=icon_name, prefix="fa")
            ).add_to(marker_cluster)

            # Cerchio buffer della cabina elettrica
            folium.Circle(
                location=[l["lat"], l["lng"]],
                radius=float(l["distanza_cabina_m"]),
                color="#059669",
                weight=1,
                fill=False,
                dash_array="5, 5",
                tooltip=f"Distanza Cabina: {l['distanza_cabina_m']:,.0f} m"
            ).add_to(m)

        st_folium(m, width="100%", height=560)

# ----------------------------------------------------
# TAB 2: PIPELINE & TABELLA OPPORTUNITÀ
# ----------------------------------------------------
with tab_table:
    if not all_leads:
        st.info("Nessuna opportunità trovata con i filtri correnti.")
    else:
        # Prepara visualizzazione tabellare pulita
        table_rows = []
        for l in all_leads:
            table_rows.append({
                "ID": l["id"],
                "Titolo / Nome Area": l["title"],
                "Regione": l["regione"],
                "Provincia": l["provincia"],
                "Comune": l["comune"],
                "Superficie (ha)": l["superficie_ha"],
                "MWp Stimati": l["mwp_stimati"],
                "Prezzo (€/mq)": l["prezzo_mq_eur"],
                "Tipologia": l["tipologia"],
                "Dist. Cabina (m)": l["distanza_cabina_m"],
                "Score": l["score_totale"],
                "Rating": l["rating_classe"],
                "Stato": l["stato_commerciale"],
                "Proprietario": l["proprietario_nome"]
            })
        df_display = pd.DataFrame(table_rows)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn("Score (0-100)", min_value=0, max_value=100, format="%d"),
                "Prezzo (€/mq)": st.column_config.NumberColumn(format="€ %.2f"),
                "Superficie (ha)": st.column_config.NumberColumn(format="%.2f ha"),
                "MWp Stimati": st.column_config.NumberColumn(format="%.2f MWp"),
                "Dist. Cabina (m)": st.column_config.NumberColumn(format="%d m")
            }
        )

        # Download CSV
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Esporta Tutte le Opportunità in CSV",
            data=csv_data,
            file_name=f"opportunita_fotovoltaico_export.csv",
            mime="text/csv"
        )

# ----------------------------------------------------
# TAB 3: SCHEDA LEAD & DOSSIER COMMERCIALE (PDF)
# ----------------------------------------------------
with tab_dossier:
    lead_ids = [l["id"] for l in all_leads]
    if not lead_ids:
        st.warning("Nessun lead disponibile per i criteri selezionati.")
    else:
        selected_lead_id = st.selectbox("Seleziona Area / Lead per Dossier Dettagliato:", lead_ids, index=0)
        curr_lead = get_lead(selected_lead_id)

        if curr_lead:
            col_d1, col_d2 = st.columns([2, 1])

            with col_d1:
                st.subheader(f"{curr_lead['title']}")
                st.caption(f"ID univoco: {curr_lead['id']} | Registrato: {curr_lead.get('created_at', 'Oggi')}")

            with col_d2:
                # Gestione Stato Commerciale e Salvataggio
                st.markdown("##### Aggiorna Stato Pipeline")
                curr_status_idx = LEAD_STATUSES.index(curr_lead["stato_commerciale"]) if curr_lead["stato_commerciale"] in LEAD_STATUSES else 0
                new_status = st.selectbox("Stato Contatto:", LEAD_STATUSES, index=curr_status_idx, key=f"status_{curr_lead['id']}")
                new_notes = st.text_input("Note Commerciali:", value=curr_lead.get("note_commerciali") or "", key=f"notes_{curr_lead['id']}")

                if st.button("💾 Salva Modifiche Lead", key=f"btn_save_{curr_lead['id']}"):
                    update_status(curr_lead["id"], new_status, new_notes)
                    st.success("Stato aggiornato con successo!")
                    st.rerun()

            st.markdown("---")

            # Generazione PDF e Pulsante di Download
            col_pdf1, col_pdf2 = st.columns([1, 3])
            with col_pdf1:
                pdf_path = generate_pdf_dossier(curr_lead)
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="📄 Scarica Dossier Ufficiale PDF (A4)",
                    data=pdf_bytes,
                    file_name=f"dossier_fotovoltaico_{curr_lead['id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with col_pdf2:
                wms_url = get_cadastral_wms_url(curr_lead['lat'], curr_lead['lng'])
                st.markdown(f"[🛰️ Apri Vista Satellitare Alta Risoluzione ({curr_lead['lat']:.4f}, {curr_lead['lng']:.4f})]({wms_url})")

            # Anteprima Dossier HTML
            st.markdown("---")
            st.markdown("#### Anteprima Scheda Commerciale")
            html_preview = generate_html_dossier(curr_lead)
            st.markdown(html_preview, unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 4: SCANSIONE TERRITORIALE / AGGIUNTA NUOVO SITO
# ----------------------------------------------------
with tab_add:
    st.subheader("➕ Inserimento / Qualificazione Nuova Area Fotovoltaica")
    st.write("Inserisci i parametri di una nuova area individuata sul territorio per eseguire il calcolo automatico di idoneità, MWp, costi di allaccio e score.")

    with st.form("new_lead_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            f_title = st.text_input("Titolo o Denominazione Sito", "Nuova Ex Cava / Area Produttiva")
            f_regione = st.selectbox("Regione", list(PRIORITY_REGIONS.keys()))
            f_provincia = st.text_input("Provincia", "Brescia")
            f_comune = st.text_input("Comune", "Ghedi")
            f_foglio = st.text_input("Foglio Catastale", "12")
            f_particella = st.text_input("Particella/e", "45, 46")
            f_lat = st.number_input("Latitudine", value=45.4000, format="%.5f")
            f_lng = st.number_input("Longitudine", value=10.3500, format="%.5f")

        with col_f2:
            f_superficie_ha = st.number_input("Superficie in Ettari (min 2 ha)", min_value=2.0, max_value=200.0, value=5.5, step=0.5)
            f_prezzo_mq = st.number_input("Prezzo Richiesto (€/mq)", min_value=1.0, max_value=30.0, value=8.5, step=0.1)
            f_tipologia = st.selectbox("Tipologia Sito", [
                "EX_CAVA",
                "DISCARICA_ESAURITA",
                "BUFFER_INDUSTRIALE_350M",
                "FASCIA_AUTOSTRADALE_300M",
                "BROWNFIELD"
            ])
            f_dist_ind = st.number_input("Distanza da Zona Industriale (metri)", value=150, step=10)
            f_dist_auto = st.number_input("Distanza da Autostrada (metri)", value=250, step=10)
            f_nome_auto = st.text_input("Nome Autostrada / Raccordo", "A4 Milano-Venezia")
            f_dist_cabina = st.number_input("Distanza da Cabina Primaria AT/MT (metri)", value=800, step=50)
            f_cabina_nome = st.text_input("Nome Cabina Primaria", "CP Ghedi 132/15 kV")

        st.markdown("##### Dati Proprietario / Contatto Commerciale")
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            f_prop_nome = st.text_input("Nome Intestatario / Società", "Immobiliare Agricola S.r.l.")
            f_prop_tipo = st.selectbox("Tipo Soggetto", ["PERSONA_GIURIDICA", "PERSONA_FISICA", "CURATELA_FALLIMENTARE"])
            f_prop_piva = st.text_input("P.IVA o Codice Fiscale", "01234567890")
        with col_o2:
            f_prop_pec = st.text_input("PEC Ufficiale", "info@pec.it")
            f_prop_tel = st.text_input("Telefono di Contatto", "+39 030 1234567")

        submit_btn = st.form_submit_button("⚡ Qualifica e Salva nel Database")

        if submit_btn:
            new_id = f"LEAD-{f_provincia[:3].upper()}-{int(f_lat*100)%1000:03d}"
            mq_tot = f_superficie_ha * 10_000

            raw_entry = {
                "id": new_id,
                "title": f_title,
                "regione": f_regione,
                "provincia": f_provincia,
                "comune": f_comune,
                "foglio": f_foglio,
                "particella": f_particella,
                "lat": f_lat,
                "lng": f_lng,
                "superficie_mq": mq_tot,
                "prezzo_mq_eur": f_prezzo_mq,
                "prezzo_richiesto_eur": mq_tot * f_prezzo_mq,
                "tipologia": f_tipologia,
                "distanza_zona_industriale_m": f_dist_ind,
                "distanza_autostrada_m": f_dist_auto,
                "nome_autostrada": f_nome_auto,
                "distanza_cabina_m": f_dist_cabina,
                "cabina_piu_vicina": f_cabina_nome,
                "proprietario_nome": f_prop_nome,
                "proprietario_tipo": f_prop_tipo,
                "proprietario_piva": f_prop_piva,
                "proprietario_pec": f_prop_pec,
                "proprietario_telefono": f_prop_tel,
                "fonte_origine": "INSERIMENTO_DIRETTO_MANUALE"
            }

            saved = process_and_save_lead(raw_entry)
            st.success(f"Area {new_id} registrata con successo! Score calcolato: {saved['score_totale']}/100 ({saved['rating_classe']})")
            st.rerun()
