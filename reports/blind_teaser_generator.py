"""
Generatore di Blind Commercial Teaser (Pre-NDA One-Pager PDF A4) per SunPro.
Crea schede commerciali di alto profilo per sviluppatori, EPC e fondi infrastrutturali:
- Maschera i dati catastali sensibili (foglio, particella, anagrafica proprietario)
- Evidenzia metriche chiave: Superficie, MWp, Resa PVGIS (Fisso vs Tracker), Distanza Stradale Cabina
- Include modello finanziario a doppio scenario (Acquisto vs Diritto di Superficie 30 anni)
- Riporta l'esito dello screening vincoli ambientali/idrogeologici e autorizzabilità PAS
- Box di sblocco dati completi previa firma NDA con Nicola Valigi (Houdinick)
Autore: Nicola Valigi Engine System
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import (
    BLIND_TEASERS_DIR,
    DETOUR_FACTOR_GRID,
    TRACKER_BOOST_DEFAULT_PCT,
    TRACKER_CAPEX_EXTRA_PER_MWP,
)
from crawler.environmental_checker import check_environmental_constraints
from crawler.pvgis import get_pvgis_irradiance

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text

def generate_blind_teaser_pdf(lead: Dict[str, Any], output_dir: Path = BLIND_TEASERS_DIR) -> Path:
    """Genera una scheda teaser cieca commerciale in formato PDF (A4 One-Pager)."""
    lead_id = lead["id"]
    comune_slug = slugify(lead.get("comune", "sito"))
    filename = f"teaser_{lead_id}_{comune_slug}.pdf"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm
    )

    styles = getSampleStyleSheet()

    # Stili tipografici corporate
    title_style = ParagraphStyle(
        'TeaserTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0F172A')
    )
    badge_style = ParagraphStyle(
        'TeaserBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#D97706')
    )
    confidential_style = ParagraphStyle(
        'TeaserConfidential',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#DC2626')
    )
    section_title = ParagraphStyle(
        'TeaserSection',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=6,
        spaceAfter=3
    )
    cell_bold = ParagraphStyle(
        'TeaserCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0F172A')
    )
    cell_text = ParagraphStyle(
        'TeaserCellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )
    cell_accent = ParagraphStyle(
        'TeaserCellAccent',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#059669')
    )
    masked_style = ParagraphStyle(
        'TeaserMasked',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#94A3B8')
    )
    cta_style = ParagraphStyle(
        'TeaserCTA',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    story = []

    # Calcoli tecnici ed energetici
    superficie_ha = float(lead.get("superficie_ha", 0))
    superficie_mq = float(lead.get("superficie_mq", superficie_ha * 10000))
    mwp = float(lead.get("mwp_stimati", round(superficie_mq / 12000, 2)))
    mwh_fisso = float(lead.get("produzione_mwh_anno", round(mwp * 1300, 1)))

    # PVGIS scientifico
    lat = float(lead.get("lat", 45.0))
    lng = float(lead.get("lng", 10.0))
    solar_info = get_pvgis_irradiance(lat, lng)
    yield_fisso = solar_info.get("kwh_kwp_anno", 1300.0)
    yield_tracker = solar_info.get("kwh_kwp_tracker", round(yield_fisso * 1.20, 1))
    boost_tracker_pct = solar_info.get("boost_tracker_pct", TRACKER_BOOST_DEFAULT_PCT)
    mwh_tracker = round(mwp * yield_tracker, 1)

    # Rete con fattore di tortuosità stradale (1.30x)
    dist_cabina_aria = int(lead.get("distanza_cabina_m", 750))
    dist_cabina_strada = int(dist_cabina_aria * DETOUR_FACTOR_GRID)
    capex_allaccio = int(lead.get("capex_allaccio_eur", 75000))

    # Economico
    prezzo_mq = float(lead.get("prezzo_mq_eur", 8.20))
    valore_acquisto = int(lead.get("prezzo_richiesto_eur", superficie_mq * prezzo_mq))
    canone_annuo = int(superficie_ha * 3000.0)
    canone_30anni = int(canone_annuo * 30.0)

    # CAPEX e Ricavi (85 €/MWh)
    capex_epc_fisso = int(mwp * 680_000.0)
    capex_epc_tracker = int(mwp * (680_000.0 + TRACKER_CAPEX_EXTRA_PER_MWP))
    ricavo_annuo_fisso = int(mwh_fisso * 85.0)
    ricavo_annuo_tracker = int(mwh_tracker * 85.0)
    extra_ricavo_tracker = ricavo_annuo_tracker - ricavo_annuo_fisso
    ebitda_annuo_fisso = int(ricavo_annuo_fisso - (mwp * 14_000.0) - canone_annuo)
    payback_fisso = round((capex_epc_fisso + capex_allaccio) / max(1.0, ebitda_annuo_fisso), 1)

    # Screening Vincoli Ambientali
    env_audit = check_environmental_constraints(lead)

    # 1. Header Documento
    story.append(Paragraph(f"SUNPRO INVESTMENT TEASER — COD. TEASER-{lead_id}", title_style))
    header_text = (
        f"<b>Opportunità Utility-Scale & Agrivoltaico D.Lgs. 199/2021</b> | "
        f"Territorio: <b>{lead['regione']} ({lead.get('provincia', 'IT')})</b> | "
        f"Score SunPro: <b>{lead.get('score_totale', 80)}/100 ({lead.get('rating_classe', 'QUALIFICATO')})</b>"
    )
    story.append(Paragraph(header_text, badge_style))
    story.append(Paragraph("DOCUMENTO RISERVATO PRE-NDA — DATI PUNTUALI CATASTALI MASCHERATI", confidential_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=6))

    # 2. Tabella Macro-Inquadramento & Idoneità
    story.append(Paragraph("1. INQUADRAMENTO TERRITORIALE & IDONEITÀ NORMATIVA EX LEGE", section_title))
    t1_data = [
        [Paragraph("<b>Macro Area</b>", cell_bold), Paragraph(f"{lead['regione']} — Macro-area {lead.get('provincia', '')}", cell_text),
         Paragraph("<b>Comune di Riferimento</b>", cell_bold), Paragraph(f"{lead['comune']}", cell_text)],
        [Paragraph("<b>Classificazione D.Lgs. 199/21</b>", cell_bold), Paragraph(f"<b>{lead['tipologia']}</b>", cell_accent),
         Paragraph("<b>Fondamento Giuridico</b>", cell_bold), Paragraph(f"{env_audit['fondamento_normativo']}", cell_text)],
        [Paragraph("<b>Dati Catastali (Fg/P.lle)</b>", cell_bold), Paragraph("🔒 <i>CONFIDENZIALE — Sbloccabile previa firma NDA</i>", masked_style),
         Paragraph("<b>Titolarità Giuridica</b>", cell_bold), Paragraph("🔒 <i>CONFIDENZIALE — Persona Giuridica censita</i>", masked_style)],
    ]
    t1 = Table(t1_data, colWidths=[4.2*cm, 5.2*cm, 4.0*cm, 5.2*cm])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t1)
    story.append(Spacer(1, 4))

    # 3. Dimensionamento Tecnico & Resa Solare Comparata
    story.append(Paragraph("2. DIMENSIONAMENTO TECNICO & PRODUCIBILITÀ PVGIS JRC (FISSO vs TRACKER)", section_title))
    t2_data = [
        [Paragraph("<b>Superficie Totale</b>", cell_bold), Paragraph(f"<b>{superficie_ha:.2f} ha</b> ({int(superficie_mq):,} mq)", cell_bold),
         Paragraph("<b>Potenza Stimata</b>", cell_bold), Paragraph(f"<b>~{mwp:.2f} MWp</b>", cell_accent)],
        [Paragraph("<b>Resa Specifica (Tilt Fisso)</b>", cell_bold), Paragraph(f"<b>{yield_fisso:.0f} kWh/kWp/anno</b> (PVGIS v5.2)", cell_text),
         Paragraph("<b>Produzione Annua Fissa</b>", cell_bold), Paragraph(f"<b>{int(mwh_fisso):,} MWh/anno</b>", cell_bold)],
        [Paragraph("<b>Resa con Tracker Monoassiale</b>", cell_bold), Paragraph(f"<b>{yield_tracker:.0f} kWh/kWp/anno</b> (+{boost_tracker_pct:.1f}%)", cell_accent),
         Paragraph("<b>Produzione con Tracker</b>", cell_bold), Paragraph(f"<b>{int(mwh_tracker):,} MWh/anno</b> (+{int(mwh_tracker-mwh_fisso):,} MWh)", cell_accent)],
    ]
    t2 = Table(t2_data, colWidths=[4.2*cm, 5.2*cm, 4.0*cm, 5.2*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t2)
    story.append(Spacer(1, 4))

    # 4. Connessione Rete MT (Con fattore stradale 1.30x)
    story.append(Paragraph("3. CONNESSIONE DI RETE MT (CABINA PRIMARIA & ROUTING STRADALE)", section_title))
    t3_data = [
        [Paragraph("<b>Cabina Primaria Target</b>", cell_bold), Paragraph(f"<b>{lead.get('cabina_piu_vicina', 'CP Primaria')}</b>", cell_bold),
         Paragraph("<b>Livello di Tensione</b>", cell_bold), Paragraph("Media Tensione (MT 15/20 kV)", cell_text)],
        [Paragraph("<b>Distanza Linea d'Aria</b>", cell_bold), Paragraph(f"{dist_cabina_aria} metri", cell_text),
         Paragraph("<b>Percorso Stradale Reale (1.3x)</b>", cell_bold), Paragraph(f"<b>{dist_cabina_strada} metri</b> (viabilità pubblica)", cell_accent)],
        [Paragraph("<b>Stima CAPEX Allaccio Rete</b>", cell_bold), Paragraph(f"<b>€ {capex_allaccio:,}</b>", cell_accent),
         Paragraph("<b>Componenti Incluse</b>", cell_bold), Paragraph("Cavidotto interrato MT + stallo cabina primaria", cell_text)],
    ]
    t3 = Table(t3_data, colWidths=[4.2*cm, 5.2*cm, 4.0*cm, 5.2*cm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4))

    # 5. Modello Economico & Redditività Finanziaria
    story.append(Paragraph("4. MODELLO ECONOMICO & METRICHE FINANZIARIE", section_title))
    t4_data = [
        [Paragraph("<b>Canone Diritto Superficie (30a)</b>", cell_bold), Paragraph(f"<b>€ {canone_annuo:,}/anno</b> (3.000 €/ha/a)", cell_accent),
         Paragraph("<b>Totale Canone 30 Anni</b>", cell_bold), Paragraph(f"€ {canone_30anni:,}", cell_text)],
        [Paragraph("<b>Opzione Acquisto Terreno</b>", cell_bold), Paragraph(f"€ {valore_acquisto:,} ({prezzo_mq:.2f} €/mq)", cell_text),
         Paragraph("<b>CAPEX Progetto (Fisso / Tracker)</b>", cell_bold), Paragraph(f"€ {capex_epc_fisso/1e6:.2f}M / € {capex_epc_tracker/1e6:.2f}M", cell_bold)],
        [Paragraph("<b>Ricavi Annui Energia (85€/MWh)</b>", cell_bold), Paragraph(f"€ {ricavo_annuo_fisso:,} (Fisso) | € {ricavo_annuo_tracker:,} (Tracker)", cell_accent),
         Paragraph("<b>Delta Extra Ricavo Tracker</b>", cell_bold), Paragraph(f"<b>+€ {extra_ricavo_tracker:,}/anno</b>", cell_accent)],
        [Paragraph("<b>EBITDA Annuo Diritto Sup.</b>", cell_bold), Paragraph(f"<b>~€ {ebitda_annuo_fisso:,}/anno</b>", cell_accent),
         Paragraph("<b>Payback Stimato</b>", cell_bold), Paragraph(f"<b>~{payback_fisso} Anni</b>", cell_bold)],
    ]
    t4 = Table(t4_data, colWidths=[4.2*cm, 5.2*cm, 4.0*cm, 5.2*cm])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t4)
    story.append(Spacer(1, 4))

    # 6. Screening Vincoli Ambientali & Iter
    story.append(Paragraph("5. WATCHDOG VINCOLI AMBIENTALI & ITER AUTORIZZATIVO", section_title))
    t5_data = [
        [Paragraph("<b>Esito Screening Vincoli</b>", cell_bold), Paragraph(f"<b>{env_audit['esito_globale']}</b>", cell_accent),
         Paragraph("<b>Rating Ambientale</b>", cell_bold), Paragraph(f"<b>{env_audit['rating_ambientale']}</b>", cell_accent)],
        [Paragraph("<b>Rete Natura 2000 (ZPS/SIC)</b>", cell_bold), Paragraph(f"{env_audit['rete_natura_2000']}", cell_text),
         Paragraph("<b>Rischio Idrogeologico PAI</b>", cell_bold), Paragraph(f"{env_audit['rischio_idrogeologico_pai']}", cell_text)],
        [Paragraph("<b>Procedura Autorizzativa</b>", cell_bold), Paragraph(f"<b>{env_audit['iter_autorizzativo']}</b>", cell_accent),
         Paragraph("<b>Indice Autorizzabilità</b>", cell_bold), Paragraph(f"<b>{env_audit['autorizzabilita_pct']:.0f}%</b> (Certezza ex lege)", cell_accent)],
    ]
    t5 = Table(t5_data, colWidths=[4.2*cm, 5.2*cm, 4.0*cm, 5.2*cm])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t5)
    story.append(Spacer(1, 6))

    # 7. Box Call to Action & Sblocco Dati Previa NDA
    cta_box_data = [
        [Paragraph(
            "<b>🔑 MODALITÀ DI ACCESSO ALLA DUE DILIGENCE COMPLETA (PREVIA FIRMA NDA / LOI):</b><br/>"
            "Per ricevere il <b>Dossier Catastale Completo</b> (Foglio, Particelle, Visure storiche, Estratto di mappa catastale, "
            "Poligono georeferenziato KML/DXF, Identità e Contatti diretti della Proprietà, e avvio trattativa contrattuale), "
            "richiedere l'Accordo di Riservatezza (NDA) a:<br/>"
            "<b>Nicola Valigi (Houdinick)</b> | Origination & Geo-Intelligence | Contatto: <b>305862309+nicolavaligi@users.noreply.github.com</b>",
            cta_style
        )]
    ]
    t_cta = Table(cta_box_data, colWidths=[18.6*cm])
    t_cta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF3C7')), # Amber chiaro
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor('#F59E0B')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cta)

    doc.build(story)
    return pdf_path

def generate_all_blind_teasers():
    """Genera tutti i Teaser Ciechi PDF per i lead presenti nel database."""
    from data.storage import get_all_leads
    leads = get_all_leads()
    print(f"📄 Generazione di {len(leads)} Blind Teaser Commerciali PDF...")
    generated = []
    for l in leads:
        p = generate_blind_teaser_pdf(l)
        generated.append(p)
    print(f"✅ Generati {len(generated)} Blind Teaser in {BLIND_TEASERS_DIR}/")
    return generated

if __name__ == "__main__":
    generate_all_blind_teasers()
