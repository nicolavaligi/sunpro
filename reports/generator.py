"""
Generatore di Dossier e Report Commerciali per l'acquisizione di terreni fotovoltaici.
Supporta generazione PDF (ReportLab) e formattazione HTML pronta per la stampa o l'invio.
Autore: Nicola Valigi Engine System
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

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

from config import REPORTS_DIR
from crawler.owner_discovery import generate_commercial_pitch

def generate_pdf_dossier(lead: Dict[str, Any]) -> Path:
    """Genera un dossier commerciale executive in formato PDF (A4)."""
    lead_id = lead["id"]
    filename = f"dossier_{lead_id}_{lead['comune'].lower().replace(' ', '_')}.pdf"
    pdf_path = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#059669')
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    bold_style = ParagraphStyle(
        'DocBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A')
    )
    pitch_style = ParagraphStyle(
        'DocPitch',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1E3A8A')
    )

    story = []

    # Intestazione
    story.append(Paragraph(f"DOSSIER ORIGINATION TERRENI: {lead['title']}", title_style))
    story.append(Paragraph(
        f"ID: <b>{lead_id}</b> | Regione: <b>{lead['regione']} ({lead['provincia']})</b> | "
        f"Score: <b>{lead['score_totale']}/100 ({lead.get('rating_classe', 'QUALIFICATO')})</b>",
        subtitle_style
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#059669'), spaceAfter=10))

    # Tabella Dati Catastali & Geografici
    catastali_data = [
        [Paragraph("<b>Comune</b>", bold_style), Paragraph(f"{lead['comune']} ({lead.get('codice_belfiore', 'N/D')})", body_style),
         Paragraph("<b>Foglio / Particelle</b>", bold_style), Paragraph(f"Fg. {lead.get('foglio', 'N/D')} - P.lle {lead.get('particella', 'N/D')}", body_style)],
        [Paragraph("<b>Coordinate GPS</b>", bold_style), Paragraph(f"{lead['lat']:.4f}, {lead['lng']:.4f}", body_style),
         Paragraph("<b>Tipologia D.Lgs 199/21</b>", bold_style), Paragraph(f"{lead['tipologia']}", body_style)],
        [Paragraph("<b>Buffer Industriale</b>", bold_style), Paragraph(f"{lead.get('distanza_zona_industriale_m', 0):.0f} m da Z.I.", body_style),
         Paragraph("<b>Fascia Autostradale</b>", bold_style), Paragraph(f"{lead.get('distanza_autostrada_m', 0):.0f} m ({lead.get('nome_autostrada', '')})", body_style)],
    ]
    t_cat = Table(catastali_data, colWidths=[3.2*cm, 5.8*cm, 3.8*cm, 5.2*cm])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 10))

    # Tabella Dimensionamento Tecnico & Rete Elettrica
    story.append(Paragraph("DIMENSIONAMENTO TECNICO & PROSSIMITÀ CABINA AT/MT", section_title_style))
    mwp = lead.get('mwp_stimati', 0)
    mwh = lead.get('produzione_mwh_anno', 0)
    capex = lead.get('capex_allaccio_eur', 0)

    tecnici_data = [
        [Paragraph("<b>Superficie Totale</b>", bold_style), Paragraph(f"{lead['superficie_ha']:.2f} ha ({lead['superficie_mq']:,.0f} mq)", body_style),
         Paragraph("<b>Potenza Stimata</b>", bold_style), Paragraph(f"<b>~{mwp:.2f} MWp</b>", bold_style)],
        [Paragraph("<b>Produzione Stimata</b>", bold_style), Paragraph(f"<b>{mwh:,.0f} MWh/anno</b>", body_style),
         Paragraph("<b>Cabina Primaria</b>", bold_style), Paragraph(f"{lead.get('cabina_piu_vicina', 'N/D')}", body_style)],
        [Paragraph("<b>Distanza Cabina</b>", bold_style), Paragraph(f"<b>{lead.get('distanza_cabina_m', 0):,.0f} m</b>", bold_style),
         Paragraph("<b>Stima CAPEX Allaccio</b>", bold_style), Paragraph(f"~{capex:,.0f} €", body_style)]
    ]
    t_tec = Table(tecnici_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    t_tec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0FDF4')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#86EFAC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BBF7D0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tec)
    story.append(Spacer(1, 10))

    # Valutazione Economica (Acquisto vs Diritto di Superficie)
    story.append(Paragraph("PROPOSTA ECONOMICA PER LA PROPRIETÀ (BENCHMARK 8-9 €/MQ)", section_title_style))
    pr_tot = lead.get('prezzo_richiesto_eur', 0)
    pr_mq = lead.get('prezzo_mq_eur', 0)
    canone_annuo = lead['superficie_ha'] * 3000
    canone_30anni = canone_annuo * 30

    econ_data = [
        [Paragraph("<b>OPZIONE A: Cessione / Acquisto Immediato</b>", bold_style),
         Paragraph(f"<b>{pr_tot:,.0f} €</b> totali ({pr_mq:.2f} €/mq a rogito notarile)", bold_style)],
        [Paragraph("<b>OPZIONE B: Diritto di Superficie (30 Anni)</b>", bold_style),
         Paragraph(f"<b>{canone_annuo:,.0f} € / anno</b> indicizzato ISTAT (~{canone_30anni:,.0f} € in 30 anni)", bold_style)]
    ]
    t_econ = Table(econ_data, colWidths=[7.0*cm, 11.0*cm])
    t_econ.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#93C5FD')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BFDBFE')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_econ)
    story.append(Spacer(1, 10))

    # Dati Proprietario e Canali di Contatto
    story.append(Paragraph("CONTATTI & INTESTAZIONE PROPRIETÀ", section_title_style))
    prop_data = [
        [Paragraph("<b>Intestatario</b>", bold_style), Paragraph(f"<b>{lead.get('proprietario_nome', 'N/D')}</b> ({lead.get('proprietario_tipo', 'N/D')})", body_style)],
        [Paragraph("<b>P.IVA / C.F.</b>", bold_style), Paragraph(f"{lead.get('proprietario_piva') or 'In corso di estrazione camerale'}", body_style)],
        [Paragraph("<b>PEC Ufficiale</b>", bold_style), Paragraph(f"<b>{lead.get('proprietario_pec') or 'N/D'}</b>", bold_style)],
        [Paragraph("<b>Telefono / Referente</b>", bold_style), Paragraph(f"{lead.get('proprietario_telefono') or 'N/D'}", body_style)]
    ]
    t_prop = Table(prop_data, colWidths=[4.0*cm, 14.0*cm])
    t_prop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#FDE68A')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FEF3C7')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_prop)
    story.append(Spacer(1, 10))

    # Script Commerciale per il Sales Rep
    pitch_info = generate_commercial_pitch(lead)
    story.append(Paragraph("SCRIPT TELEFONICO & PITCH COMMERCIALE (PER IL SALES REP)", section_title_style))
    story.append(Paragraph(pitch_info["pitch_telefonico"], pitch_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Come superare le obiezioni comuni:</b>", bold_style))
    story.append(Paragraph(pitch_info["obiezioni_e_risposte"].replace('\n', '<br/>'), body_style))

    # Note Commerciali Interne
    if lead.get("note_commerciali"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Note di origination interna:</b>", bold_style))
        story.append(Paragraph(lead["note_commerciali"], body_style))

    doc.build(story)
    return pdf_path

def generate_html_dossier(lead: Dict[str, Any]) -> str:
    """Genera una stringa HTML stilizzata pronta per anteprima o stampa web."""
    lead_id = lead["id"]
    pitch_info = generate_commercial_pitch(lead)
    canone_annuo = lead['superficie_ha'] * 3000

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #059669; padding-bottom: 12px; margin-bottom: 20px;">
            <div>
                <h1 style="font-size: 22px; margin: 0; color: #1e293b;">{lead['title']}</h1>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 14px;">
                    ID: <b>{lead_id}</b> | Comune: <b>{lead['comune']} ({lead['provincia']})</b> | Regione: <b>{lead['regione']}</b>
                </p>
            </div>
            <div style="text-align: right; background: #f0fdf4; border: 1px solid #86efac; padding: 8px 16px; border-radius: 6px;">
                <span style="font-size: 12px; color: #166534; font-weight: bold; display: block;">SCORE IDONEITÀ</span>
                <span style="font-size: 24px; font-weight: bold; color: #059669;">{lead['score_totale']}/100</span>
                <span style="font-size: 11px; color: #15803d; display: block;">{lead.get('rating_classe', 'QUALIFICATO')}</span>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
            <div style="background: #f8fafc; padding: 14px; border-radius: 6px; border: 1px solid #e2e8f0;">
                <h3 style="margin-top: 0; font-size: 14px; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px;">📍 Inquadramento Spaziale (D.Lgs 199/21)</h3>
                <p style="margin: 6px 0; font-size: 13px;"><b>Foglio / Particelle:</b> Fg. {lead.get('foglio')} - P.lle {lead.get('particella')}</p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Coordinate GPS:</b> {lead['lat']:.4f}, {lead['lng']:.4f}</p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Tipologia:</b> <span style="background: #dbeafe; color: #1e40af; padding: 2px 6px; border-radius: 4px;">{lead['tipologia']}</span></p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Zona Industriale:</b> {lead.get('distanza_zona_industriale_m', 0):.0f} m (buffer 350m)</p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Autostrada:</b> {lead.get('distanza_autostrada_m', 0):.0f} m ({lead.get('nome_autostrada', '')})</p>
            </div>

            <div style="background: #f0fdf4; padding: 14px; border-radius: 6px; border: 1px solid #bbf7d0;">
                <h3 style="margin-top: 0; font-size: 14px; color: #065f46; border-bottom: 1px solid #86efac; padding-bottom: 6px;">⚡ Potenziale Impiantistico & Rete</h3>
                <p style="margin: 6px 0; font-size: 13px;"><b>Superficie:</b> {lead['superficie_ha']:.2f} ha ({lead['superficie_mq']:,.0f} mq)</p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Potenza Stimata:</b> <b style="color: #059669;">~{lead.get('mwp_stimati', 0):.2f} MWp</b></p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Produzione Attesa:</b> {lead.get('produzione_mwh_anno', 0):,.0f} MWh/anno</p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Cabina Primaria AT/MT:</b> {lead.get('cabina_piu_vicina')}</p>
                <p style="margin: 6px 0; font-size: 13px;"><b>Distanza Cabina:</b> <b>{lead.get('distanza_cabina_m', 0):,.0f} m</b> (~{lead.get('capex_allaccio_eur', 0):,.0f} € CAPEX allaccio)</p>
            </div>
        </div>

        <div style="background: #eff6ff; padding: 14px; border-radius: 6px; border: 1px solid #bfdbfe; margin-bottom: 20px;">
            <h3 style="margin-top: 0; font-size: 14px; color: #1e40af; border-bottom: 1px solid #93c5fd; padding-bottom: 6px;">💶 Valutazione Economica (Target 8-9 €/mq)</h3>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div>
                    <div style="font-size: 12px; color: #3b82f6; font-weight: bold;">OPZIONE 1: ACQUISTO A ROGITO</div>
                    <div style="font-size: 20px; font-weight: bold; color: #1d4ed8; margin: 4px 0;">{lead.get('prezzo_richiesto_eur', 0):,.0f} €</div>
                    <div style="font-size: 12px; color: #64748b;">({lead.get('prezzo_mq_eur', 0):.2f} €/mq)</div>
                </div>
                <div style="border-left: 1px solid #cbd5e1; height: 50px;"></div>
                <div>
                    <div style="font-size: 12px; color: #3b82f6; font-weight: bold;">OPZIONE 2: DIRITTO DI SUPERFICIE 30 ANNI</div>
                    <div style="font-size: 20px; font-weight: bold; color: #1d4ed8; margin: 4px 0;">{canone_annuo:,.0f} € / anno</div>
                    <div style="font-size: 12px; color: #64748b;">(~{canone_annuo*30:,.0f} € complessivi in 30 anni)</div>
                </div>
            </div>
        </div>

        <div style="background: #fffbeb; padding: 14px; border-radius: 6px; border: 1px solid #fde68a; margin-bottom: 20px;">
            <h3 style="margin-top: 0; font-size: 14px; color: #92400e; border-bottom: 1px solid #fcd34d; padding-bottom: 6px;">🏢 Dati Proprietario e Canali di Contatto</h3>
            <p style="margin: 6px 0; font-size: 13px;"><b>Intestatario:</b> {lead.get('proprietario_nome')} ({lead.get('proprietario_tipo')})</p>
            <p style="margin: 6px 0; font-size: 13px;"><b>PEC:</b> <a href="mailto:{lead.get('proprietario_pec')}">{lead.get('proprietario_pec') or 'In corso di estrazione'}</a></p>
            <p style="margin: 6px 0; font-size: 13px;"><b>Telefono / Referente:</b> {lead.get('proprietario_telefono') or 'N/D'}</p>
        </div>

        <div style="background: #f1f5f9; padding: 14px; border-radius: 6px; border: 1px solid #cbd5e1;">
            <h3 style="margin-top: 0; font-size: 14px; color: #0f172a; border-bottom: 1px solid #94a3b8; padding-bottom: 6px;">📞 Script Telefonico per il Commerciale</h3>
            <blockquote style="margin: 8px 0; font-style: italic; color: #1e3a8a; background: #e0e7ff; padding: 10px; border-left: 4px solid #4338ca; border-radius: 4px; font-size: 13px; line-height: 1.5;">
                {pitch_info['pitch_telefonico']}
            </blockquote>
        </div>
    </div>
    """
    return html
