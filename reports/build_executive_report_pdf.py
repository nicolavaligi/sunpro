"""
Script per compilare REPORT_CRITICITA_E_SPECIFICHE_MOTORE in un PDF elegante,
professionale e pronto per essere condiviso con i soci e partner strategici.
Utilizza ReportLab 5.0 con numerazione pagine dinamica e layout executive.
Autore: Nicola Valigi Engine System
"""

import os
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
        self.drawString(1.5 * cm, 1.0 * cm, "© 2026 Nicola Valigi (Houdinick) — Tutti i diritti riservati")
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

    # Tipografia Custom
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor('#1E3A8A'), spaceAfter=10
    )
    meta_box_style = ParagraphStyle(
        'MetaBox', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155')
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=17,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12, spaceAfter=6, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155'), spaceAfter=5
    )
    body_bold = ParagraphStyle(
        'BodyBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#0F172A')
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155'), leftIndent=12, firstLineIndent=-8, spaceAfter=3
    )
    alert_box_title = ParagraphStyle(
        'AlertTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=12,
        textColor=colors.HexColor('#B45309')
    )
    alert_box_body = ParagraphStyle(
        'AlertBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor('#451A03')
    )
    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.HexColor('#FFFFFF')
    )
    td_style = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )
    td_bold = ParagraphStyle(
        'TDBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10.5,
        textColor=colors.HexColor('#0F172A')
    )
    td_accent = ParagraphStyle(
        'TDAcct', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10.5,
        textColor=colors.HexColor('#059669')
    )

    story = []

    # ==================== COPERTINA / INTESTAZIONE ====================
    story.append(Paragraph("☀️ SunPro Engine System", subtitle_style))
    story.append(Paragraph("DOCUMENTO TECNICO-ESECUTIVO:<br/>SPECIFICHE DI RICERCA, MOTORE & REPORT DELLE CRITICITÀ", title_style))
    story.append(Spacer(1, 6))

    # Box Metadata e Classificazione
    meta_data = [
        [Paragraph(
            "<b>Destinatari:</b> Soci, Sviluppatori FER, Fondi di Investimento Partner<br/>"
            "<b>Oggetto:</b> Origination Fondiaria, Qualificazione Normativa D.Lgs. 199/21 & Modello Finanziario Utility-Scale<br/>"
            "<b>Autore & Architettura:</b> Nicola Valigi (Houdinick) — SunPro Engine System | <b>Data:</b> Ottobre 2026<br/>"
            "<b>Classificazione di Sicurezza:</b> STRICTLY CONFIDENTIAL — Proprietà Intellettuale Riservata",
            meta_box_style
        )]
    ]
    t_meta = Table(meta_data, colWidths=[18.0 * cm])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1.0, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=10))

    # ==================== SEZIONE 1: SINTESI ESECUTIVA ====================
    story.append(Paragraph("1. Sintesi Esecutiva: La Value Proposition di SunPro", h1_style))
    story.append(Paragraph(
        "Il motore <b>SunPro</b> è una piattaforma di <b>Geo-Intelligence predittiva</b> sviluppata per risolvere e "
        "industrializzare la fase a più alto assorbimento di tempo, capitale e rischio nello sviluppo fotovoltaico in Italia: "
        "l'<b>Origination Fondiaria</b>.",
        body_style
    ))
    story.append(Paragraph(
        "Mentre il mercato tradizionale si affida a mediatori locali o sopralluoghi manuali frammentati, SunPro scansiona "
        "il territorio nazionale incrociando simultaneamente:",
        body_style
    ))
    story.append(Paragraph("• <b>Conformità Normativa Ex Lege (D.Lgs. 199/2021):</b> Isola aree idonee di diritto (350m Z.I., 300m autostrade, cave).", bullet_style))
    story.append(Paragraph("• <b>Grid Intelligence Istituzionale:</b> Integrato con <b>2.107 Cabine Primarie ARERA/GSE</b> e routing cavidotto stradale.", bullet_style))
    story.append(Paragraph("• <b>Resa Scientifica PVGIS v5.2 (JRC Commissione Europea):</b> Calcola la resa a terra per impianti fissi e tracker.", bullet_style))
    story.append(Paragraph("• <b>Watchdog Vincoli Ambientali:</b> Verifica in tempo reale l'assenza di Rete Natura 2000 (ZPS/SIC) e rischio idrogeologico PAI.", bullet_style))
    story.append(Paragraph("• <b>Modello Finanziario Utility-Scale:</b> Valuta canoni trentennali di diritto di superficie (€ 3.000/ha/anno), EBITDA e Payback.", bullet_style))
    story.append(Paragraph(
        "<b>Risultato:</b> Una pipeline di terreni non solo mappati, ma <i>già pre-qualificati, quotati finanziariamente e pronti "
        "per l'iter autorizzativo accelerato (PAS in 60–90 giorni)</i>.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ==================== SEZIONE 2: SPECIFICHE TECNICHE ====================
    story.append(Paragraph("2. Specifiche Tecniche di Ricerca & Filtri Territoriali", h1_style))
    story.append(Paragraph(
        "Il crawler applica una rigorosa politica di filtraggio a monte che scarta il 98% del territorio agricolo ordinario "
        "per concentrarsi unicamente su terreni a elevata probabilità di autorizzazione e bancabilità:",
        body_style
    ))

    t_spec_data = [
        [Paragraph("Parametro", th_style), Paragraph("Soglia / Requisito Applicato", th_style), Paragraph("Razionale Tecnico & Impatto di Business", th_style)],
        [Paragraph("<b>Superficie Minima</b>", td_bold), Paragraph("&ge; <b>2,0 Ettari (20.000 mq)</b>", td_accent),
         Paragraph("Dimensione minima per giustificare i costi fissi di sviluppo, cabina MT e oneri autorizzativi (~1,6 – 2,0 MWp).", td_style)],
        [Paragraph("<b>Superficie Massima</b>", td_bold), Paragraph("Fino a <b>150 Ettari</b> (1.500.000 mq)", td_style),
         Paragraph("Copertura estesa per grandi parchi utility-scale ed agrivoltaico avanzato PNRR.", td_style)],
        [Paragraph("<b>Densità di Potenza</b>", td_bold), Paragraph("<b>1,2 ha per 1,0 MWp</b> installato", td_style),
         Paragraph("Standard prudenziale compatibile sia con tracker monoassiali (pitch 5-6m) che strutture fisse.", td_style)],
        [Paragraph("<b>Buffer Zona Industriale</b>", td_bold), Paragraph("Entro <b>350 metri</b> da Z.I. / P.I.P.", td_accent),
         Paragraph("Area Idonea ex lege D.Lgs. 199/2021 (Art. 20 co. 8 lett. c-ter). Rischio paesaggistico azzerato.", td_style)],
        [Paragraph("<b>Buffer Autostradale</b>", td_bold), Paragraph("Entro <b>300 metri</b> da assi autostradali", td_accent),
         Paragraph("Area Idonea ex lege D.Lgs. 199/2021 (Art. 20 co. 8 lett. c-quater). Fascia di rispetto infrastrutturale.", td_style)],
        [Paragraph("<b>Cave & Discariche</b>", td_bold), Paragraph("Bacini dismessi, cave, brownfield", td_accent),
         Paragraph("Idoneità primaria assoluta ex lege. Consumo di suolo zero; massimizzazione del consenso locale.", td_style)],
        [Paragraph("<b>Screening Vincoli</b>", td_bold), Paragraph("Zero ZPS/SIC, Fuori PAI Fascia A", td_accent),
         Paragraph("Presunzione di iter con <b>PAS (Procedura Abilitativa Semplificata, 60–90 gg)</b> con certezza al 95%.", td_style)],
    ]
    t_spec = Table(t_spec_data, colWidths=[4.2*cm, 5.2*cm, 8.6*cm])
    t_spec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_spec)
    story.append(Spacer(1, 8))

    # ==================== SEZIONE 3: RETE E PVGIS ====================
    story.append(Paragraph("3. Ingegneria di Rete & Resa Energetica Scientifica", h1_style))
    story.append(Paragraph(
        "Uno dei maggiori differenziali competitivi di SunPro risiede nella precisione dei calcoli infrastrutturali ed energetici:",
        body_style
    ))

    story.append(Paragraph("A. Database Nazionale 2.107 Cabine Primarie ARERA / GSE", h2_style))
    story.append(Paragraph(
        "Il motore ingloba in memoria l'intero dataset istituzionale delle <b>2.107 Cabine Primarie</b> di tutti i distributori "
        "nazionali (<i>e-distribuzione, Unareti/A2A, Areti/Acea, Ireti, Inrete/Hera, V-Reti, Edyna, Set, Deval</i>). "
        "Questo consente di calcolare all'istante la cabina più vicina per qualsiasi coordinata in Italia in <b>1 millisecondo</b>.",
        body_style
    ))

    story.append(Paragraph("B. Routing Stradale Cavidotto con Fattore di Tortuosità 1,30x", h2_style))
    story.append(Paragraph(
        "I software tradizionali misurano la distanza in linea d'aria euclidea, sottostimando i costi di allaccio del 30–40%. "
        "SunPro applica un <b>coefficiente geometrico infrastrutturale di 1,30x</b> lungo la viabilità pubblica e le servitù di "
        "passaggio obbligate. La formula parametrica di CAPEX allaccio MT adottata è:<br/>"
        "<b>CAPEX Allaccio MT = (Distanza Stradale in km &times; 65.000 €/km) + 45.000 € (Stallo Cabina Primaria)</b>",
        body_style
    ))

    story.append(Paragraph("C. Resa Energetica PVGIS v5.2 JRC: Strutture Fisse vs Tracker Monoassiale", h2_style))
    story.append(Paragraph(
        "Il motore interroga l'algoritmo scientifico PVGIS della Commissione Europea modellando due configurazioni impiantistiche:<br/>"
        "• <b>Tilt Fisso Ottimale:</b> 1.280 – 1.450 kWh/kWp/anno al Nord e Centro Italia.<br/>"
        "• <b>Inseguitori Monoassiali (Tracker N-S con rotazione Est-Ovest):</b> Boost di producibilità pari al <b>+19,2% al Nord fino a +22,0% al Centro/Sud</b>. "
        "Questo permette ai soci e agli sviluppatori di valutare l'extra-ricavo annuo a fronte del maggior costo iniziale dei tracker.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ==================== SEZIONE 4: SCORING ====================
    story.append(Paragraph("4. Algoritmo di Scoring Multicriterio (0–100)", h1_style))
    story.append(Paragraph(
        "Ogni area analizzata viene valutata tramite una matrice di scoring oggettiva ponderata su 5 pilastri cardine:",
        body_style
    ))

    t_score_data = [
        [Paragraph("Pilastro", th_style), Paragraph("Peso Max", th_style), Paragraph("Regole di Attribuzione Punteggio", th_style)],
        [Paragraph("<b>1. Idoneità Normativa D.Lgs. 199/21</b>", td_bold), Paragraph("<b>30 pt</b>", td_accent),
         Paragraph("Cave/Discariche: 30pt | Buffer 350m Z.I.: 26pt | Buffer 300m Autostrada: 22pt | Buffer 500m: 14pt.", td_style)],
        [Paragraph("<b>2. Prossimità Cabina Primaria</b>", td_bold), Paragraph("<b>25 pt</b>", td_accent),
         Paragraph("&le; 500m: 25pt | &le; 1.000m: 21pt | &le; 1.500m: 16pt | &le; 2.500m: 11pt | &gt; 3.500m: 2pt.", td_style)],
        [Paragraph("<b>3. Convenienza Economica Prezzo</b>", td_bold), Paragraph("<b>20 pt</b>", td_accent),
         Paragraph("Prezzo &le; 7,5 €/mq: 20pt | Target 7,5 - 9,0 €/mq: 18pt | 9 - 10 €/mq: 11pt | &gt; 12 €/mq: 1pt.", td_style)],
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
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_score)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Rating Commerciale:</b> Score &ge; 75 = <b>TOP OPPORTUNITÀ</b> (Priorità immediata outreach) | "
        "Score 60 – 74 = <b>QUALIFICATO</b> (Ottimo potenziale) | Score &lt; 60 = <b>SECONDARIO</b>.",
        body_bold
    ))
    story.append(Spacer(1, 8))

    # ==================== SEZIONE 5: MODELLO FINANZIARIO ====================
    story.append(Paragraph("5. Modello Finanziario & Redditività a Confronto", h1_style))
    story.append(Paragraph(
        "Il modello economico esecutivo confronta due scenari contrattuali basati su benchmark attuali di mercato utility-scale Italia:",
        body_style
    ))

    t_fin_data = [
        [Paragraph("Parametro Economico", th_style), Paragraph("Scenario Diritto di Superficie (30 Anni)", th_style), Paragraph("Scenario Acquisto Diretto", th_style)],
        [Paragraph("<b>Costo Fondiario</b>", td_bold), Paragraph("<b>€ 3.000 / ha / anno</b> (~0,30 €/mq/anno)", td_accent),
         Paragraph("<b>€ 8,00 – 9,00 / mq</b> (CAPEX fondiario a bilancio)", td_style)],
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
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 10))

    # ==================== SEZIONE 6: CRITICITÀ ====================
    story.append(Paragraph("6. Report delle Criticità & Analisi dei Rischi (Gap Analysis)", h1_style))
    story.append(Paragraph(
        "Di seguito si riportano con la massima trasparenza le <b>5 criticità operative</b> riscontrabili nell'origination "
        "e le relative contromisure implementate in SunPro:",
        body_style
    ))

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
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        return t_card

    story.append(make_criticity_card(
        1, "Saturazione Elettrica della Cabina (Hosting Capacity)",
        "La cabina primaria fisica è vicina (< 1,5 km), ma potrebbe essere virtualmente satura per troppe richieste di connessione già depositate da altri sviluppatori.",
        "Rischio di preventivo TICA/STMG con obbligo di allaccio su stazioni in Alta Tensione remote e aumento del CAPEX.",
        "Incrociare i codici identificativi COD_AC con i report trimestrali di saturazione E-Distribuzione, penalizzando nello score le cabine con semaforo 'Rosso'."
    ))
    story.append(Spacer(1, 4))

    story.append(make_criticity_card(
        2, "Risoluzione Catastale Puntuale da Open Data",
        "Gli Open Data regionali identificano perfettamente la geometria baricentrica e l'estensione in ettari, ma non contengono l'elenco esatto di ogni singola particella catastale.",
        "Finché non si estraggono i singoli numeri di particella non è possibile depositare l'istanza formale di connessione.",
        "Strategia a 'Imbuto Inverso': presentare agli investitori i Blind Teaser commerciali; acquistare le visure catastali ufficiali (~0,20 € - 1,00 €) solo sulle aree in cui lo sviluppatore firma una Lettera d'Intenti (LOI/NDA)."
    ))
    story.append(Spacer(1, 4))

    story.append(make_criticity_card(
        3, "Frammentazione della Proprietà Fondiaria",
        "Su terreni agricoli molto estesi (15-30 ha), la proprietà può essere frazionata tra decine di coeredi o privati.",
        "Rischio di trattative infinite o veti incrociati che bloccano la firma del contratto di opzione.",
        "L'algoritmo di SunPro attribuisce un punteggio prioritario alle Persone Giuridiche (società agricole, aziende di cave, curatele fallimentari, immobiliari) rispetto ai privati, garantendo interlocutori unici."
    ))
    story.append(Spacer(1, 4))

    story.append(make_criticity_card(
        4, "Pendenze e Morfologia Locale di Dettaglio",
        "Un terreno può essere idoneo in pianta 2D ma presentare pendenze verso Nord superiori al 10% o avvallamenti complessi.",
        "Extracosti di sbancamento e movimentazione terra, oppure perdite di rendimento per ombreggiamento.",
        "Screening preventivo tramite modelli digitali di elevazione (DEM Copernicus 25m) ed esame in volo orbitale 3D MapLibre prima del sopralluogo sul campo."
    ))
    story.append(Spacer(1, 4))

    story.append(make_criticity_card(
        5, "Recepimento Regionale del Decreto Aree Idonee",
        "Le singole Regioni stanno approvando leggi locali di recepimento del D.M. Aree Idonee che potrebbero introdurre buffer restrittivi.",
        "Variazione dei criteri di autorizzabilità a seconda del territorio regionale.",
        "Mantenere il focus d'acciaio sulle aree brownfield (cave dismesse, discariche, adiacenze industriali entro 350m) che per legge statale primaria sono idonee su tutto il territorio nazionale senza deroghe."
    ))
    story.append(Spacer(1, 8))

    # ==================== SEZIONE 7: ROADMAP ====================
    story.append(Paragraph("7. Roadmap di Scalabilità & Consigli per i Soci", h1_style))
    story.append(Paragraph(
        "Per massimizzare il valore economico del sistema e generare operazioni commerciali ad alto rendimento, "
        "si raccomandano i seguenti passi esecutivi:",
        body_style
    ))
    story.append(Paragraph("1. <b>Go-to-Market Immediato sui 36 Lead Qualificati:</b> Utilizzare i 36 <i>Blind Teaser PDF One-Pager</i> per avviare il cold outreach confidenziale verso sviluppatori ed EPC primari (Ewiva, Atlante, Electra, Renantis, Sonnedix).", bullet_style))
    story.append(Paragraph("2. <b>Tutela del Valore tramite NDA:</b> Rilasciare i dati catastali completi e l'identità del proprietario solo previa sottoscrizione dell'Accordo di Riservatezza / LOI con Nicola Valigi.", bullet_style))
    story.append(Paragraph("3. <b>Espansione Territoriale a Costo Zero:</b> Sfruttare il nuovo database nazionale di 2.107 Cabine Primarie per estendere il crawler a Toscana, Piemonte, Veneto e Puglia senza spendere in licenze esterne.", bullet_style))
    story.append(Paragraph("4. <b>Micro-Budget per Chiusura Deal:</b> Allocare un fondo prepagato di circa 100 € - 200 € in crediti API catastali (es. Openapi.it) da utilizzare unicamente per scaricare le visure ufficiali sui deal con trattativa avviata.", bullet_style))
    story.append(Spacer(1, 10))

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
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Copia per il web
    WEB_OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(OUTPUT_PDF, WEB_OUTPUT_PDF)

    print(f"✅ PDF generato con successo: {OUTPUT_PDF}")
    print(f"✅ Copia sincronizzata in: {WEB_OUTPUT_PDF}")
    return OUTPUT_PDF

if __name__ == "__main__":
    build_pdf()
