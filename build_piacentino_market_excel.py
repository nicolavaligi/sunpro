# ==============================================================================
# PROPRIETARY AND CONFIDENTIAL — NICOLA VALIGI (HOUDINICK)
# SunPro Geo-Intelligence 3D — Piacentino Real Estate & Market Comparables Excel Builder
# Autore & Titolare Esclusivo della Proprietà Intellettuale: Nicola Valigi (Houdinick)
# Email: 305862309+nicolavaligi@users.noreply.github.com | GitHub: nicolavaligi
# Copyright (c) 2026 Nicola Valigi. All Rights Reserved.
# ==============================================================================
"""
Genera il Workbook Excel completo e dettagliato con:
1. Quadro Comparativo di Mercato per tutti i 13 Comuni del Cluster Piacentino (A1 & A21)
   distinguendo rigorosamente tra:
   - VAM Amministrativo (BURERT Regione Emilia-Romagna)
   - Prezzi di Reale Compravendita Agricola (Rogiti CREA / CCIAA Piacenza) in €/mq, €/ha e €/Pertica Piacentina
   - Prezzi Richiesti sugli Annunci Immobiliari in Zona (Idealista, Immobiliare.it, Immobiliare 7 Valli, ecc.)
   - Basi d'Asta Giudiziaria (Tribunale / IVG Piacenza)
   - Prezzi Terreni Edificabili Industriali / Logistici (Zona D: Le Mose, Castel San Giovanni, Fiorenzuola, Caorso)
   - Comparabili Sviluppo Fotovoltaico Utility-Scale (Acquisto vs Diritto di Superficie 30 anni vs Affitto Agrario)
2. Tabella Esecutiva Fasce di Prezzo & Confronto Formule Contrattuali
3. Scheda Analitica dei 90 Lotti in Aperta Campagna con tutte le metriche tecniche + comparabili immobiliari reali
4. Scheda Analitica dei 26 Lotti in Riserva Periurbana
5. Casi Reali di Mercato Rilevati in Provincia di Piacenza & Vademecum Negoziale
"""

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
WEB_DIR = BASE_DIR / "web"
DESKTOP_DIR = Path("/Users/houdinick/Desktop")

PERTICA_PIACENTINA_MQ = 762.0186
PERTICHE_PER_HA = 10000.0 / PERTICA_PIACENTINA_MQ  # 13.123039

# ==============================================================================
# DATABASE REAL ESTATE & COMPARABILI PER I 13 COMUNI DEL CLUSTER PIACENTINO
# ==============================================================================
COMUNE_MARKET_DATA: Dict[str, Dict[str, Any]] = {
    "Cadeo": {
        "asse": "A1",
        "regione_agraria": "Reg. Agr. 6 (Basso Arda) / 4",
        "vam_uff_mq": 5.45,
        "rogito_min_mq": 5.10,
        "rogito_max_mq": 6.30,
        "rogito_med_mq": 5.75,
        "asking_min_mq": 5.60,
        "asking_max_mq": 7.15,
        "asking_med_mq": 6.40,
        "asta_min_mq": 1.10,
        "asta_max_mq": 2.40,
        "ind_min_mq": 70.0,
        "ind_max_mq": 95.0,
        "polo_ind": "Comparto artigianale Via Emilia / Roveleto di Cadeo",
        "affitto_agr_ha": 640,
        "fv_buy_min_mq": 6.80,
        "fv_buy_max_mq": 7.55,
        "fv_buy_cons_mq": 7.20,
        "fv_dds_ha": 3100,
        "pressione_logistica": "Bassa (Fascia interclusa tra A1 e Ferrovia AV)",
        "priorita_negoziale": "TOP — Priorità 1",
        "note_mercato": (
            "19 lotti in aperta campagna stretti tra A1 e linea AV Milano-Bologna (Saliceto/Roveleto). "
            "L'effetto 'fascia interclusa' riduce il valore per grandi macchine agricole e azzera l'edificabilità residenziale: "
            "ottima propensione dei proprietari a vendere a 6,80-7,55 €/mq (5.180-5.750 €/pertica) o cedere DDS."
        ),
    },
    "Rottofreno": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 5 (Pianura di Piacenza)",
        "vam_uff_mq": 5.65,
        "rogito_min_mq": 5.00,
        "rogito_max_mq": 6.25,
        "rogito_med_mq": 5.65,
        "asking_min_mq": 5.40,
        "asking_max_mq": 6.80,
        "asking_med_mq": 6.10,
        "asta_min_mq": 1.00,
        "asta_max_mq": 2.30,
        "ind_min_mq": 75.0,
        "ind_max_mq": 105.0,
        "polo_ind": "Zona artigianale San Nicolò a Trebbia / Cattagnina",
        "affitto_agr_ha": 650,
        "fv_buy_min_mq": 7.20,
        "fv_buy_max_mq": 7.85,
        "fv_buy_cons_mq": 7.50,
        "fv_dds_ha": 3300,
        "pressione_logistica": "Media-Bassa lungo l'asta A21 agricola",
        "priorita_negoziale": "TOP — Priorità 1 (Hub Rete 132 kV)",
        "note_mercato": (
            "Snodo elettrico #1 della mappa (Stazione 132 kV Rottofreno e CP AC001E01165 a 1,4-2,0 km). "
            "Seminativi irrigui scambiati a rogito intorno a 4.300 €/pertica (~5,65 €/mq). "
            "Offerta FV a 7,30-7,85 €/mq (5.560-5.980 €/pertica) incorpora un premio netto del +32% sul mercato reale."
        ),
    },
    "Caorso": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 6 (Basso Arda)",
        "vam_uff_mq": 5.55,
        "rogito_min_mq": 4.85,
        "rogito_max_mq": 6.00,
        "rogito_med_mq": 5.45,
        "asking_min_mq": 5.20,
        "asking_max_mq": 6.50,
        "asking_med_mq": 5.85,
        "asta_min_mq": 0.90,
        "asta_max_mq": 2.20,
        "ind_min_mq": 85.0,
        "ind_max_mq": 100.0,
        "polo_ind": "Comparto produttivo/logistico Svincolo A21 Caorso",
        "affitto_agr_ha": 620,
        "fv_buy_min_mq": 7.00,
        "fv_buy_max_mq": 7.75,
        "fv_buy_cons_mq": 7.35,
        "fv_dds_ha": 3200,
        "pressione_logistica": "Media vicino al casello; Bassa nelle frazioni (Fossadello/Zerbio)",
        "priorita_negoziale": "TOP — Priorità 1 (Nodo RTN 380 kV)",
        "note_mercato": (
            "Presenza della Stazione RTN Terna 380/132 kV di Caorso. I lotti produttivi al casello quotano 85-100 €/mq, "
            "ma i grandi fondi agricoli a Fossadello/Muradolo scambiano a 3.900-4.500 €/pertica (5,10-5,90 €/mq). "
            "Ottimo margine per chiudere i 9 lotti in aperta campagna entro 7,35 €/mq."
        ),
    },
    "Piacenza": {
        "asse": "A1/A21",
        "regione_agraria": "Reg. Agr. 5 (Pianura di Piacenza)",
        "vam_uff_mq": 5.65,
        "rogito_min_mq": 5.50,
        "rogito_max_mq": 6.80,
        "rogito_med_mq": 6.15,
        "asking_min_mq": 6.00,
        "asking_max_mq": 7.60,
        "asking_med_mq": 6.80,
        "asta_min_mq": 1.30,
        "asta_max_mq": 2.60,
        "ind_min_mq": 80.0,
        "ind_max_mq": 140.0,
        "polo_ind": "Polo Logistico Le Mose / Caorsana / Piacenza Sud (80-85 €/mq grezzo, 120-140 €/mq urbanizzato)",
        "affitto_agr_ha": 700,
        "fv_buy_min_mq": 7.50,
        "fv_buy_max_mq": 8.00,
        "fv_buy_cons_mq": 7.80,
        "fv_dds_ha": 3500,
        "pressione_logistica": "Molto Alta a Piacenza Sud/Le Mose; Media a Roncaglia/Mortizza",
        "priorita_negoziale": "Selettiva (3 Aperta Campagna OK; 12 Periurbani solo DDS)",
        "note_mercato": (
            "Il polo logistico Le Mose/Piacenza Sud spinge i terreni industriali a 80-140 €/mq. "
            "Per questo 12 lotti su 15 sono classificati come 'Riserve Periurbane'. Puntare in acquisto sui 3 lotti agricoli "
            "di Roncaglia/Mortizza (7,50-8,00 €/mq) e offrire DDS (3.500 €/ha/anno) sui lotti in fascia di rispetto inedificabile."
        ),
    },
    "Fiorenzuola d'Arda": {
        "asse": "A1",
        "regione_agraria": "Reg. Agr. 6 (Basso Arda)",
        "vam_uff_mq": 5.45,
        "rogito_min_mq": 5.00,
        "rogito_max_mq": 6.20,
        "rogito_med_mq": 5.60,
        "asking_min_mq": 5.50,
        "asking_max_mq": 6.80,
        "asking_med_mq": 6.15,
        "asta_min_mq": 1.00,
        "asta_max_mq": 2.30,
        "ind_min_mq": 80.0,
        "ind_max_mq": 116.0,
        "polo_ind": "Polo Logistico Svincolo A1 Fiorenzuola / Barabasca (80-116 €/mq su Demer/Idealista)",
        "affitto_agr_ha": 630,
        "fv_buy_min_mq": 7.00,
        "fv_buy_max_mq": 7.60,
        "fv_buy_cons_mq": 7.30,
        "fv_dds_ha": 3100,
        "pressione_logistica": "Alta intorno al casello A1; Bassa lungo l'asta agricola",
        "priorita_negoziale": "Alta sugli 8 lotti in Aperta Campagna",
        "note_mercato": (
            "Mercato bipolare: i lotti artigianali/logistici vicino al casello A1 scambiano a 100-116 €/mq, "
            "mentre i seminativi in aperta campagna si rogitano a 4.000-4.700 €/pertica (5,25-6,15 €/mq). "
            "Sugli 8 lotti in aperta campagna l'offerta a 7,30 €/mq (5.560 €/pertica) è altamente competitiva."
        ),
    },
    "Castelvetro Piacentino": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 6 (Basso Arda)",
        "vam_uff_mq": 5.50,
        "rogito_min_mq": 4.75,
        "rogito_max_mq": 5.85,
        "rogito_med_mq": 5.30,
        "asking_min_mq": 5.10,
        "asking_max_mq": 6.30,
        "asking_med_mq": 5.70,
        "asta_min_mq": 0.85,
        "asta_max_mq": 2.10,
        "ind_min_mq": 60.0,
        "ind_max_mq": 85.0,
        "polo_ind": "Asse produttivo SS10 Padana Inferiore verso Cremona",
        "affitto_agr_ha": 600,
        "fv_buy_min_mq": 6.80,
        "fv_buy_max_mq": 7.50,
        "fv_buy_cons_mq": 7.15,
        "fv_dds_ha": 3000,
        "pressione_logistica": "Bassa lungo il corridoio autostradale A21",
        "priorita_negoziale": "Alta — Ottimo rapporto qualità/prezzo",
        "note_mercato": (
            "Terreni alluvionali fertili al confine cremonese con quotazioni fondiarie moderate (3.800-4.500 €/pertica). "
            "Bassa competizione logistica lungo il tracciato A21: 8 lotti in aperta campagna acquisibili a 6,80-7,50 €/mq."
        ),
    },
    "Monticelli d'Ongina": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 6 (Basso Arda)",
        "vam_uff_mq": 5.50,
        "rogito_min_mq": 4.80,
        "rogito_max_mq": 5.90,
        "rogito_med_mq": 5.35,
        "asking_min_mq": 5.15,
        "asking_max_mq": 6.35,
        "asking_med_mq": 5.75,
        "asta_min_mq": 0.85,
        "asta_max_mq": 2.10,
        "ind_min_mq": 55.0,
        "ind_max_mq": 80.0,
        "polo_ind": "Aree artigianali locali lungo SP10 / Via Edison",
        "affitto_agr_ha": 610,
        "fv_buy_min_mq": 6.90,
        "fv_buy_max_mq": 7.65,
        "fv_buy_cons_mq": 7.25,
        "fv_dds_ha": 3100,
        "pressione_logistica": "Bassa (Economia prevalentemente agricola/orticola)",
        "priorita_negoziale": "Alta (Presenza Cabina Primaria AC001E01173)",
        "note_mercato": (
            "Ospita la Cabina Primaria ARERA AC001E01173 e la Stazione RFI 132 kV Monticelli FS. "
            "Prezzi agricoli reali molto stabili (~5,35 €/mq medi a rogito = 4.075 €/pertica) e costi di cavidotto MT minimi."
        ),
    },
    "San Pietro in Cerro": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 6 (Basso Arda)",
        "vam_uff_mq": 5.50,
        "rogito_min_mq": 4.60,
        "rogito_max_mq": 5.70,
        "rogito_med_mq": 5.15,
        "asking_min_mq": 4.90,
        "asking_max_mq": 6.10,
        "asking_med_mq": 5.50,
        "asta_min_mq": 0.80,
        "asta_max_mq": 2.00,
        "ind_min_mq": 50.0,
        "ind_max_mq": 70.0,
        "polo_ind": "Piccoli lotti artigianali locali (assenza di grandi poli logistici)",
        "affitto_agr_ha": 580,
        "fv_buy_min_mq": 6.60,
        "fv_buy_max_mq": 7.50,
        "fv_buy_cons_mq": 7.05,
        "fv_dds_ha": 3000,
        "pressione_logistica": "Nulla / Puramente Rurale",
        "priorita_negoziale": "BEST PICK ASSOLUTO (Score 99,5/100)",
        "note_mercato": (
            "Comune puramente agricolo senza inflazione da logistica (rogiti tra 3.500 e 4.350 €/pertica = 4,60-5,70 €/mq). "
            "Include il Lotto PC-A21-011 (Fg.2 Part.1, 8,29 ha a 49m dalla linea 132 kV e 200m dalla Stazione Monticelli FS)."
        ),
    },
    "Pontenure": {
        "asse": "A1",
        "regione_agraria": "Reg. Agr. 5 (Pianura di Piacenza)",
        "vam_uff_mq": 5.85,
        "rogito_min_mq": 5.50,
        "rogito_max_mq": 6.70,
        "rogito_med_mq": 6.10,
        "asking_min_mq": 6.00,
        "asking_max_mq": 7.35,
        "asking_med_mq": 6.65,
        "asta_min_mq": 1.20,
        "asta_max_mq": 2.50,
        "ind_min_mq": 85.0,
        "ind_max_mq": 110.0,
        "polo_ind": "Comparto industriale Via Emilia Est / Zona Stazione",
        "affitto_agr_ha": 680,
        "fv_buy_min_mq": 7.40,
        "fv_buy_max_mq": 7.90,
        "fv_buy_cons_mq": 7.65,
        "fv_dds_ha": 3300,
        "pressione_logistica": "Media lungo Via Emilia; Bassa nella fascia tra A1 e Ferrovia AV",
        "priorita_negoziale": "TOP — Priorità 1 (Cabina Primaria Pontenure)",
        "note_mercato": (
            "Terreni molto ricercati da aziende agricole strutturate (rogiti ~6,10 €/mq = 4.650 €/pertica; "
            "annunci per 50 pertiche irrigue fino a 7,15 €/mq). I 6 lotti in aperta campagna (Valconasso) sono però "
            "interclusi tra A1 e AV ferroviaria, agevolando la chiusura a 7,40-7,90 €/mq."
        ),
    },
    "Castel San Giovanni": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 3 / 5 (Val Tidone - Pianura)",
        "vam_uff_mq": 5.60,
        "rogito_min_mq": 4.90,
        "rogito_max_mq": 6.20,
        "rogito_med_mq": 5.55,
        "asking_min_mq": 5.30,
        "asking_max_mq": 6.80,
        "asking_med_mq": 6.05,
        "asta_min_mq": 1.10,
        "asta_max_mq": 2.40,
        "ind_min_mq": 110.0,
        "ind_max_mq": 150.0,
        "polo_ind": "Mega-Hub Logistico Castel San Giovanni (Amazon / A21: 110-150 €/mq urbanizzato; 40 €/mq attesa)",
        "affitto_agr_ha": 640,
        "fv_buy_min_mq": 7.40,
        "fv_buy_max_mq": 8.00,
        "fv_buy_cons_mq": 7.70,
        "fv_dds_ha": 3400,
        "pressione_logistica": "Altissima vicino al Polo Logistico; Bassa verso Pievetta/Po",
        "priorita_negoziale": "Verifica CDU Preliminare Obbligatoria",
        "note_mercato": (
            "Nel raggio del Polo Logistico i terreni di trasformazione partono da 40 €/mq fino a 150 €/mq urbanizzati. "
            "Fuori dal perimetro logistico (frazioni agricole verso il Po) la terra resta a 5,00-6,20 €/mq. "
            "Verificare il PUG prima dell'offerta o proporre Diritto di Superficie."
        ),
    },
    "Calendasco": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 5 (Pianura di Piacenza)",
        "vam_uff_mq": 5.65,
        "rogito_min_mq": 4.85,
        "rogito_max_mq": 5.95,
        "rogito_med_mq": 5.40,
        "asking_min_mq": 5.20,
        "asking_max_mq": 6.40,
        "asking_med_mq": 5.80,
        "asta_min_mq": 0.90,
        "asta_max_mq": 2.15,
        "ind_min_mq": 65.0,
        "ind_max_mq": 90.0,
        "polo_ind": "Comparto produttivo SP10 / Ponte Trebbia",
        "affitto_agr_ha": 610,
        "fv_buy_min_mq": 6.90,
        "fv_buy_max_mq": 7.60,
        "fv_buy_cons_mq": 7.25,
        "fv_dds_ha": 3000,
        "pressione_logistica": "Bassa lungo il corridoio A21",
        "priorita_negoziale": "Alta (Bassa speculazione)",
        "note_mercato": (
            "Mercato fondiario stabile e agricolo (rogiti 3.700-4.530 €/pertica = 4,85-5,95 €/mq). "
            "Assenza di pressione dai grandi hub logistici sui 4 lotti in aperta campagna lungo A21."
        ),
    },
    "Alseno": {
        "asse": "A1",
        "regione_agraria": "Reg. Agr. 4 / 6 (Basso Arda)",
        "vam_uff_mq": 5.45,
        "rogito_min_mq": 4.50,
        "rogito_max_mq": 5.55,
        "rogito_med_mq": 5.05,
        "asking_min_mq": 4.80,
        "asking_max_mq": 5.95,
        "asking_med_mq": 5.40,
        "asta_min_mq": 0.80,
        "asta_max_mq": 1.95,
        "ind_min_mq": 55.0,
        "ind_max_mq": 75.0,
        "polo_ind": "Piccole aree artigianali Via Emilia (Castelnuovo Fogliani)",
        "affitto_agr_ha": 570,
        "fv_buy_min_mq": 6.50,
        "fv_buy_max_mq": 7.20,
        "fv_buy_cons_mq": 6.85,
        "fv_dds_ha": 2900,
        "pressione_logistica": "Nulla sul tratto autostradale A1 (Chiaravalle)",
        "priorita_negoziale": "Molto Facile (Prezzi agricoli puri)",
        "note_mercato": (
            "Tratto A1 vicino all'Abbazia di Chiaravalle della Colomba (verificare fasce di rispetto paesaggistiche comunali): "
            "valori fondiari tra i più contenuti della pianura (3.500-4.250 €/pertica), trattativa agevole sotto i 7,20 €/mq."
        ),
    },
    "Sarmato": {
        "asse": "A21",
        "regione_agraria": "Reg. Agr. 5 (Pianura di Piacenza)",
        "vam_uff_mq": 5.60,
        "rogito_min_mq": 4.95,
        "rogito_max_mq": 6.05,
        "rogito_med_mq": 5.50,
        "asking_min_mq": 5.30,
        "asking_max_mq": 6.50,
        "asking_med_mq": 5.90,
        "asta_min_mq": 0.95,
        "asta_max_mq": 2.20,
        "ind_min_mq": 70.0,
        "ind_max_mq": 95.0,
        "polo_ind": "Polo energetico/industriale Ex Zuccherificio / Centrale Edison 220 kV",
        "affitto_agr_ha": 620,
        "fv_buy_min_mq": 7.00,
        "fv_buy_max_mq": 7.60,
        "fv_buy_cons_mq": 7.30,
        "fv_dds_ha": 3200,
        "pressione_logistica": "Bassa (Alta vocazione energetica storica)",
        "priorita_negoziale": "Alta (Vicino Stazione 220 kV Edison Sarmato)",
        "note_mercato": (
            "Comune a storica vocazione energetica (centrale termoelettrica Edison 220 kV, biometano, ex zuccherificio). "
            "Proprietari abituati a contratti di servitù e diritto di superficie energetico."
        ),
    },
}


def style_range(ws, min_col, min_row, max_col, max_row, font=None, fill=None, border=None, alignment=None, num_format=None):
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        for cell in row:
            if font:
                cell.font = font
            if fill:
                cell.fill = fill
            if border:
                cell.border = border
            if alignment:
                cell.alignment = alignment
            if num_format:
                cell.number_format = num_format


def build_comprehensive_market_excel(lots: List[Dict[str, Any]], out_paths: List[Path]):
    wb = openpyxl.Workbook()

    # Fogli del Workbook
    ws_comuni = wb.active
    ws_comuni.title = "1_Quadro_Mercato_13_Comuni"
    ws_fasce = wb.create_sheet("2_Fasce_Prezzo_e_Contratti")
    ws_aperta = wb.create_sheet("3_Aperta_Campagna_90_Lotti")
    ws_peri = wb.create_sheet("4_Riserve_Periurbane_26_Lotti")
    ws_casi = wb.create_sheet("5_Casi_Reali_e_Guida_Trattativa")

    # Palette Stili Executive SunPro
    navy_fill = PatternFill("solid", fgColor="0B1528")
    slate_fill = PatternFill("solid", fgColor="1E293B")
    emerald_fill = PatternFill("solid", fgColor="059669")
    emerald_soft = PatternFill("solid", fgColor="D1FAE5")
    blue_soft = PatternFill("solid", fgColor="DBEAFE")
    amber_soft = PatternFill("solid", fgColor="FEF3C7")
    rose_soft = PatternFill("solid", fgColor="FFE4E6")
    gray_soft = PatternFill("solid", fgColor="F8FAFC")
    zebra_fill = PatternFill("solid", fgColor="F1F5F9")

    title_font = Font(name="Calibri", size=15, bold=True, color="0B1528")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="334155")
    sec_font = Font(name="Calibri", size=12, bold=True, color="059669")
    hdr_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=10, bold=True, color="0F172A")
    reg_font = Font(name="Calibri", size=10, bold=False, color="0F172A")
    blue_bold = Font(name="Calibri", size=10, bold=True, color="1D4ED8")
    green_bold = Font(name="Calibri", size=10, bold=True, color="047857")
    amber_bold = Font(name="Calibri", size=10, bold=True, color="B45309")
    red_bold = Font(name="Calibri", size=10, bold=True, color="BE123C")
    link_font = Font(name="Calibri", size=10, bold=True, color="0284C7", underline="single")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )
    thick_bottom = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="medium", color="0B1528"),
        bottom=Side(style="double", color="0B1528"),
    )

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    right_align = Alignment(horizontal="right", vertical="center", wrap_text=True)

    # ==========================================================================
    # FOGLIO 1: QUADRO MERCATO 13 COMUNI (ROGITI REALI vs PORTALI vs VAM vs ZONA D)
    # ==========================================================================
    ws_comuni.views.sheetView[0].showGridLines = True
    ws_comuni["A1"] = "SUNPRO GEO-INTELLIGENCE 3D — ANALISI MERCATO IMMOBILIARE REALE & COMPARABILI PER I 13 COMUNI DEL CLUSTER PIACENTINO (A1 & A21)"
    ws_comuni["A1"].font = title_font
    ws_comuni["A2"] = (
        "Confronto tra Valori Amministrativi (VAM), Compravendite Reali a Rogito (CREA / CCIAA Piacenza), Annunci Immobiliari in Zona (Idealista / Immobiliare.it / Agenzie Locali), "
        "Aste Giudiziarie (IVG Piacenza), Terreni Industriali Zona D e Offerte Fotovoltaico Utility-Scale. (1 Pertica Piacentina = 762,02 mq | 1 Ettaro = 13,123 Pertiche)."
    )
    ws_comuni["A2"].font = subtitle_font

    headers_f1 = [
        "Comune",
        "Asse Autostrada",
        "Regione Agraria Ufficiale",
        "Lotti Tot. Mappa",
        "Lotti Aperta Campagna",
        "Lotti Riserve Periurbane",
        "Sup. Totale Mappa (ha)",
        "Sup. Entro 300m (ha)",
        "Sup. Entro 300m (Pertiche P.ne)",
        "VAM Ufficiale Amministrativo (€/mq)",
        "VAM Ufficiale (€/ha)",
        "ROGITO REALE Agricolo Min (€/mq)",
        "ROGITO REALE Agricolo Max (€/mq)",
        "ROGITO REALE Agricolo Media (€/mq)",
        "ROGITO REALE Media (€/Ettaro)",
        "ROGITO REALE Media (€/Pertica 762mq)",
        "ANNUNCI PORTALI Richiesta Min (€/mq)",
        "ANNUNCI PORTALI Richiesta Max (€/mq)",
        "ANNUNCI PORTALI Media (€/Pertica 762mq)",
        "ASTE GIUDIZIARIE Base CTU (€/mq)",
        "TERRENO INDUSTRIALE Zona D Min (€/mq)",
        "TERRENO INDUSTRIALE Zona D Max (€/mq)",
        "Polo Produttivo / Logistico di Riferimento",
        "Affitto Agrario Reale (€/ha/anno)",
        "Affitto Agrario Reale (€/Pertica/anno)",
        "Canone DDS Fotovoltaico (€/ha/anno)",
        "Canone DDS Fotovoltaico (€/Pertica/anno)",
        "Moltiplicatore Rendita DDS vs Affitto",
        "OFFERTA ACQUISTO FV Consigliata (€/mq)",
        "OFFERTA ACQUISTO FV (€/Ettaro)",
        "OFFERTA ACQUISTO FV (€/Pertica 762mq)",
        "Premio % Offerta FV su Rogito Reale",
        "Pressione Speculativa / Logistica",
        "Priorità & Strategia Negoziale",
        "Note di Mercato & Comparabili Locali",
    ]

    for col_idx, h in enumerate(headers_f1, 1):
        c = ws_comuni.cell(4, col_idx, h)
        c.fill = navy_fill if col_idx <= 11 else (emerald_fill if 12 <= col_idx <= 19 else (slate_fill if 20 <= col_idx <= 23 else navy_fill))
        c.font = hdr_font
        c.alignment = center_align
        c.border = thin_border
    ws_comuni.row_dimensions[4].height = 36

    # Raggruppa statistiche lotti per comune
    com_stats: Dict[str, Dict[str, Any]] = {}
    for cm in COMUNE_MARKET_DATA:
        sub = [x for x in lots if x["comune"] == cm]
        ap = [x for x in sub if x["gruppo"] == "APERTA_CAMPAGNA"]
        pe = [x for x in sub if x["gruppo"] != "APERTA_CAMPAGNA"]
        com_stats[cm] = {
            "tot": len(sub),
            "aperta": len(ap),
            "peri": len(pe),
            "ha_tot": round(sum(x["sup_tot_ha"] for x in sub), 2),
            "ha_300": round(sum(x["sup_300m_ha"] for x in sub), 2),
        }

    sorted_comuni = sorted(COMUNE_MARKET_DATA.keys(), key=lambda c: (-com_stats[c]["aperta"], -com_stats[c]["ha_300"]))

    for idx, cm in enumerate(sorted_comuni, 1):
        r = 4 + idx
        ws_comuni.row_dimensions[r].height = 34
        m = COMUNE_MARKET_DATA[cm]
        st = com_stats[cm]

        row_data = [
            cm,
            m["asse"],
            m["regione_agraria"],
            st["tot"],
            st["aperta"],
            st["peri"],
            st["ha_tot"],
            st["ha_300"],
            f"=H{r}*{PERTICHE_PER_HA:.4f}",
            m["vam_uff_mq"],
            f"=J{r}*10000",
            m["rogito_min_mq"],
            m["rogito_max_mq"],
            m["rogito_med_mq"],
            f"=N{r}*10000",
            f"=N{r}*{PERTICA_PIACENTINA_MQ:.2f}",
            m["asking_min_mq"],
            m["asking_max_mq"],
            f"=((Q{r}+R{r})/2)*{PERTICA_PIACENTINA_MQ:.2f}",
            f"{m['asta_min_mq']:.2f} - {m['asta_max_mq']:.2f} €/mq",
            m["ind_min_mq"],
            m["ind_max_mq"],
            m["polo_ind"],
            m["affitto_agr_ha"],
            f"=X{r}/{PERTICHE_PER_HA:.4f}",
            m["fv_dds_ha"],
            f"=Z{r}/{PERTICHE_PER_HA:.4f}",
            f"=Z{r}/X{r}",
            m["fv_buy_cons_mq"],
            f"=AC{r}*10000",
            f"=AC{r}*{PERTICA_PIACENTINA_MQ:.2f}",
            f"=(AC{r}-N{r})/N{r}",
            m["pressione_logistica"],
            m["priorita_negoziale"],
            m["note_mercato"],
        ]

        for col_idx, val in enumerate(row_data, 1):
            c = ws_comuni.cell(r, col_idx, val)
            c.border = thin_border
            c.font = bold_font if col_idx in (1, 14, 16, 29, 31, 34) else reg_font
            c.alignment = left_align if col_idx in (1, 3, 23, 33, 34, 35) else (center_align if col_idx in (2, 4, 5, 6, 20) else right_align)

            # Formati numerici e colori dedicati
            if col_idx in (7, 8, 9):
                c.number_format = "#,##0.0"
            elif col_idx in (10, 12, 13, 14, 17, 18, 21, 22, 29):
                c.number_format = '#,##0.00 "€/mq"'
            elif col_idx in (11, 15, 24, 26, 30):
                c.number_format = '#,##0 "€"'
            elif col_idx in (16, 19, 25, 27, 31):
                c.number_format = '#,##0 "€/pert."'
            elif col_idx == 28:
                c.number_format = '0.0"x"'
                c.font = green_bold
            elif col_idx == 32:
                c.number_format = '+0.0%'
                c.font = green_bold

            if col_idx in (14, 15, 16):
                c.fill = blue_soft
                c.font = blue_bold
            elif col_idx in (21, 22):
                c.fill = rose_soft
            elif col_idx in (29, 30, 31, 32):
                c.fill = emerald_soft
                c.font = green_bold
            elif col_idx in (26, 27):
                c.fill = amber_soft
                c.font = amber_bold

    # Riga Totali / Medie Foglio 1
    tot_r = 4 + len(sorted_comuni) + 1
    ws_comuni.row_dimensions[tot_r].height = 26
    ws_comuni.cell(tot_r, 1, "TOTALE / MEDIA PROVINCIALE CLUSTER").font = bold_font
    ws_comuni.cell(tot_r, 4, f"=SUM(D5:D{tot_r-1})")
    ws_comuni.cell(tot_r, 5, f"=SUM(E5:E{tot_r-1})")
    ws_comuni.cell(tot_r, 6, f"=SUM(F5:F{tot_r-1})")
    ws_comuni.cell(tot_r, 7, f"=SUM(G5:G{tot_r-1})").number_format = "#,##0.0"
    ws_comuni.cell(tot_r, 8, f"=SUM(H5:H{tot_r-1})").number_format = "#,##0.0"
    ws_comuni.cell(tot_r, 9, f"=SUM(I5:I{tot_r-1})").number_format = "#,##0.0"
    ws_comuni.cell(tot_r, 10, f"=AVERAGE(J5:J{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 11, f"=AVERAGE(K5:K{tot_r-1})").number_format = '#,##0 "€"'
    ws_comuni.cell(tot_r, 12, f"=AVERAGE(L5:L{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 13, f"=AVERAGE(M5:M{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 14, f"=AVERAGE(N5:N{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 15, f"=AVERAGE(O5:O{tot_r-1})").number_format = '#,##0 "€"'
    ws_comuni.cell(tot_r, 16, f"=AVERAGE(P5:P{tot_r-1})").number_format = '#,##0 "€/pert."'
    ws_comuni.cell(tot_r, 17, f"=AVERAGE(Q5:Q{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 18, f"=AVERAGE(R5:R{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 19, f"=AVERAGE(S5:S{tot_r-1})").number_format = '#,##0 "€/pert."'
    ws_comuni.cell(tot_r, 21, f"=AVERAGE(U5:U{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 22, f"=AVERAGE(V5:V{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 24, f"=AVERAGE(X5:X{tot_r-1})").number_format = '#,##0 "€"'
    ws_comuni.cell(tot_r, 25, f"=AVERAGE(Y5:Y{tot_r-1})").number_format = '#,##0 "€/pert."'
    ws_comuni.cell(tot_r, 26, f"=AVERAGE(Z5:Z{tot_r-1})").number_format = '#,##0 "€"'
    ws_comuni.cell(tot_r, 27, f"=AVERAGE(AA5:AA{tot_r-1})").number_format = '#,##0 "€/pert."'
    ws_comuni.cell(tot_r, 28, f"=AVERAGE(AB5:AB{tot_r-1})").number_format = '0.0"x"'
    ws_comuni.cell(tot_r, 29, f"=AVERAGE(AC5:AC{tot_r-1})").number_format = '#,##0.00 "€/mq"'
    ws_comuni.cell(tot_r, 30, f"=AVERAGE(AD5:AD{tot_r-1})").number_format = '#,##0 "€"'
    ws_comuni.cell(tot_r, 31, f"=AVERAGE(AE5:AE{tot_r-1})").number_format = '#,##0 "€/pert."'
    ws_comuni.cell(tot_r, 32, f"=AVERAGE(AF5:AF{tot_r-1})").number_format = '+0.0%'
    style_range(ws_comuni, 1, tot_r, len(headers_f1), tot_r, font=bold_font, fill=gray_soft, border=thick_bottom)

    ws_comuni.freeze_panes = "B5"

    # ==========================================================================
    # FOGLIO 2: FASCE DI PREZZO, CONTRATTI E DISTINZIONE FONTI (OMI vs VAM vs ROGITI)
    # ==========================================================================
    ws_fasce.views.sheetView[0].showGridLines = True
    ws_fasce["A1"] = "QUADRO SINTETICO DELLE 5 FASCE DI PREZZO E DELLE FORMULE CONTRATTUALI NEL PIACENTINO"
    ws_fasce["A1"].font = title_font
    ws_fasce["A2"] = "Unità di misura locale: 1 Pertica Piacentina = 762,0186 mq  |  1 Ettaro (10.000 mq) = 13,123 Pertiche Piacentine"
    ws_fasce["A2"].font = subtitle_font

    ws_fasce["A4"] = "A. LE 5 FASCE DI PREZZO DEI TERRENI NELLA PIANURA PIACENTINA (A1 & A21)"
    ws_fasce["A4"].font = sec_font

    h_fasce = [
        "Fascia / Segmento di Mercato",
        "Natura del Dato",
        "Prezzo Min (€/mq)",
        "Prezzo Max (€/mq)",
        "Prezzo a Ettaro (€/ha)",
        "Prezzo a Pertica Piacentina (762 mq)",
        "Fonte Ufficiale / Riscontro Mercato",
        "Impatto sui 116 Lotti in Mappa (piacentino.html)",
    ]
    for idx, h in enumerate(h_fasce, 1):
        c = ws_fasce.cell(5, idx, h)
        c.fill = navy_fill
        c.font = hdr_font
        c.alignment = center_align
        c.border = thin_border
    ws_fasce.row_dimensions[5].height = 28

    fasce_rows = [
        (
            "1. Aste Giudiziarie Agricole (Base d'Asta Ribassata)",
            "Vendita Forzata / Esecuzioni",
            0.80,
            2.50,
            "8.000 – 25.000 €/ha",
            "610 – 1.905 €/pertica",
            "Tribunale di Piacenza / IVG Parma-Piacenza / PVP Giustizia",
            "Terreni spesso gravati da contratti d'affitto opponibili o prelazione del coltivatore insediato.",
        ),
        (
            "2. Valore Agricolo Medio (VAM Ufficiale)",
            "Valore Amministrativo / Espropri",
            4.80,
            5.85,
            "48.000 – 58.500 €/ha",
            "3.658 – 4.458 €/pertica",
            "Commissione Provinciale Espropri Piacenza (BURERT Regione ER — Reg. Agr. 5 e 6)",
            "Base amministrativa caricata in SunPro per verificare lo scostamento del prezzo richiesto.",
        ),
        (
            "3. Compravendita Agricola Reale (Rogiti Notarili)",
            "REALE VENDITA (Transato Effettivo)",
            4.60,
            6.80,
            "46.000 – 68.000 €/ha",
            "3.505 – 5.182 €/pertica",
            "Indagine Mercato Fondiario CREA + Osservatorio ISMEA + Camera di Commercio Piacenza",
            "Riferimento reale dei 90 Lotti in Aperta Campagna (seminativo irriguo a mais/pomodoro).",
        ),
        (
            "4. Annunci Immobiliari in Zona (Asking Price)",
            "Richiesta Iniziale Proprietari",
            5.20,
            7.35,
            "52.000 – 73.500 €/ha",
            "3.962 – 5.600 €/pertica",
            "Idealista, Immobiliare.it, Trovacasa, Immobiliare 7 Valli (es. 50 pertiche a 275.000 €)",
            "Include un margine di trattativa medio dell'8-12% rispetto al prezzo finale di rogito.",
        ),
        (
            "5. Target Acquisizione Sviluppo Fotovoltaico",
            "REALE OFFERTA OPERATORI FV",
            6.50,
            8.00,
            "65.000 – 80.000 €/ha",
            "4.953 – 6.096 €/pertica",
            "Comparabili Sviluppatori Utility-Scale Nord Italia (Sunprime, Solare Industriale, Nibo Green)",
            "Fascia target dei 90 Lotti in Aperta Campagna: riconosce un premio del +20/+35% sul rogito agricolo.",
        ),
        (
            "6. Terreno Periurbano / Attesa Logistica",
            "Aspettativa Speculativa",
            10.00,
            40.00,
            "100.000 – 400.000 €/ha",
            "7.620 – 30.480 €/pertica",
            "Annunci Casa.it / Idealista per grandi aree agricole contigue a poli logistici (es. Castel S.G.)",
            "Riguarda i 26 Lotti 'Riserve Periurbane': non acquistare in piena proprietà se >8 €/mq, offrire DDS.",
        ),
        (
            "7. Terreno Industriale / Logistico Urbanizzato (Zona D)",
            "REALE VENDITA EDIFICABILE",
            80.00,
            150.00,
            "800.000 – 1.500.000 €/ha",
            "Non quotato a pertica (solo €/mq)",
            "Annunci Immobiliare.it / Idealista / Demer (Le Mose 80-140 €/mq, Castel S.G. 110-150 €/mq, Fiorenzuola 80-116 €/mq)",
            "Escluso dal Gatekeeper SunPro: costo del suolo incompatibile con impianti fotovoltaici a terra.",
        ),
    ]

    for i, row_vals in enumerate(fasce_rows, 1):
        r = 5 + i
        ws_fasce.row_dimensions[r].height = 28
        for c_idx, val in enumerate(row_vals, 1):
            c = ws_fasce.cell(r, c_idx, val)
            c.border = thin_border
            c.font = bold_font if c_idx in (1, 5, 6) else reg_font
            c.alignment = left_align if c_idx in (1, 2, 7, 8) else (right_align if c_idx in (3, 4) else center_align)
            if c_idx in (3, 4):
                c.number_format = '#,##0.00 "€/mq"'
            if i == 3:
                c.fill = blue_soft
            elif i == 5:
                c.fill = emerald_soft
            elif i == 7:
                c.fill = rose_soft

    # Sezione B: Confronto Formule Contrattuali
    ws_fasce["A15"] = "B. CONFRONTO ECONOMICO E LEGALE DELLE 3 FORMULE CONTRATTUALI PER IL PROPRIETARIO PIACENTINO"
    ws_fasce["A15"].font = sec_font

    h_contr = [
        "Formula Contrattuale",
        "Valore al mq",
        "Valore per Ettaro (10.000 mq)",
        "Valore per Pertica Piacentina (762 mq)",
        "Incasso su Lotto Medio da 10 Ettari (131,2 Pertiche)",
        "Proprietà del Terreno a Fine Vita",
        "Diritto di Prelazione Confinanti (CD / IAP)",
        "Quando Usarla nella Trattativa SunPro",
    ]
    for idx, h in enumerate(h_contr, 1):
        c = ws_fasce.cell(16, idx, h)
        c.fill = navy_fill
        c.font = hdr_font
        c.alignment = center_align
        c.border = thin_border
    ws_fasce.row_dimensions[16].height = 28

    contr_rows = [
        (
            "1. Affitto Agrario Ordinario (L. 203/1982)",
            "0,06 – 0,07 €/mq/anno",
            "580 – 700 €/ha/anno",
            "44 – 53 €/pertica/anno",
            "6.200 €/anno (186.000 € in 30 anni)",
            "Resta al proprietario",
            "Sì (in caso di futura vendita del fondo)",
            "È la baseline attuale del proprietario: il fotovoltaico offre da 4,5x a 5,2x tanto.",
        ),
        (
            "2. Diritto di Superficie Fotovoltaico 30 Anni (Art. 952 c.c.)",
            "0,29 – 0,35 €/mq/anno (Target: 0,30)",
            "2.900 – 3.500 €/ha/anno (Target: 3.000 €)",
            "221 – 267 €/pertica/anno (Target: 229 €)",
            "30.000 €/anno (900.000 € cumulati in 30 anni)",
            "Torna al proprietario dopo 30 anni (con fideiussione ripristino)",
            "NO — ESENTE PRELAZIONE AGRARIA (Cassazione consolidata)",
            "Ideale se ci sono confinanti Coltivatori Diretti ostili o per proprietari patrimonialisti.",
        ),
        (
            "3. Acquisto Piena Proprietà per Fotovoltaico (Rogito Definitivo)",
            "6,50 – 8,00 €/mq una tantum",
            "65.000 – 80.000 €/ha una tantum",
            "4.953 – 6.096 €/pertica una tantum",
            "650.000 – 800.000 € incassati subito al rogito",
            "Passa definitivamente a SunPro / SPV",
            "SÌ — 30 giorni dalla notifica a confinanti CD/IAP o affittuario",
            "Ideale quando il proprietario vuole liquidità immediata e non ci sono confinanti CD/IAP.",
        ),
    ]
    for i, row_vals in enumerate(contr_rows, 1):
        r = 16 + i
        ws_fasce.row_dimensions[r].height = 30
        for c_idx, val in enumerate(row_vals, 1):
            c = ws_fasce.cell(r, c_idx, val)
            c.border = thin_border
            c.font = bold_font if c_idx in (1, 3, 4, 5, 7) else reg_font
            c.alignment = left_align if c_idx in (1, 6, 7, 8) else center_align
            if i == 2:
                c.fill = amber_soft
            elif i == 3:
                c.fill = emerald_soft

    for col_idx in range(1, 9):
        ws_fasce.column_dimensions[get_column_letter(col_idx)].width = 26
    ws_fasce.column_dimensions["A"].width = 36
    ws_fasce.column_dimensions["G"].width = 42
    ws_fasce.column_dimensions["H"].width = 48

    # ==========================================================================
    # FOGLI 3 & 4: DETTAGLIO DEI 90 LOTTI APERTA CAMPAGNA E 26 RISERVE PERIURBANE
    # ==========================================================================
    headers_lotti = [
        "#",
        "ID Lotto",
        "Coorte / Origine",
        "Priorità Visura Sister",
        "Comune",
        "Belfiore",
        "Foglio",
        "Particella",
        "Sup. Totale (ha)",
        "Sup. Entro 300m (ha)",
        "Sup. Totale (Pertiche P.ne)",
        "Sup. ≤300m (Pertiche P.ne)",
        "Autostrada",
        "Dist. Asse (m)",
        "Dist. Linea AT (m)",
        "kV Linea AT",
        "Stazione Elettrica OSM",
        "Dist. Stazione (km)",
        "Cabina Primaria ARERA",
        "Cavidotto MT 1.30x (m)",
        "CAPEX Allaccio TICA (€)",
        "Potenza Totale (MWp)",
        "Potenza ≤300m (MWp)",
        "Producibilità Tracker (MWh/a)",
        "VAM Ufficiale (€/mq)",
        "ROGITO REALE Agricolo Comune (€/mq)",
        "ROGITO REALE Agricolo (€/Pertica)",
        "Valore Mercato Agricolo Reale Lotto (€)",
        "Annunci Portali Comune (€/mq)",
        "Terreno Industriale Zona D Comune (€/mq)",
        "Offerta FV Consigliata SunPro (€/mq)",
        "Offerta FV Consigliata (€/Pertica)",
        "Valore Offerta Consigliata Lotto (€)",
        "Spesa Max Tetto Mandato 8 €/mq (€)",
        "Affitto Agrario Attuale Stimato (€/anno)",
        "Canone DDS FV 30y (3.000 €/ha/a)",
        "Incasso Proprietario DDS 30 Anni (€)",
        "Score SunPro",
        "Lat",
        "Lon",
        "Ortofoto Google",
        "Note Tecniche e di Mercato",
        "Intestatario (da Visura Sister)",
        "Prezzo Richiesto (€/mq)",
        "Equivalente Richiesto (€/Pertica)",
        "Entro Tetto 8 €/mq?",
    ]

    def populate_lots_sheet(ws, subset: List[Dict[str, Any]], sheet_title: str):
        ws.views.sheetView[0].showGridLines = True
        ws["A1"] = sheet_title
        ws["A1"].font = title_font
        ws["A2"] = (
            "Ogni lotto integra: Dati Catastali WMS AdE, Conversione in Pertiche Piacentine (762 mq), Rete AT/MT e CAPEX TICA, "
            "VAM Amministrativo, Prezzo Reale di Compravendita Agricola (Rogiti CREA/CCIAA), Annunci Portali, Terreni Industriali Zona D e Calcolatore Trattativa."
        )
        ws["A2"].font = subtitle_font
        ws["A3"] = "Tetto Massimo Mandato (€/mq):"
        ws["A3"].font = bold_font
        ws["C3"] = 8.00
        ws["C3"].fill = amber_soft
        ws["C3"].font = blue_bold
        ws["C3"].number_format = '#,##0.00 "€/mq"'
        ws["D3"] = f"=C3*{PERTICA_PIACENTINA_MQ:.2f}"
        ws["D3"].fill = amber_soft
        ws["D3"].font = blue_bold
        ws["D3"].number_format = '#,##0 "€/pertica"'

        for col_idx, h in enumerate(headers_lotti, 1):
            c = ws.cell(5, col_idx, h)
            if col_idx <= 12:
                c.fill = navy_fill
            elif col_idx <= 24:
                c.fill = slate_fill
            elif col_idx <= 37:
                c.fill = emerald_fill
            else:
                c.fill = navy_fill
            c.font = hdr_font
            c.alignment = center_align
            c.border = thin_border
        ws.row_dimensions[5].height = 36

        for i, item in enumerate(subset, 1):
            r = 5 + i
            ws.row_dimensions[r].height = 24
            cm = item["comune"]
            m = COMUNE_MARKET_DATA.get(cm, COMUNE_MARKET_DATA["Caorso"])
            is_peri = item["gruppo"] != "APERTA_CAMPAGNA"
            offerta_cons_mq = m["fv_buy_cons_mq"] if not is_peri else 8.50

            row_vals = [
                i,
                item["id"],
                item["categoria_label"],
                item["priorita_label"],
                cm,
                item["belfiore"],
                int(item["foglio"]) if str(item["foglio"]).isdigit() else item["foglio"],
                int(item["particella"]) if str(item["particella"]).isdigit() else item["particella"],
                item["sup_tot_ha"],
                item["sup_300m_ha"],
                f"=I{r}*{PERTICHE_PER_HA:.4f}",
                f"=J{r}*{PERTICHE_PER_HA:.4f}",
                item["autostrada"],
                item["dist_asse_m"],
                item["dist_linea_at_m"],
                item["kv_linea"],
                item["stazione_display"],
                item["dist_stazione_km"],
                item["cp_arera_nome"],
                item["cavidotto_mt_m"],
                item["capex_allaccio_eur"],
                item["mwp_tot"],
                item["mwp_300m"],
                item["mwh_tracker"],
                m["vam_uff_mq"],
                m["rogito_med_mq"],
                f"=Z{r}*{PERTICA_PIACENTINA_MQ:.2f}",
                f"=I{r}*10000*Z{r}",
                f"{m['asking_min_mq']:.2f}-{m['asking_max_mq']:.2f}",
                f"{int(m['ind_min_mq'])}-{int(m['ind_max_mq'])}",
                offerta_cons_mq,
                f"=AE{r}*{PERTICA_PIACENTINA_MQ:.2f}",
                f"=I{r}*10000*AE{r}",
                f"=I{r}*10000*$C$3",
                f"=I{r}*{m['affitto_agr_ha']}",
                f"=I{r}*3000",
                f"=AJ{r}*30",
                item["score"],
                item["lat"],
                item["lon"],
                "Apri Google Maps",
                item["note"],
                None,
                None,
                f'=IF(AR{r}="","",AR{r}*{PERTICA_PIACENTINA_MQ:.2f})',
                f'=IF(AR{r}="","",IF(AR{r}<=$C$3,"SÌ (ENTRO 8€/MQ)","NO (SOPRA SOGLIA -> PROPORRE DDS)"))',
            ]

            for col_idx, val in enumerate(row_vals, 1):
                c = ws.cell(r, col_idx, val)
                c.border = thin_border
                c.font = bold_font if col_idx in (2, 5, 9, 10, 26, 28, 31, 33, 34, 38) else reg_font
                c.alignment = (
                    left_align
                    if col_idx in (3, 4, 5, 17, 19, 42, 43)
                    else (center_align if col_idx in (1, 2, 6, 7, 8, 13, 16, 29, 30, 41, 46) else right_align)
                )

                if col_idx in (9, 10):
                    c.number_format = "#,##0.00"
                elif col_idx in (11, 12):
                    c.number_format = '#,##0.0 "pert."'
                elif col_idx in (14, 15, 20, 24):
                    c.number_format = "#,##0"
                elif col_idx == 18:
                    c.number_format = "0.0"
                elif col_idx in (21, 28, 33, 34, 35, 36, 37):
                    c.number_format = '#,##0 "€"'
                elif col_idx in (22, 23):
                    c.number_format = "#,##0.00"
                elif col_idx in (25, 26, 31, 44):
                    c.number_format = '#,##0.00 "€/mq"'
                elif col_idx in (27, 32, 45):
                    c.number_format = '#,##0 "€/pert."'
                elif col_idx == 38:
                    c.number_format = "0.0"
                    c.font = green_bold
                elif col_idx in (39, 40):
                    c.number_format = "0.000000"

                if col_idx in (26, 27, 28):
                    c.fill = blue_soft
                    c.font = blue_bold
                elif col_idx in (31, 32, 33, 34):
                    c.fill = emerald_soft
                    c.font = green_bold
                elif col_idx in (36, 37):
                    c.fill = amber_soft
                elif col_idx == 41:
                    c.hyperlink = item["gmaps_url"]
                    c.font = link_font
                elif col_idx in (43, 44, 45):
                    c.fill = amber_soft

        tot_row = 6 + len(subset)
        ws.row_dimensions[tot_row].height = 26
        ws.cell(tot_row, 5, "TOTALE / MEDIA").font = bold_font
        for sum_col in (9, 10, 11, 12, 21, 22, 23, 24, 28, 33, 34, 35, 36, 37):
            col_l = get_column_letter(sum_col)
            cell = ws.cell(tot_row, sum_col, f"=SUM({col_l}6:{col_l}{tot_row-1})")
            cell.number_format = '#,##0 "€"' if sum_col in (21, 28, 33, 34, 35, 36, 37) else "#,##0.0"
        for avg_col in (25, 26, 27, 31, 32, 38):
            col_l = get_column_letter(avg_col)
            cell = ws.cell(tot_row, avg_col, f"=AVERAGE({col_l}6:{col_l}{tot_row-1})")
            cell.number_format = '#,##0.00 "€/mq"' if avg_col in (25, 26, 31) else ('#,##0 "€/pert."' if avg_col in (27, 32) else "0.0")
        style_range(ws, 1, tot_row, len(headers_lotti), tot_row, font=bold_font, fill=gray_soft, border=thick_bottom)
        ws.freeze_panes = "F6"

        for col_idx in range(1, len(headers_lotti) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 16
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 14
        ws.column_dimensions["C"].width = 28
        ws.column_dimensions["D"].width = 28
        ws.column_dimensions["E"].width = 20
        ws.column_dimensions["Q"].width = 24
        ws.column_dimensions["S"].width = 28
        ws.column_dimensions["AP"].width = 48

    aperta_lots = [x for x in lots if x["gruppo"] == "APERTA_CAMPAGNA"]
    peri_lots = [x for x in lots if x["gruppo"] != "APERTA_CAMPAGNA"]

    populate_lots_sheet(
        ws_aperta,
        aperta_lots,
        f"90 LOTTI QUALIFICATI IN APERTA CAMPAGNA (A1 & A21 PIACENZA) — DATI TECNICI, ROGITI REALI, PERTICHE E TARGET FV",
    )
    populate_lots_sheet(
        ws_peri,
        peri_lots,
        f"26 LOTTI IN RISERVA PERIURBANA (<250m DA AREE PRODUTTIVE/LE MOSE) — ANALISI COSTI E OPZIONE DIRITTO DI SUPERFICIE",
    )

    # ==========================================================================
    # FOGLIO 5: CASI REALI DI MERCATO DOCUMENTATI E VADEMECUM TRATTATIVA
    # ==========================================================================
    ws_casi.views.sheetView[0].showGridLines = True
    ws_casi["A1"] = "COMPARABILI REALI DOCUMENTATI SUL TERRITORIO PIACENTINO & VADEMECUM NEGOZIALE"
    ws_casi["A1"].font = title_font
    ws_casi["A2"] = "Riferimenti puntuali da portali immobiliari (Idealista, Immobiliare.it, Trovacasa, Immobiliare 7 Valli, Demer), CREA e Tribunale di Piacenza"
    ws_casi["A2"].font = subtitle_font

    h_casi = [
        "Tipologia Comparabile",
        "Localizzazione (Comune / Zona)",
        "Taglia Rilevata",
        "Prezzo Rilevato (Totale / Unitario)",
        "Prezzo in €/mq",
        "Prezzo in €/Pertica Piacentina",
        "Fonte del Dato",
        "Indicazione Operativa per SunPro",
    ]
    for idx, h in enumerate(h_casi, 1):
        c = ws_casi.cell(4, idx, h)
        c.fill = navy_fill
        c.font = hdr_font
        c.alignment = center_align
        c.border = thin_border
    ws_casi.row_dimensions[4].height = 28

    casi_reali = [
        (
            "Compendio Agricolo Seminativo Irriguo",
            "Pianura Piacentina (Asse Via Emilia / Bassa)",
            "50 Pertiche Piacentine (~3,81 ha)",
            "Richiesta: 270.000 – 280.000 € a corpo",
            "7,08 – 7,35 €/mq (Asking) -> ~6,40 €/mq al rogito",
            "5.400 – 5.600 €/pertica (Asking) -> ~4.850 €/pertica rogito",
            "Annuncio Portale Trovacasa / Agenzie Agrarie Piacenza",
            "Dimostra che per corpi irrigui di ~4 ha la richiesta iniziale su portale è ~7,15 €/mq e si chiude sotto i 6,50 €/mq.",
        ),
        (
            "Transato Medio Seminativo Irriguo Pianura",
            "Provincia di Piacenza (Pianura Irrigua)",
            "Taglia media 5 – 20 ha",
            "45.000 – 52.000 €/ha (media ordinaria) fino a 65.000 €/ha (top irriguo)",
            "4,50 – 6,50 €/mq",
            "3.430 – 4.950 €/pertica",
            "Indagine Mercato Fondiario CREA & Listini CCIAA Piacenza",
            "Conferma che l'offerta SunPro (6,80 – 7,85 €/mq) paga un premio reale del +20/+35% sopra i rogiti agricoli.",
        ),
        (
            "Aste Giudiziarie Terreni Agricoli Pianura",
            "Caorso, Cadeo, Pontenure, Rottofreno, Fiorenzuola",
            "Da 0,5 ha a oltre 10 ha",
            "Base d'asta: 8.000 – 25.000 €/ha (perizia CTU piena: 45.000-55.000 €/ha)",
            "0,80 – 2,50 €/mq (base asta ribassata)",
            "610 – 1.905 €/pertica (base asta)",
            "PVP Ministero Giustizia / IVG Parma e Piacenza",
            "Utile come argomento negoziale su terreni con esecuzioni o mutui ipotecari pendenti.",
        ),
        (
            "Lotto Edificabile Produttivo / Logistico",
            "Piacenza — Polo Logistico Le Mose / Caorsana",
            "Lotti da 5.000 a 30.000+ mq",
            "80 – 85 €/mq (grandi aree da urbanizzare) | 120 – 140 €/mq (lotti finiti)",
            "80,00 – 140,00 €/mq",
            "Non applicabile (venduto a mq edificabile)",
            "Immobiliare.it / Idealista — Comparto Le Mose / Piacenza Sud",
            "Motivo per cui i 12 lotti periurbani vicino a Le Mose sono stati separati nelle Riserve.",
        ),
        (
            "Lotto Industriale / Artigianale Urbanizzato",
            "Fiorenzuola d'Arda (Zona Svincolo A1 / Barabasca)",
            "Lotti da 3.000 a 15.000 mq",
            "80 €/mq (comparti espansione) | 100 – 116 €/mq (lotti recintati e urbanizzati)",
            "80,00 – 116,00 €/mq",
            "Non applicabile (venduto a mq edificabile)",
            "Demer Immobiliare / Idealista / Trovacasa Fiorenzuola",
            "Tenersi a >300m dal perimetro del polo industriale del casello per comprare a prezzo agricolo.",
        ),
        (
            "Aree Logistiche e di Espansione Produttiva",
            "Castel San Giovanni (Polo Logistico A21)",
            "Da 7.000 mq a >50.000 mq",
            "40 €/mq (grandi aree agricole di trasformazione) | 110 – 150 €/mq (polo consolidato)",
            "40,00 – 150,00 €/mq",
            "Non applicabile",
            "Casa.it / Idealista — Castel San Giovanni",
            "Sui 5 lotti di Castel San Giovanni verificare sempre prima il CDU per escludere ambiti logistici PUG.",
        ),
        (
            "Diritto di Superficie (DDS) Fotovoltaico",
            "Emilia-Romagna / Pianura Padana (Fascia Autostradale ≤300m)",
            "Impianti da 5 a 20 MWp (6 – 24 ha)",
            "Canone annuo: 2.500 – 3.500 €/ha/anno (fino a 3.800 €/ha/anno se <1 km da CP)",
            "0,25 – 0,38 €/mq/anno (7,50-11,40 €/mq in 30 anni)",
            "190 – 290 €/pertica/anno (Target SunPro: 229 €/pertica/anno)",
            "Sunprime / Solare Industriale / Nibo Green / Operatori Utility-Scale",
            "Formula esente da Prelazione Agraria dei confinanti CD/IAP (art. 952 c.c.).",
        ),
    ]

    for i, row_vals in enumerate(casi_reali, 1):
        r = 4 + i
        ws_casi.row_dimensions[r].height = 34
        for c_idx, val in enumerate(row_vals, 1):
            c = ws_casi.cell(r, c_idx, val)
            c.border = thin_border
            c.font = bold_font if c_idx in (1, 2, 5, 6) else reg_font
            c.alignment = left_align if c_idx in (1, 2, 4, 7, 8) else center_align
            if i in (1, 2):
                c.fill = blue_soft
            elif i == 7:
                c.fill = emerald_soft
            elif i in (4, 5, 6):
                c.fill = rose_soft

    for col_idx in range(1, 9):
        ws_casi.column_dimensions[get_column_letter(col_idx)].width = 24
    ws_casi.column_dimensions["A"].width = 32
    ws_casi.column_dimensions["B"].width = 34
    ws_casi.column_dimensions["D"].width = 36
    ws_casi.column_dimensions["G"].width = 34
    ws_casi.column_dimensions["H"].width = 50

    for col_idx in range(1, len(headers_f1) + 1):
        ws_comuni.column_dimensions[get_column_letter(col_idx)].width = 16
    ws_comuni.column_dimensions["A"].width = 22
    ws_comuni.column_dimensions["C"].width = 26
    ws_comuni.column_dimensions["W"].width = 38
    ws_comuni.column_dimensions["AG"].width = 30
    ws_comuni.column_dimensions["AH"].width = 32
    ws_comuni.column_dimensions["AI"].width = 55

    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        wb.save(p)
        print(f"  ✓ Salvato Workbook Excel completo: {p}")


if __name__ == "__main__":
    lots_json = DATA_DIR / "piacentino_enriched_lots.json"
    lots = json.loads(lots_json.read_text(encoding="utf-8"))
    for x in lots:
        cm = x["comune"]
        m = COMUNE_MARKET_DATA.get(cm, COMUNE_MARKET_DATA["Caorso"])
        is_peri = x["gruppo"] != "APERTA_CAMPAGNA"
        x["pertiche_tot"] = round(x["sup_tot_ha"] * PERTICHE_PER_HA, 1)
        x["pertiche_300m"] = round(x["sup_300m_ha"] * PERTICHE_PER_HA, 1)
        x["rogito_med_mq"] = m["rogito_med_mq"]
        x["rogito_pertica_eur"] = int(round(m["rogito_med_mq"] * PERTICA_PIACENTINA_MQ))
        x["valore_rogito_reale_eur"] = int(round(x["sup_tot_ha"] * 10000 * m["rogito_med_mq"]))
        x["asking_range_mq"] = f"{m['asking_min_mq']:.2f}–{m['asking_max_mq']:.2f}"
        x["ind_range_mq"] = f"{int(m['ind_min_mq'])}–{int(m['ind_max_mq'])}"
        x["affitto_agr_ha"] = m["affitto_agr_ha"]
        x["fv_buy_cons_mq"] = m["fv_buy_cons_mq"] if not is_peri else 8.50
        x["fv_buy_pertica_eur"] = int(round(x["fv_buy_cons_mq"] * PERTICA_PIACENTINA_MQ))
        x["valore_fv_cons_eur"] = int(round(x["sup_tot_ha"] * 10000 * x["fv_buy_cons_mq"]))
        x["premio_rogito_pct"] = round(((x["fv_buy_cons_mq"] - m["rogito_med_mq"]) / m["rogito_med_mq"]) * 100, 1)
    lots_json.write_text(json.dumps(lots, indent=2, ensure_ascii=False), encoding="utf-8")

    target_paths = [
        BASE_DIR / "Quotazioni_Mercato_Reale_e_Comparabili_Piacentino_A1_A21.xlsx",
        BASE_DIR / "Terreni_FV_Piacentino_A1_A21_Esteso.xlsx",
        WEB_DIR / "Terreni_FV_Piacentino_A1_A21_Esteso.xlsx",
        WEB_DIR / "Quotazioni_Mercato_Reale_e_Comparabili_Piacentino_A1_A21.xlsx",
        DATA_DIR / "Terreni_FV_Piacentino_A1_A21_Esteso.xlsx",
        DESKTOP_DIR / "Quotazioni_Mercato_Reale_e_Comparabili_Piacentino_A1_A21.xlsx",
    ]
    build_comprehensive_market_excel(lots, target_paths)
