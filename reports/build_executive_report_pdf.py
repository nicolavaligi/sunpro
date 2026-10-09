"""
Script per compilare REPORT_CRITICITA_E_SPECIFICHE_MOTORE in un PDF elegante,
professionale e pronto per essere condiviso con i soci e partner strategici.
Include:
- Chiarimento scientifico su come viene determinato il valore dei terreni (VAM / ISMEA / OMI)
- Differenziazione urbanistica (Zona E agricola contigua vs Zona D industriale)
- Gatekeeper di esclusione lotti non acquistabili (> 15 €/mq)
- Modello finanziario (Acquisto a premio vs Diritto di superficie trentennale)
- Ingegneria di rete (2.107 Cabine Primarie, 1.30x detour cavidotto)
- Report delle 5 criticità operative e soluzioni

Autore: Nicola Valigi Engine System
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = BASE_DIR / "REPORT_CRITICITA_E_SPECIFICHE_MOTORE.pdf"
WEB_OUTPUT_PDF = BASE_DIR / "web" / "REPORT_CRITICITA_E_SPECIFICHE_MOTORE.pdf"

class NumberedCanvas(canvas.Canvas):
    """Canvas personalizzato a due passaggi per calcolare il numero totale di pagine."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (dalla pagina 2 in poi)
        if self._pageNumber > 1:
            self.drawString(1.5 * cm, A4[1] - 1.2 * cm, "SunPro Geo-Intelligence 3D — Documento Tecnico-Esecutivo per Soci e Partner")
            self.drawRightString(A4[0] - 1.5 * cm, A4[1] - 1.2 * cm, "STRICTLY CONFIDENTIAL")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(1.5 * cm, A4[1] - 1.35 * cm, A4[0] - 1.5 * cm, A4[1] - 1.35 * cm)

        # Footer su tutte le pagine
        page_text = f"Pagina {self._pageNumber} di {page_count}"
        self.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, page_text)
        self.drawString(1.5 * cm, 1.0 * cm, "© 2026 Nicola Valigi (Houdinick) — SunPro Engine System")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(1.5 * cm, 1.3 * cm, A4[0] - 1.5 * cm, 1.3 * cm)

        self.restoreState()

def build_pdf():
    print(f"📄 Compilazione PDF executive: {OUTPUT_PDF.name}...")
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    styles = getSampleStyleSheet()

    # Tipografia Custom Executive
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=colors.HexColor('#1E3A8A'), spaceAfter=8
    )
    meta_box_style = ParagraphStyle(
        'MetaBox', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155')
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=11, spaceAfter=5, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13.5,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=7, spaceAfter=3, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11.5,
        textColor=colors.HexColor('#334155'), spaceAfter=4
    )
    body_bold = ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11.5,
        textColor=colors.HexColor('#0F172A')
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11.5,
        textColor=colors.HexColor('#334155'), leftIndent=12, firstLineIndent=-8, spaceAfter=2.5
    )
    alert_box_title = ParagraphStyle(
        'AlertTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#B45309')
    )
    alert_box_body = ParagraphStyle(
        'AlertBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=10.5,
        textColor=colors.HexColor('#451A03')
    )
    focus_box_title = ParagraphStyle(
        'FocusTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=12,
        textColor=colors.HexColor('#1E3A8A')
    )
    focus_box_body = ParagraphStyle(
        'FocusBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.2, leading=11.2,
        textColor=colors.HexColor('#0F172A')
    )
    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.HexColor('#FFFFFF')
    )
    td_style = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    td_bold = ParagraphStyle(
        'TDBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=10,
        textColor=colors.HexColor('#0F172A')
    )
    td_accent = ParagraphStyle(
        'TDAcct', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=10,
        textColor=colors.HexColor('#059669')
    )
    td_reject = ParagraphStyle(
        'TDReject', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=10,
        textColor=colors.HexColor('#DC2626')
    )

    story = []

    # ==================== COPERTINA / INTESTAZIONE ====================
    story.append(Paragraph("☀️ SunPro Engine System", subtitle_style))
    story.append(Paragraph("DOCUMENTO TECNICO-ESECUTIVO:<br/>SPECIFICHE DI RICERCA, VALUTAZIONE FONDIARIA & REPORT CRITICITÀ", title_style))
    story.append(Spacer(1, 5))

    # Box Metadata
    meta_data = [
        [Paragraph(
            "<b>Destinatari:</b> Soci, Sviluppatori FER, Fondi di Investimento Partner<br/>"
            "<b>Oggetto:</b> Origination Fondiaria, Metodo Estimativo Terreni, Destinazione Urbanistica PRG & Modello Finanziario<br/>"
            "<b>Autore & Architettura:</b> Nicola Valigi (Houdinick) — SunPro Engine System | <b>Data:</b> Ottobre 2026<br/>"
            "<b>Classificazione di Sicurezza:</b> STRICTLY CONFIDENTIAL — Proprietà Intellettuale Riservata",
            meta_box_style
        )]
    ]
    t_meta = Table(meta_data, colWidths=[18.0 * cm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=8))

    # ==================== SEZIONE 1: SINTESI ESECUTIVA ====================
    story.append(Paragraph("1. Sintesi Esecutiva: La Value Proposition di SunPro", h1_style))
    story.append(Paragraph(
        "Il motore <b>SunPro</b> è una piattaforma di <b>Geo-Intelligence predittiva</b> sviluppata per risolvere e "
        "industrializzare la fase a più alto assorbimento di tempo, capitale e rischio nello sviluppo fotovoltaico in Italia: "
        "l'<b>Origination Fondiaria</b>.",
        body_style
    ))
    story.append(Paragraph("• <b>Conformità Normativa Ex Lege (D.Lgs. 199/2021):</b> Isola aree idonee di diritto (350m Z.I., 300m autostrade, cave).", bullet_style))
    story.append(Paragraph("• <b>Zonizzazione Urbanistica & Gatekeeper:</b> Intercetta solo Zona E agricola; esclude categoricamente lotti edificabili industriali Zona D.", bullet_style))
    story.append(Paragraph("• <b>Metodo Estimativo Fondiario Reale:</b> Valuta i terreni su benchmark di mercato (VAM/ISMEA), non su astrazioni energetiche.", bullet_style))
    story.append(Paragraph("• <b>Grid Intelligence Istituzionale:</b> Integrato con <b>2.107 Cabine Primarie ARERA/GSE</b> e routing cavidotto stradale (1,30x).", bullet_style))
    story.append(Paragraph("• <b>Resa Scientifica PVGIS v5.2 (JRC):</b> Modella la producibilità per impianti a terra fissi e con tracker monoassiali.", bullet_style))
    story.append(Paragraph("• <b>Watchdog Vincoli Ambientali:</b> Verifica in tempo reale l'assenza di Rete Natura 2000 (ZPS/SIC) e rischio idrogeologico PAI.", bullet_style))
    story.append(Paragraph(
        "<b>Risultato:</b> Una pipeline di terreni non solo mappati, ma <i>verificati per reale acquistabilità fondiaria, "
        "quotati finanziariamente e pronti per l'iter autorizzativo accelerato (PAS in 60–90 giorni)</i>.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 2: EVOLUZIONE DALLA RELEASE INIZIALE ====================
    story.append(Paragraph("2. Evoluzione del Motore: Cosa è Cambiato dalla Release Iniziale (v1.0 vs v2.4)", h1_style))
    story.append(Paragraph(
        "Dalla release prototipale v1.0 all'attuale release industriale v2.4, il motore SunPro ha subito un'evoluzione "
        "radicale su tutti i pilastri tecnici, eliminando i fattori di rischio che causano il fallimento dei progetti fotovoltaici:",
        body_style
    ))
    t_evo_data = [
        [Paragraph("Ambito / Pilastro", th_style), Paragraph("Release Iniziale (v1.0)", th_style),
         Paragraph("Release Attuale (v2.4)", th_style), Paragraph("Impatto Strategico & Rischio Azzerato", th_style)],
        [Paragraph("<b>Composizione Suolo</b>", td_bold),
         Paragraph("Misto generico (inclusi lotti peri-urbani a rischio edifici)", td_style),
         Paragraph("<b>86,1% Seminativi Puri in Zona E</b> + Watchdog Suolo", td_accent),
         Paragraph("<b>Zero costi di demolizione o bonifica</b>; 100% campo aperto immediatamente cantierabile con pali infissi.", td_style)],
        [Paragraph("<b>Destinazione Urbanistica</b>", td_bold),
         Paragraph("Nessun controllo PRG (rischio acquisto lotti industriali Zona D)", td_style),
         Paragraph("<b>Gatekeeper Urbanistico</b>: scarto lotti Zona D (> 15 €/mq)", td_accent),
         Paragraph("Esclusi lotti industriali/PIP da 50–120 €/mq che renderebbero insostenibile il CAPEX a terra.", td_style)],
        [Paragraph("<b>Modello Estimativo</b>", td_bold),
         Paragraph("Stima forfettaria o derivata circolarmente da resa MWh", td_style),
         Paragraph("<b>Modello Immobiliare Comparativo</b> (VAM / ISMEA / OMI)", td_accent),
         Paragraph("Disaccoppiamento totale: prezzo ancorato ai benchmark provinciali reali (target <b>7,50–9,50 €/mq</b> o <b>3.000 €/ha/a</b>).", td_style)],
        [Paragraph("<b>Ingegneria di Rete</b>", td_bold),
         Paragraph("Distanze euclidee rettilinee su pochi punti cabina generici", td_style),
         Paragraph("<b>DB 2.107 Cabine Primarie ARERA</b> + Routing 1,30x", td_accent),
         Paragraph("Lookup istantaneo (<1ms); tortuosità stradale reale per stima CAPEX allaccio MT inattaccabile in due diligence.", td_style)],
        [Paragraph("<b>Resa Energetica & Tracker</b>", td_bold),
         Paragraph("Coefficienti statici forfettari; solo tilt fisso", td_style),
         Paragraph("<b>PVGIS v5.2 JRC</b>: Fisso vs <b>Tracker Monoassiale (+20%)</b>", td_accent),
         Paragraph("Dati scientifici Commissione UE; extra-CAPEX tracker ammortizzato in <3,5 anni con PPA a 85 €/MWh.", td_style)],
        [Paragraph("<b>Commercial Kit Pre-NDA</b>", td_bold),
         Paragraph("Solo report locali interni grezzi con dati sensibili esposti", td_style),
         Paragraph("<b>36 Blind Teaser PDF One-Pager</b> + 36 Dossier completi", td_accent),
         Paragraph("Avvio immediato del cold outreach verso fondi ed EPC tutelando al 100% l'IP prima della stipula dell'NDA.", td_style)],
    ]
    t_evo = Table(t_evo_data, colWidths=[3.5*cm, 4.3*cm, 4.8*cm, 5.4*cm])
    t_evo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
    ]))
    story.append(t_evo)
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 3: SPECIFICHE TECNICHE ====================
    story.append(Paragraph("3. Specifiche Tecniche di Ricerca & Filtri Territoriali", h1_style))
    t_spec_data = [
        [Paragraph("Parametro", th_style), Paragraph("Soglia / Requisito Applicato", th_style), Paragraph("Razionale Tecnico & Impatto di Business", th_style)],
        [Paragraph("<b>Superficie Minima</b>", td_bold), Paragraph("&ge; <b>2,0 Ettari (20.000 mq)</b>", td_accent),
         Paragraph("Dimensione minima per ammortizzare i costi fissi di cabina MT e iter autorizzativo (~1,6 – 2,0 MWp).", td_style)],
        [Paragraph("<b>Superficie Massima</b>", td_bold), Paragraph("Fino a <b>150 Ettari</b> (1.500.000 mq)", td_style),
         Paragraph("Copertura estesa per parchi utility-scale ed agrivoltaico avanzato PNRR.", td_style)],
        [Paragraph("<b>Densità di Potenza</b>", td_bold), Paragraph("<b>1,2 ha per 1,0 MWp</b> installato", td_style),
         Paragraph("Standard prudenziale compatibile sia con tracker monoassiali (pitch 5-6m) che strutture fisse.", td_style)],
        [Paragraph("<b>Buffer Zona Industriale</b>", td_bold), Paragraph("Entro <b>350 metri</b> da Z.I. / P.I.P.", td_accent),
         Paragraph("Area Idonea ex lege D.Lgs. 199/2021 (Art. 20 co. 8 lett. c-ter). Rischio paesaggistico azzerato.", td_style)],
        [Paragraph("<b>Buffer Autostradale</b>", td_bold), Paragraph("Entro <b>300 metri</b> da assi autostradali", td_accent),
         Paragraph("Area Idonea ex lege D.Lgs. 199/2021 (Art. 20 co. 8 lett. c-quater). Fascia di rispetto viaria.", td_style)],
        [Paragraph("<b>Cave & Discariche</b>", td_bold), Paragraph("Bacini dismessi a cielo aperto", td_accent),
         Paragraph("Idoneità primaria assoluta ex lege. Consumo di suolo zero; recupero ambientale.", td_style)],
        [Paragraph("<b>Screening Vincoli</b>", td_bold), Paragraph("Zero ZPS/SIC, Fuori PAI Fascia A", td_accent),
         Paragraph("Presunzione di iter con <b>PAS (Procedura Abilitativa Semplificata, 60–90 gg)</b> con certezza al 95%.", td_style)],
        [Paragraph("<b>Watchdog Anti-Edifici</b>", td_bold), Paragraph("<b>Zero Capannoni / Zero Case</b>", td_accent),
         Paragraph("Esclusione contesti urbani densi; <b>86% della pipeline costituito da veri terreni agricoli a campo aperto (Zona E)</b>.", td_style)],
    ]
    t_spec = Table(t_spec_data, colWidths=[4.0*cm, 5.0*cm, 9.0*cm])
    t_spec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_spec)
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 4: MODELLO ESTIMATIVO FONDIARIO ====================
    story.append(Paragraph("4. Come il Motore Determina il Valore del Terreno (Risposta Tecnica per i Soci)", h1_style))
    
    # Box di Chiarimento Fondamentale
    clarification_box = [
        [Paragraph(
            "<b>CHIARIMENTO METODOLOGICO CRUCIALE: RESA ENERGETICA VS VALORE DI MERCATO DEL TERRENO</b><br/>"
            "Il motore SunPro <b>NON determina il prezzo del terreno in base alla resa energetica solare</b>.<br/>"
            "Determinare il costo fondiario a partire dai MWh produrrebbe una valutazione circolare e astratta che porterebbe a sovrastimare "
            "i terreni. La resa energetica PVGIS serve <i>esclusivamente a valle</i> per calcolare ricavi, LCOE e Payback dell'investitore.<br/>"
            "Il valore del terreno è invece calcolato mediante un <b>Metodo Estimativo Sintetico-Comparativo Immobiliare</b>, "
            "fondato sulla <b>destinazione urbanistica (PRG/PGT)</b>, sui <b>valori agricoli medi reali (VAM/ISMEA)</b> e su <b>filtri anti-inacquistabilità</b>.",
            focus_box_body
        )]
    ]
    t_clarify = Table(clarification_box, colWidths=[18.0*cm])
    t_clarify.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor('#3B82F6')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(t_clarify)
    story.append(Spacer(1, 5))

    story.append(Paragraph("A. Destinazione Urbanistica e Filtro Gatekeeper Anti-Inacquistabilità", h2_style))
    story.append(Paragraph(
        "Il principale rischio nello scouting fondiario è confondere i <i>terreni agricoli adiacenti alla zona industriale</i> con i <i>lotti industriali edificabili</i>:<br/>"
        "• <b>La Trappola dei Lotti Industriali Zona D (Edificabili):</b> Se un lotto ricade dentro il perimetro industriale/PIP, "
        "il valore di mercato è di <b>50 – 120+ €/mq</b> (500k – 1,2M €/ha). A questi prezzi, nessun impianto FV a terra è sostenibile. "
        "<b>Gatekeeper SunPro:</b> Il crawler rileva la destinazione urbanistica. Qualsiasi lotto in Zona D o con quotazione > 15 €/mq viene "
        "<b>CATEGORICAMENTE SCARTATO</b> (Flag: <i>NON ACQUISTABILE — FUORI MERCATO</i>).<br/>"
        "• <b>La Selezione Chirurgica di SunPro (Zona E Agricola nel Buffer 350m):</b> Il D.Lgs. 199/2021 dichiara idonei i terreni <i>entro 350m</i> "
        "dalla zona industriale. SunPro intercetta unicamente terreni che a Piano Regolatore sono <b>ZONA E (Agricola Ordinaria)</b>: "
        "hanno costi fondiari agricoli contenuti ma godono dell'iter PAS accelerato per legge primaria!<br/>"
        "• <b>Priorità Assoluta ai Terreni Agricoli a Campo Aperto (86% della Pipeline):</b> "
        "Per escludere alla radice capannoni e case, SunPro seleziona grandi compendi agricoli aperti (Zona E - seminativi irrigui / agrivoltaico). "
        "I terreni agricoli sono l'asset più facile e conveniente: zero demolizioni, zero bonifiche, zero contenziosi. L'offerta SunPro a 3.000 €/ha/anno "
        "garantisce all'agricoltore 4x-6x la rendita agraria ordinaria, portando alla firma rapida del preliminare.<br/>"
        "• <b>Ex Cave & Discariche a Cielo Aperto (14% residuo):</b> Solo bacini a cielo aperto con fondo livellato, con esclusione totale di capannoni o fabbricati.",
        body_style
    ))

    story.append(Paragraph("B. Benchmark Fondiari di Mercato (VAM / ISMEA) & Formula Estimativa", h2_style))
    story.append(Paragraph(
        "Il motore applica il valore agricolo di base provinciale (VAM Agenzia Entrate / quotazioni ISMEA seminativo irriguo) "
        "e vi applica un <b>Coefficiente Posizionale Logistico (C_pos)</b> (+5% per accessibilità viaria/autostradale, +5% per contiguità con polo servito, penalizzazioni per forti pendenze). "
        "Per convincere l'agricoltore a cedere il terreno, SunPro applica il <b>Premio di Trasformazione Energetica (+40% a +80%)</b>:<br/>"
        "<b>Prezzo Acquisto Target = clamp(Valore_Mercato_Agricolo &times; 1,60, 7,50 €/mq, 9,50 €/mq)</b>",
        body_style
    ))

    t_val_data = [
        [Paragraph("Regione / Territorio", th_style), Paragraph("Benchmark Agricolo VAM/ISMEA", th_style),
         Paragraph("Affitto Agrario Ordinario", th_style), Paragraph("Offerta SunPro Acquisto Target", th_style), Paragraph("Canone Diritto Superficie SunPro", th_style)],
        [Paragraph("<b>Lombardia (Pianura Irrigua)</b>", td_bold), Paragraph("4,80 – 5,60 €/mq (48k – 56k €/ha)", td_style),
         Paragraph("550 – 700 €/ha/anno", td_style), Paragraph("<b>8,50 – 9,20 €/mq</b> (+55% premio)", td_accent), Paragraph("<b>€ 3.000 / ha / anno (4,6x)</b>", td_accent)],
        [Paragraph("<b>Veneto (Pianura Veneta)</b>", td_bold), Paragraph("4,40 – 5,20 €/mq (44k – 52k €/ha)", td_style),
         Paragraph("500 – 650 €/ha/anno", td_style), Paragraph("<b>8,20 – 9,00 €/mq</b> (+60% premio)", td_accent), Paragraph("<b>€ 3.000 / ha / anno (5,0x)</b>", td_accent)],
        [Paragraph("<b>Emilia-Romagna</b>", td_bold), Paragraph("4,20 – 5,30 €/mq (42k – 53k €/ha)", td_style),
         Paragraph("500 – 620 €/ha/anno", td_style), Paragraph("<b>8,00 – 8,80 €/mq</b> (+65% premio)", td_accent), Paragraph("<b>€ 3.000 / ha / anno (5,2x)</b>", td_accent)],
        [Paragraph("<b>Piemonte</b>", td_bold), Paragraph("3,20 – 4,50 €/mq (32k – 45k €/ha)", td_style),
         Paragraph("450 – 550 €/ha/anno", td_style), Paragraph("<b>7,80 – 8,50 €/mq</b> (+75% premio)", td_accent), Paragraph("<b>€ 3.000 / ha / anno (6,0x)</b>", td_accent)],
        [Paragraph("<b>Centro (Toscana, Umbria)</b>", td_bold), Paragraph("2,80 – 3,80 €/mq (28k – 38k €/ha)", td_style),
         Paragraph("350 – 450 €/ha/anno", td_style), Paragraph("<b>7,50 – 8,20 €/mq</b> (+80% premio)", td_accent), Paragraph("<b>€ 3.000 / ha / anno (7,0x)</b>", td_accent)],
        [Paragraph("<b>Lotto Zona D (Edificabile)</b>", td_reject), Paragraph("<b>50,00 – 120,00+ €/mq</b>", td_reject),
         Paragraph("Destinazione Industriale/PIP", td_style), Paragraph("<b>SCARTATO (NON ACQUISTABILE)</b>", td_reject), Paragraph("<b>SCARTATO DAL GATEKEEPER</b>", td_reject)],
    ]
    t_val = Table(t_val_data, colWidths=[4.2*cm, 4.0*cm, 3.2*cm, 3.4*cm, 3.2*cm])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Impatto di Business:</b> Il premio di trasformazione fondiaria rende l'offerta di SunPro irresistibile per l'agricoltore "
        "(incassa il +50%/+80% rispetto a vendere a un vicino), mentre per l'investitore il costo del terreno incide solo per l'8-11% del CAPEX complessivo.",
        body_bold
    ))
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 5: RETE E PVGIS ====================
    story.append(Paragraph("5. Ingegneria di Rete & Resa Energetica Scientifica", h1_style))
    story.append(Paragraph(
        "• <b>Database Nazionale 2.107 Cabine Primarie ARERA / GSE:</b> Integrato in locale per tutti i distributori italiani "
        "(<i>E-Distribuzione, Unareti, Areti, Ireti, Inrete, V-Reti, Edyna, Set</i>). Lookup spaziale in <b>1 millisecondo</b>.<br/>"
        "• <b>Routing Stradale Cavidotto con Fattore 1,30x:</b> Supera le stime euclidee errate dei concorrenti applicando la tortuosità reale. "
        "Formula: <b>CAPEX Allaccio MT = (Distanza Stradale in km &times; 65.000 €/km) + 45.000 € (Stallo Cabina)</b>.<br/>"
        "• <b>Resa PVGIS v5.2 JRC (Fisso vs Tracker):</b> Tilt fisso ottimale (1.280 – 1.450 kWh/kWp/anno); con inseguitori monoassiali rotazione E-O "
        "boost del <b>+19,2% al Nord fino a +22,0% al Centro/Sud</b>, consentendo il rapido rientro dei +70k €/MWp di extra-CAPEX.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 6: SCORING ====================
    story.append(Paragraph("6. Algoritmo di Scoring Multicriterio (0–100) & Gatekeeper", h1_style))
    t_score_data = [
        [Paragraph("Pilastro", th_style), Paragraph("Peso Max", th_style), Paragraph("Regole di Attribuzione Punteggio", th_style)],
        [Paragraph("<b>1. Idoneità Normativa D.Lgs. 199/21</b>", td_bold), Paragraph("<b>30 pt</b>", td_accent),
         Paragraph("Cave/Discariche: 30pt | Buffer 350m Z.I.: 26pt | Buffer 300m Autostrada: 22pt | Buffer 500m: 14pt.", td_style)],
        [Paragraph("<b>2. Prossimità Cabina Primaria</b>", td_bold), Paragraph("<b>25 pt</b>", td_accent),
         Paragraph("&le; 500m: 25pt | &le; 1.000m: 21pt | &le; 1.500m: 16pt | &le; 2.500m: 11pt | &gt; 3.500m: 2pt.", td_style)],
        [Paragraph("<b>3. Convenienza Economica & Acquistabilità</b>", td_bold), Paragraph("<b>20 pt</b>", td_accent),
         Paragraph("Prezzo &le; 7,5 €/mq: 20pt | Target 7,5 - 9,0 €/mq: 18pt | 9 - 10 €/mq: 11pt | <b>Zona D / Prezzo > 15 €/mq: 0 pt (SCARTATO)</b>.", td_style)],
        [Paragraph("<b>4. Resa Solare & Dimensione</b>", td_bold), Paragraph("<b>15 pt</b>", td_accent),
         Paragraph("Insolazione regionale PVGIS (max 10pt) + Bonus scala (&ge; 100k mq: +5pt, &ge; 50k mq: +4pt, &ge; 20k mq: +3pt).", td_style)],
        [Paragraph("<b>5. Reperibilità della Proprietà</b>", td_bold), Paragraph("<b>10 pt</b>", td_accent),
         Paragraph("PEC + Telefono verificati: 10pt | PEC o Telefono: 8pt | Persona Giuridica: 7pt | Particella nota: 4pt.", td_style)],
    ]
    t_score = Table(t_score_data, colWidths=[5.5*cm, 2.5*cm, 10.0*cm])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Rating Commerciale:</b> &ge; 75 = <b>TOP OPPORTUNITÀ</b> | 60 – 74 = <b>QUALIFICATO</b> | &lt; 60 = <b>SECONDARIO</b> | "
        "<b>NON ACQUISTABILE (SOVRASTIMATO)</b> = Terreni scartati a monte dal Gatekeeper.",
        body_bold
    ))
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 7: MODELLO FINANZIARIO ====================
    story.append(Paragraph("7. Modello Finanziario & Redditività a Confronto", h1_style))
    t_fin_data = [
        [Paragraph("Parametro Economico", th_style), Paragraph("Scenario Diritto di Superficie (30 Anni)", th_style), Paragraph("Scenario Acquisto Diretto", th_style)],
        [Paragraph("<b>Costo Fondiario</b>", td_bold), Paragraph("<b>€ 3.000 / ha / anno</b> (~0,30 €/mq/anno)", td_accent),
         Paragraph("<b>€ 7,80 – 9,20 / mq</b> (Valore target SunPro a rogito)", td_style)],
        [Paragraph("<b>CAPEX EPC Impianto</b>", td_bold), Paragraph("Fisso: <b>€ 680k/MWp</b> | Tracker: <b>€ 750k/MWp</b>", td_style),
         Paragraph("Fisso: <b>€ 680k/MWp</b> | Tracker: <b>€ 750k/MWp</b>", td_style)],
        [Paragraph("<b>Prezzo Energia (Capture)</b>", td_bold), Paragraph("<b>€ 85,0 / MWh</b> (PPA / Prezzo Zonale)", td_style),
         Paragraph("<b>€ 85,0 / MWh</b> (PPA / Prezzo Zonale)", td_style)],
        [Paragraph("<b>OPEX Annuo O&M</b>", td_bold), Paragraph("Fisso: € 14k/MWp/a | Tracker: € 16k/MWp/a", td_style),
         Paragraph("Fisso: € 14k/MWp/a | Tracker: € 16k/MWp/a", td_style)],
        [Paragraph("<b>Payback Medio Stimato</b>", td_bold), Paragraph("<b>Immediato / Alto IRR di Progetto</b>", td_accent),
         Paragraph("<b>6,3 – 7,1 Anni</b> (Payback semplice)", td_accent)],
        [Paragraph("<b>Consigliato per:</b>", td_bold), Paragraph("Sviluppatori puri, Fondi Infrastrutturali, EPC", td_accent),
         Paragraph("Investitori patrimoniali, CPO, Proprietà a lungo termine", td_style)],
    ]
    t_fin = Table(t_fin_data, colWidths=[4.2*cm, 6.9*cm, 6.9*cm])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 8: CRITICITÀ ====================
    story.append(Paragraph("8. Report delle Criticità & Analisi dei Rischi (Gap Analysis)", h1_style))
    def make_criticity_card(num, title, risk, impact, mitigation):
        card_data = [
            [Paragraph(f"⚠️ CRITICITÀ {num}: {title.upper()}", alert_box_title)],
            [Paragraph(f"<b>Descrizione del Rischio:</b> {risk}", alert_box_body)],
            [Paragraph(f"<b>Impatto di Business:</b> {impact}", alert_box_body)],
            [Paragraph(f"<b>Soluzione Operativa SunPro:</b> {mitigation}", alert_box_body)],
        ]
        t_card = Table(card_data, colWidths=[18.0 * cm])
        t_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')),
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#F59E0B')),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        return t_card

    story.append(make_criticity_card(
        1, "Saturazione Elettrica della Cabina (Hosting Capacity)",
        "La cabina primaria fisica è vicina (< 1,5 km), ma potrebbe essere virtualmente satura per troppe richieste di connessione già depositate da terzi.",
        "Rischio di preventivo TICA/STMG con obbligo di allaccio su stazioni in Alta Tensione remote e aumento del CAPEX.",
        "Incrociare i codici identificativi COD_AC con i report trimestrali di saturazione E-Distribuzione, penalizzando nello score le cabine con semaforo 'Rosso'."
    ))
    story.append(Spacer(1, 3))

    story.append(make_criticity_card(
        2, "Risoluzione Catastale Puntuale da Open Data",
        "Gli Open Data regionali identificano perfettamente la geometria baricentrica e l'estensione in ettari, ma non contengono l'elenco esatto di ogni singola particella catastale.",
        "Finché non si estraggono i singoli numeri di particella non è possibile depositare l'istanza formale di connessione.",
        "Strategia a 'Imbuto Inverso': presentare agli investitori i Blind Teaser commerciali; acquistare le visure catastali ufficiali (~0,20 € - 1,00 €) solo sulle aree in cui lo sviluppatore firma una Lettera d'Intenti (LOI/NDA)."
    ))
    story.append(Spacer(1, 3))

    story.append(make_criticity_card(
        3, "Frammentazione della Proprietà Fondiaria",
        "Su terreni agricoli molto estesi (15-30 ha), la proprietà può essere frazionata tra decine di coeredi o privati.",
        "Rischio di trattative infinite o veti incrociati che bloccano la firma del contratto di opzione.",
        "L'algoritmo di SunPro attribuisce un punteggio prioritario alle Persone Giuridiche (società agricole, aziende di cave, curatele fallimentari, immobiliari) rispetto ai privati, garantendo interlocutori unici."
    ))
    story.append(Spacer(1, 3))

    story.append(make_criticity_card(
        4, "Pendenze e Morfologia Locale di Dettaglio",
        "Un terreno può essere idoneo in pianta 2D ma presentare pendenze verso Nord superiori al 10% o avvallamenti complessi.",
        "Extracosti di sbancamento e movimentazione terra, oppure perdite di rendimento per ombreggiamento orografico.",
        "Screening preventivo tramite modelli digitali di elevazione (DEM Copernicus 25m) ed esame in volo orbitale 3D prima del sopralluogo sul campo."
    ))
    story.append(Spacer(1, 3))

    story.append(make_criticity_card(
        5, "Recepimento Regionale del Decreto Aree Idonee",
        "Le singole Regioni stanno approvando leggi locali di recepimento del D.M. Aree Idonee che potrebbero introdurre buffer restrittivi.",
        "Variazione dei criteri di autorizzabilità a seconda del territorio regionale.",
        "Mantenere il focus d'acciaio sulle aree brownfield (cave dismesse, discariche, adiacenze industriali entro 350m) che per legge statale primaria sono idonee su tutto il territorio nazionale senza deroghe."
    ))
    story.append(Spacer(1, 6))

    # ==================== SEZIONE 8: ROADMAP ====================
    story.append(Paragraph("8. Roadmap di Scalabilità & Consigli per i Soci", h1_style))
    story.append(Paragraph("1. <b>Go-to-Market Immediato sui 36 Lead Qualificati:</b> Utilizzare i 36 <i>Blind Teaser PDF One-Pager</i> per avviare il cold outreach confidenziale verso sviluppatori ed EPC primari (Ewiva, Atlante, Electra, Renantis, Sonnedix).", bullet_style))
    story.append(Paragraph("2. <b>Tutela del Valore tramite NDA:</b> Rilasciare i dati catastali completi e l'identità del proprietario solo previa sottoscrizione dell'Accordo di Riservatezza / LOI con Nicola Valigi.", bullet_style))
    story.append(Paragraph("3. <b>Espansione Territoriale a Costo Zero:</b> Sfruttare il nuovo database nazionale di 2.107 Cabine Primarie per estendere il crawler a Toscana, Piemonte, Veneto e Puglia senza spendere in licenze esterne.", bullet_style))
    story.append(Paragraph("4. <b>Micro-Budget per Chiusura Deal:</b> Allocare un fondo prepagato di circa 100 € - 200 € in crediti API catastali (es. Openapi.it) da utilizzare unicamente per scaricare le visure ufficiali sui deal con trattativa avviata.", bullet_style))
    story.append(Spacer(1, 6))

    # Box di chiusura
    sign_data = [
        [Paragraph(
            "<b>PIATTAFORMA SUNPRO — GEO-INTELLIGENCE 3D</b><br/>"
            "Proprietà Intellettuale & Sviluppo Software: <b>Nicola Valigi (Houdinick)</b><br/>"
            "Repository Ufficiale: <b>https://github.com/nicolavaligi/sunpro</b> | Demo Live: <b>https://nicolavaligi.github.io/sunpro/</b>",
            meta_box_style
        )]
    ]
    t_sign = Table(sign_data, colWidths=[18.0 * cm])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor('#0F172A')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Copia per il web
    WEB_OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT_PDF, WEB_OUTPUT_PDF)

    print(f"✅ PDF generato con successo: {OUTPUT_PDF}")
    print(f"✅ Copia sincronizzata in: {WEB_OUTPUT_PDF}")
    return OUTPUT_PDF

if __name__ == "__main__":
    build_pdf()
