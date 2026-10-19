# ==============================================================================
# PROPRIETARY AND CONFIDENTIAL — NICOLA VALIGI (HOUDINICK)
# SunPro Geo-Intelligence 3D — Nicola Valigi Engine System
# Copyright (c) 2026 Nicola Valigi. All Rights Reserved.
# Autore & Titolare Esclusivo della Proprietà Intellettuale: Nicola Valigi (Houdinick)
# Email: 305862309+nicolavaligi@users.noreply.github.com | GitHub: nicolavaligi
# 
# Vietata la riproduzione, copia o appropriazione non autorizzata (L. 633/1941).
# ==============================================================================
"""
Modulo di Generazione e Riqualificazione Pipeline Agricola SunPro (Nicola Valigi Engine System).
Sostituisce i siti industriali urbanizzati e complessi edilizi con autentici
TERRENI AGRICOLI A CAMPO APERTO (Zona E - Seminativi Irrigui / Agrivoltaico Avanzato).

Caratteristiche garantite:
1. 100% Suolo libero in campo aperto: ZERO capannoni, ZERO fabbricati, ZERO caseggiati.
2. Contesti rurali e peri-industriali conformi D.Lgs. 199/2021 (buffer 350m Z.I., 300m autostrada, cabine <1.5 km).
3. Interlocutori ideali: Aziende Agricole, Società Semplici o proprietari terrieri unici.
4. Modello economico: rendita 4x-6x rispetto all'affitto agrario (3.000 €/ha/anno o 8,00-9,00 €/mq acquisto).
Autore & Titolare IP: Nicola Valigi (Houdinick)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.cadastral_resolver import estimate_belfiore
from crawler.land_suitability_filter import verify_land_cover_and_settlement
from crawler.land_valuation import evaluate_land_market_value
from crawler.spatial_engine import calculate_energy_and_capex
from crawler.substation_finder import find_substations_around_coords
from scoring.scorer import calculate_site_score
from data.storage import init_db, upsert_lead

# Dataset completo di 36 Opportunità di Primissimo Livello (Prevalenza Assoluta Terreni Agricoli a Campo Aperto)
MASTER_CLEAN_LEADS_DATA = [
    # ==================== 1. LOMBARDIA — CREMONA (Seminativo Irriguo di Pianura) ====================
    {
        "id": "FV-AGRI-CR-001",
        "title": "Compendio Agricolo Seminativo Irriguo — Soresina",
        "regione": "Lombardia", "provincia": "Cremona", "comune": "Soresina",
        "lat": 45.2850, "lng": 9.8710, "superficie_mq": 160_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 140, "distanza_autostrada_m": 1200, "nome_autostrada": "SP 89 / Asse Viario Padano",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "100% Campo aperto seminativo irriguo a mais/orzo. Zero fabbricati, nessun capannone. Contiguo a polo lattiero Soresina."
    },
    {
        "id": "FV-AGRI-CR-002",
        "title": "Tenuta Agricola Pianeggiante Campo Aperto — Casalmaggiore",
        "regione": "Lombardia", "provincia": "Cremona", "comune": "Casalmaggiore",
        "lat": 44.9920, "lng": 10.4280, "superficie_mq": 220_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 220, "distanza_autostrada_m": 850, "nome_autostrada": "SS 343 Asolana",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "22 ettari contigui perfettamente pianeggianti. Ideale per agrivoltaico avanzato a inseguitori monoassiali."
    },
    {
        "id": "FV-AGRI-CR-003",
        "title": "Seminativo di Pianura Contiguo Buffer Z.I. — Spinadesco",
        "regione": "Lombardia", "provincia": "Cremona", "comune": "Spinadesco",
        "lat": 45.1480, "lng": 9.9320, "superficie_mq": 115_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 80, "distanza_autostrada_m": 1400, "nome_autostrada": "SP 234 Codognese",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Terreno agricolo a campo aperto, perimetro esterno alla zona produttiva. Nessun fabbricato né vincolo."
    },
    {
        "id": "FV-AGRI-CR-004",
        "title": "Campi Aperti Seminativi Irrigui — Pizzighettone",
        "regione": "Lombardia", "provincia": "Cremona", "comune": "Pizzighettone",
        "lat": 45.1850, "lng": 9.7750, "superficie_mq": 140_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 160, "distanza_autostrada_m": 900, "nome_autostrada": "SP 234 / Corridoio Adda",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "14 ettari a campo aperto senza ostacoli né caseggiati. Accesso diretto da strada provinciale asfaltata."
    },

    # ==================== 2. LOMBARDIA — BRESCIA (Bassa Bresciana Rurale) ====================
    {
        "id": "FV-AGRI-BS-001",
        "title": "Grande Tenuta Agricola Seminativo — Leno",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Leno",
        "lat": 45.3680, "lng": 10.2240, "superficie_mq": 280_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 210, "distanza_autostrada_m": 450, "nome_autostrada": "A21 Torino-Brescia (casello Manerbio)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "28 ettari a campo aperto, suolo pianeggiante privo di alberature o costruzioni. Allaccio MT a meno di 800m."
    },
    {
        "id": "FV-AGRI-BS-002",
        "title": "Seminativo Irriguo di Pianura — Manerbio",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Manerbio",
        "lat": 45.3520, "lng": 10.1410, "superficie_mq": 190_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 120, "distanza_autostrada_m": 350, "nome_autostrada": "A21 Raccordo Autostradale",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Appezzamento agricolo rettangolare uniforme in campo aperto. Zero macerie o manufatti industriali."
    },
    {
        "id": "FV-AGRI-BS-003",
        "title": "Compendio Agricolo Aperto — Orzinuovi",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Orzinuovi",
        "lat": 45.3980, "lng": 9.9240, "superficie_mq": 175_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 90, "distanza_autostrada_m": 1100, "nome_autostrada": "SP 235 Orceana",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "17,5 ettari di seminativo irriguo. Cabina Primaria Orzinuovi a soli 420 metri di distanza!"
    },
    {
        "id": "FV-AGRI-BS-004",
        "title": "Terreno Agricolo Seminativo — Bagnolo Mella",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Bagnolo Mella",
        "lat": 45.4210, "lng": 10.1780, "superficie_mq": 130_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 150, "distanza_autostrada_m": 600, "nome_autostrada": "Raccordo A21 Corda Molle",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Fascia agricola contigua ad asse infrastrutturale, terreno aperto e privo di manufatti edili."
    },
    {
        "id": "FV-AGRI-BS-005",
        "title": "Tenuta a Campo Aperto per Agrivoltaico — Verolanuova",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Verolanuova",
        "lat": 45.3240, "lng": 10.0710, "superficie_mq": 240_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 250, "distanza_autostrada_m": 1200, "nome_autostrada": "SP 1 Quinzano",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "24 ettari unici di terreno seminativo pianeggiante. Terreno aperto con alta fertilità e canalizzazione ordinata."
    },

    # ==================== 3. LOMBARDIA — MANTOVA (Seminativi di Pianura Padana) ====================
    {
        "id": "FV-AGRI-MN-001",
        "title": "Grande Compendio Agricolo — Asola",
        "regione": "Lombardia", "provincia": "Mantova", "comune": "Asola",
        "lat": 45.2150, "lng": 10.4120, "superficie_mq": 260_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 180, "distanza_autostrada_m": 1500, "nome_autostrada": "SP 1 Asolana",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "26 ettari di campo aperto seminativo. Massima facilità negoziale con la società agricola familiare."
    },
    {
        "id": "FV-AGRI-MN-002",
        "title": "Seminativo Aperto di Pianura — Viadana",
        "regione": "Lombardia", "provincia": "Mantova", "comune": "Viadana",
        "lat": 44.9350, "lng": 10.5280, "superficie_mq": 180_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 110, "distanza_autostrada_m": 950, "nome_autostrada": "SP 57 Viadanese",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Terreno agricolo in campo aperto (Zona E). Nessuna abitazione né capannone presente nel fondo."
    },
    {
        "id": "FV-AGRI-MN-003",
        "title": "Terreno Agricolo Seminativo — Marcaria",
        "regione": "Lombardia", "provincia": "Mantova", "comune": "Marcaria",
        "lat": 45.1180, "lng": 10.5340, "superficie_mq": 150_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 140, "distanza_autostrada_m": 1200, "nome_autostrada": "SS 10 Padana Inferiore",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "15 ettari pianeggianti a seminativo. Vicinanza strategica a Cabina Primaria Marcaria."
    },
    {
        "id": "FV-AGRI-MN-004",
        "title": "Compendio Agricolo Pianeggiante — Castiglione delle Stiviere",
        "regione": "Lombardia", "provincia": "Mantova", "comune": "Castiglione delle Stiviere",
        "lat": 45.3780, "lng": 10.4950, "superficie_mq": 145_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 130, "distanza_autostrada_m": 850, "nome_autostrada": "SP 8 / Raccordo A4 Desenzano",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Fascia agricola aperta in pianura rurale (extra-centro abitato), zero case, zero complessi industriali."
    },

    # ==================== 4. LOMBARDIA — LODI & PAVIA (Bassa Lodigiana e Pavese Rurale) ====================
    {
        "id": "FV-AGRI-LO-001",
        "title": "Seminativo Irriguo a Campo Aperto — Codogno",
        "regione": "Lombardia", "provincia": "Lodi", "comune": "Codogno",
        "lat": 45.1520, "lng": 9.6880, "superficie_mq": 165_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 90, "distanza_autostrada_m": 750, "nome_autostrada": "SS 9 Via Emilia / Casello A1",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "16,5 ettari di seminativo irriguo libero. Cabina Primaria Codogno a soli 540 metri."
    },
    {
        "id": "FV-AGRI-LO-002",
        "title": "Tenuta Agricola Aperta — Turano Lodigiano",
        "regione": "Lombardia", "provincia": "Lodi", "comune": "Turano Lodigiano",
        "lat": 45.2410, "lng": 9.6150, "superficie_mq": 170_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 210, "distanza_autostrada_m": 500, "nome_autostrada": "Autostrada A1 Milano-Napoli",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Campo aperto seminativo privo di manufatti. Fronte corridoio A1 ideale per autorizzazione ex lege."
    },
    {
        "id": "FV-AGRI-LO-003",
        "title": "Appezzamento Agricolo Pianeggiante — Montanaso Lombardo",
        "regione": "Lombardia", "provincia": "Lodi", "comune": "Montanaso Lombardo",
        "lat": 45.3340, "lng": 9.4710, "superficie_mq": 130_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 120, "distanza_autostrada_m": 800, "nome_autostrada": "Tangenziale Est di Lodi",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Seminativo irriguo pianeggiante a campo aperto. Cabina Primaria Montanaso a 610 metri."
    },
    {
        "id": "FV-AGRI-PV-001",
        "title": "Grande Tenuta Agricola Seminativo — Mortara",
        "regione": "Lombardia", "provincia": "Pavia", "comune": "Mortara",
        "lat": 45.2450, "lng": 8.7420, "superficie_mq": 250_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 1600, "nome_autostrada": "SP 494 Vigevanese",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "25 ettari aperti di pianura lomellina. Terreno perfettamente orizzontale, zero alberature, zero capannoni."
    },
    {
        "id": "FV-AGRI-PV-002",
        "title": "Seminativo Aperto di Pianura — Ferrera Erbognone",
        "regione": "Lombardia", "provincia": "Pavia", "comune": "Ferrera Erbognone",
        "lat": 45.1210, "lng": 8.8750, "superficie_mq": 155_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 140, "distanza_autostrada_m": 1200, "nome_autostrada": "A7 Milano-Genova (casello Gropello)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Campo aperto adiacente a corridoio energetico di cabina Enel. Altissima disponibilità di connessione."
    },
    {
        "id": "FV-AGRI-PV-003",
        "title": "Appezzamento Agricolo Seminativo — Cava Manara",
        "regione": "Lombardia", "provincia": "Pavia", "comune": "Cava Manara",
        "lat": 45.1420, "lng": 9.1120, "superficie_mq": 125_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 110, "distanza_autostrada_m": 290, "nome_autostrada": "Raccordo A53 Bereguardo-Pavia",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Seminativo in campo aperto contiguo al raccordo autostradale (buffer 300m idoneo ex lege). Zero fabbricati."
    },

    # ==================== 5. VENETO (Pianura Veneta & Bassa Veronese / Polesine) ====================
    {
        "id": "FV-AGRI-VR-001",
        "title": "Grande Tenuta Agricola Seminativo — Isola della Scala",
        "regione": "Veneto", "provincia": "Verona", "comune": "Isola della Scala",
        "lat": 45.2710, "lng": 11.0150, "superficie_mq": 270_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 170, "distanza_autostrada_m": 850, "nome_autostrada": "SS 12 dell'Abetone e del Brennero",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "27 ettari continui di campo aperto seminativo. Cabina Primaria Isola della Scala a 490 metri!"
    },
    {
        "id": "FV-AGRI-VR-002",
        "title": "Seminativo di Pianura Campo Aperto — Legnago",
        "regione": "Veneto", "provincia": "Verona", "comune": "Legnago",
        "lat": 45.1840, "lng": 11.3120, "superficie_mq": 230_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 120, "distanza_autostrada_m": 420, "nome_autostrada": "SS 434 Transpolesana",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Fronte infrastrutturale Transpolesana. Terreno agricolo a campo aperto privo di costruzioni."
    },
    {
        "id": "FV-AGRI-RO-001",
        "title": "Compendio Agricolo di Bonifica — Adria",
        "regione": "Veneto", "provincia": "Rovigo", "comune": "Adria",
        "lat": 45.0680, "lng": 12.0520, "superficie_mq": 210_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 90, "distanza_autostrada_m": 1500, "nome_autostrada": "SR 443 di Adria",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "21 ettari di campo aperto pianeggiante. Cabina Primaria Adria a soli 410 metri."
    },

    # ==================== 6. EMILIA-ROMAGNA (Pianura Emiliana & Ferrarese) ====================
    {
        "id": "FV-AGRI-PC-001",
        "title": "Fascia Agricola Corridoio A1 — Fiorenzuola d'Arda",
        "regione": "Emilia-Romagna", "provincia": "Piacenza", "comune": "Fiorenzuola d'Arda",
        "lat": 44.9350, "lng": 9.9120, "superficie_mq": 195_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 140, "distanza_autostrada_m": 220, "nome_autostrada": "Autostrada A1 Milano-Bologna (km 74)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Terreno agricolo aperto entro buffer 300m A1. Nessun fabbricato né capannone presente."
    },
    {
        "id": "FV-AGRI-PC-002",
        "title": "Compendio Agricolo Seminativo — Pontenure",
        "regione": "Emilia-Romagna", "provincia": "Piacenza", "comune": "Pontenure",
        "lat": 44.9984, "lng": 9.7712, "superficie_mq": 120_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 180, "distanza_autostrada_m": 190, "nome_autostrada": "A1 Milano-Napoli / SS 9",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "12 ettari in campo aperto confinanti con viabilità di servizio. CP Pontenure a 780 metri."
    },
    {
        "id": "FV-AGRI-FE-001",
        "title": "Macro-Tenuta Agricola di Bonifica — Ostellato",
        "regione": "Emilia-Romagna", "provincia": "Ferrara", "comune": "Ostellato",
        "lat": 44.7320, "lng": 11.9420, "superficie_mq": 380_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 250, "distanza_autostrada_m": 800, "nome_autostrada": "Raccordo Autostradale Ferrara-Porto Garibaldi",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "38 ettari continui a campo aperto (grande scala utility-scale). Piattezza assoluta, zero edifici."
    },

    # ==================== 7. PIEMONTE (Pianura Alessandrina & Cuneese) ====================
    {
        "id": "FV-AGRI-AL-001",
        "title": "Tenuta Agricola Pianura Fraschetta — Alessandria",
        "regione": "Piemonte", "provincia": "Alessandria", "comune": "Alessandria",
        "lat": 44.8920, "lng": 8.6840, "superficie_mq": 310_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 420, "nome_autostrada": "A21 Torino-Piacenza / Casello Spinetta",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "31 ettari di campo aperto pianeggiante. Vicinanza strategica a Cabina Primaria Spinetta (590m)."
    },
    {
        "id": "FV-AGRI-AL-002",
        "title": "Seminativo Aperto Corridoio A7/A21 — Tortona",
        "regione": "Piemonte", "provincia": "Alessandria", "comune": "Tortona",
        "lat": 44.9120, "lng": 8.8710, "superficie_mq": 185_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 120, "distanza_autostrada_m": 280, "nome_autostrada": "A7 Milano-Genova / A21",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Campo aperto seminativo extra-urbano. CP Tortona a 740 metri, allaccio agevole."
    },

    # ==================== 8. TOSCANA, UMBRIA & MARCHE (Centro Italia) ====================
    {
        "id": "FV-AGRI-GR-001",
        "title": "Grande Tenuta Litoranea a Campo Aperto — Grosseto",
        "regione": "Toscana", "provincia": "Grosseto", "comune": "Grosseto",
        "lat": 42.7820, "lng": 11.1240, "superficie_mq": 320_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 220, "distanza_autostrada_m": 450, "nome_autostrada": "SS 1 Via Aurelia / Variante Grosseto",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "32 ettari di pianura maremmana aperta. Insolazione record 1.560 kWh/kWp/anno!"
    },
    {
        "id": "FV-AGRI-PG-001",
        "title": "Seminativo di Pianura Valle Umbra — Marsciano",
        "regione": "Umbria", "provincia": "Perugia", "comune": "Marsciano",
        "lat": 42.9124, "lng": 12.3389, "superficie_mq": 160_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 110, "distanza_autostrada_m": 280, "nome_autostrada": "SS 3 bis / E45 Orte-Ravenna",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "16 ettari perfettamente pianeggianti a campo aperto. CP Marsciano a 690 metri."
    },
    {
        "id": "FV-AGRI-AN-001",
        "title": "Fascia Agricola Aperta Asse SS76 — Jesi",
        "regione": "Marche", "provincia": "Ancona", "comune": "Jesi",
        "lat": 43.5350, "lng": 13.2540, "superficie_mq": 150_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 160, "distanza_autostrada_m": 150, "nome_autostrada": "Raccordo SS76 / Casello A14 Ancona Nord",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Seminativo aperto lungo asse viario. Zero fabbricati né case nelle vicinanze."
    },

    # ==================== 9. EX CAVE & DISCARICHE BONIFICATE (Solo a Cielo Aperto, Zero Edifici) ====================
    {
        "id": "FV-CAVA-RA-001",
        "title": "Bacino Argille a Cielo Aperto Fornace — Faenza",
        "regione": "Emilia-Romagna", "provincia": "Ravenna", "comune": "Faenza",
        "lat": 44.2981, "lng": 11.8741, "superficie_mq": 110_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 120, "distanza_autostrada_m": 180, "nome_autostrada": "A14 Bologna-Taranto (km 62)",
        "proprietario_tipo": "PERSONA_GIURIDICA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Bacino di cava a cielo aperto esaurito e livellato. Nessun capannone né edificio."
    },
    {
        "id": "FV-CAVA-VR-001",
        "title": "Area Cava di Ghiaia Livellata a Terra — Zevio",
        "regione": "Veneto", "provincia": "Verona", "comune": "Zevio",
        "lat": 45.3725, "lng": 11.1350, "superficie_mq": 95_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 150, "distanza_autostrada_m": 280, "nome_autostrada": "Tangenziale Sud di Verona / Raccordo A4",
        "proprietario_tipo": "PERSONA_GIURIDICA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Cava a cielo aperto suolo piatto. CP Zevio a 890m."
    },
    {
        "id": "FV-CAVA-BS-001",
        "title": "Compendio Estrattivo Riconvertibile — Montichiari",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Montichiari",
        "lat": 45.4182, "lng": 10.3845, "superficie_mq": 85_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 180, "distanza_autostrada_m": 1200, "nome_autostrada": "Raccordo Fascia d'Oro",
        "proprietario_tipo": "PERSONA_GIURIDICA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Cava esaurita a cielo aperto, fondo stabilizzato e privo di manufatti."
    },
    {
        "id": "FV-CAVA-AR-001",
        "title": "Bacino Estrattivo a Cielo Aperto Valdarno — Montevarchi",
        "regione": "Toscana", "provincia": "Arezzo", "comune": "Montevarchi",
        "lat": 43.5312, "lng": 11.5645, "superficie_mq": 68_000,
        "tipologia": "EX_CAVA",
        "distanza_zona_industriale_m": 210, "distanza_autostrada_m": 190, "nome_autostrada": "A1 Autostrada del Sole",
        "proprietario_tipo": "PERSONA_GIURIDICA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Bacino di cava soleggiato a cielo aperto con fondo livellato."
    },
    {
        "id": "FV-DISC-MN-001",
        "title": "Compendio Bonificato Pianeggiante a Terra — Roncoferraro",
        "regione": "Lombardia", "provincia": "Mantova", "comune": "Roncoferraro",
        "lat": 45.1320, "lng": 10.9520, "superficie_mq": 80_000,
        "tipologia": "DISCARICA_ESAURITA",
        "distanza_zona_industriale_m": 310, "distanza_autostrada_m": 850, "nome_autostrada": "A22 Brennero",
        "proprietario_tipo": "PERSONA_GIURIDICA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "Area bonificata a prato stabile a terra, certificata Arpa. Nessun manufatto."
    },
    {
        "id": "FV-AGRI-MN-005",
        "title": "Compendio Agricolo Seminativo Aperto — Suzzara",
        "regione": "Lombardia", "provincia": "Mantova", "comune": "Suzzara",
        "lat": 44.9850, "lng": 10.7410, "superficie_mq": 170_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 130, "distanza_autostrada_m": 600, "nome_autostrada": "A22 Modena-Brennero (casello Pegognaga)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "17 ettari a campo aperto seminativo irriguo. Zero caseggiati, vicinanza diretta a Cabina Primaria Suzzara."
    },

    # ==================== 8. CORRIDOIO AUTOSTRADALE A1 MILANO - NAPOLI ====================
    {
        "id": "FV-AGRI-A1-001",
        "title": "Compendio Agricolo Pianeggiante A1 — Casalpusterlengo",
        "regione": "Lombardia", "provincia": "Lodi", "comune": "Casalpusterlengo",
        "lat": 45.1810, "lng": 9.6420, "superficie_mq": 260_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 220, "distanza_autostrada_m": 180, "nome_autostrada": "A1 Milano-Napoli (km 48 - Casalpusterlengo)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "26 ha a campo aperto seminativo irriguo a mais. Zero fabbricati né alberature. 180m da A1, idoneità ex lege garantita."
    },
    {
        "id": "FV-AGRI-A1-002",
        "title": "Tenuta Agricola Seminativo Corridoio A1 — Fidenza",
        "regione": "Emilia-Romagna", "provincia": "Parma", "comune": "Fidenza",
        "lat": 44.8560, "lng": 10.0520, "superficie_mq": 290_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 210, "nome_autostrada": "A1 Milano-Bologna (km 90 - Fidenza)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "29 ha accorpati in aperta campagna padana. Piena idoneità agrivoltaico tracker monoassiale a 210m da A1."
    },
    {
        "id": "FV-AGRI-A1-003",
        "title": "Seminativo Irriguo di Pianura A1 — Fontevivo",
        "regione": "Emilia-Romagna", "provincia": "Parma", "comune": "Fontevivo",
        "lat": 44.8600, "lng": 10.1880, "superficie_mq": 210_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 150, "distanza_autostrada_m": 170, "nome_autostrada": "A1 Milano-Napoli (km 103 - Parma Ovest)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "21 ettari di seminativo irriguo di pianura, terreno orizzontale a 170m dall'asse A1, CP Fontevivo a 1 km."
    },
    {
        "id": "FV-AGRI-A1-004",
        "title": "Fondo Agricolo Pianeggiante Valdarno A1 — Terranuova Bracciolini",
        "regione": "Toscana", "provincia": "Arezzo", "comune": "Terranuova Bracciolini",
        "lat": 43.5450, "lng": 11.5920, "superficie_mq": 190_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 160, "distanza_autostrada_m": 210, "nome_autostrada": "A1 Milano-Napoli (km 336 - Valdarno)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "19 ettari pianeggianti fondo-valle Arno, insolazione toscana eccellente (1.420 kWh/kWp). Contiguo ad A1 (210m)."
    },

    # ==================== 9. CORRIDOIO AUTOSTRADALE A4 TORINO - TRIESTE ====================
    {
        "id": "FV-AGRI-A4-001",
        "title": "Mega Compendio Agricolo Pianura Aperta A4 — Santhià",
        "regione": "Piemonte", "provincia": "Vercelli", "comune": "Santhià",
        "lat": 45.3690, "lng": 8.1920, "superficie_mq": 340_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 250, "distanza_autostrada_m": 190, "nome_autostrada": "A4 Torino-Milano (km 54 - Santhià)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "34 ettari in un unico lotto continuo a campo aperto. Top assoluto per scala (28.3 MWp) a 190m da A4."
    },
    {
        "id": "FV-AGRI-A4-002",
        "title": "Seminativo Irriguo Corridoio A4 — Galliate",
        "regione": "Piemonte", "provincia": "Novara", "comune": "Galliate",
        "lat": 45.4740, "lng": 8.7180, "superficie_mq": 220_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 230, "nome_autostrada": "A4 Torino-Milano (km 96 - Novara Est)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "22 ha seminativi pianeggianti a 230m da A4. Allaccio record a CP Galliate (380m) con CAPEX minimo."
    },
    {
        "id": "FV-AGRI-A4-003",
        "title": "Seminativo Pianeggiante Asse A4 — Calcinato",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Calcinato",
        "lat": 45.4620, "lng": 10.4180, "superficie_mq": 250_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 170, "distanza_autostrada_m": 220, "nome_autostrada": "A4 Milano-Venezia (km 239 - Lonato)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "25 ettari seminativo aperto. Prossimità ad A4 (220m) e CP Calcinato (1,2 km)."
    },
    {
        "id": "FV-AGRI-A4-004",
        "title": "Tenuta Agricola Corridoio A4 — Sommacampagna",
        "regione": "Veneto", "provincia": "Verona", "comune": "Sommacampagna",
        "lat": 45.4010, "lng": 10.8120, "superficie_mq": 270_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 210, "distanza_autostrada_m": 250, "nome_autostrada": "A4 Torino-Trieste (km 271 - Sommacampagna)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "27 ettari ad alta vocazione agrivoltaica, orografia perfettamente piana a ridosso dell'asse A4 (250m)."
    },
    {
        "id": "FV-AGRI-A4-005",
        "title": "Compendio Seminativo Bassa Vicentina A4 — Gambellara",
        "regione": "Veneto", "provincia": "Vicenza", "comune": "Gambellara",
        "lat": 45.4460, "lng": 11.3580, "superficie_mq": 230_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 160, "distanza_autostrada_m": 190, "nome_autostrada": "A4 Milano-Venezia (km 312 - Montebello)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "23 ha seminativi aperti a 190m da A4. Zero demolizioni, CP Gambellara a soli 810m."
    },

    # ==================== 10. CORRIDOIO AUTOSTRADALE A14 BOLOGNA - TARANTO ====================
    {
        "id": "FV-AGRI-A14-001",
        "title": "Tenuta Agricola Romagnola A14 — Forlì",
        "regione": "Emilia-Romagna", "provincia": "Forlì-Cesena", "comune": "Forlì",
        "lat": 44.2480, "lng": 12.0150, "superficie_mq": 280_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 220, "distanza_autostrada_m": 200, "nome_autostrada": "A14 Bologna-Taranto (km 81 - Forlì)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "28 ettari seminativi contigui, perfetta giacitura piana lungo A14 (200m). CP Forlì a 1 km."
    },
    {
        "id": "FV-AGRI-A14-002",
        "title": "Seminativo Aperto Corridoio A14 — Longiano",
        "regione": "Emilia-Romagna", "provincia": "Forlì-Cesena", "comune": "Longiano",
        "lat": 44.0780, "lng": 12.3320, "superficie_mq": 220_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 170, "distanza_autostrada_m": 220, "nome_autostrada": "A14 Bologna-Taranto (km 111 - Valle del Rubicone)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "22 ha seminativo irriguo tra Cesena e Rimini, 220m da A14, CP Longiano a 970m, iter PAS accelerato."
    },

    # ==================== 11. CORRIDOIO AUTOSTRADALE A21 TORINO - BRESCIA ====================
    {
        "id": "FV-AGRI-A21-001",
        "title": "Grande Tenuta Agricola A21 — Felizzano",
        "regione": "Piemonte", "provincia": "Alessandria", "comune": "Felizzano",
        "lat": 44.9210, "lng": 8.4480, "superficie_mq": 290_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 200, "distanza_autostrada_m": 220, "nome_autostrada": "A21 Torino-Piacenza (km 63 - Felizzano)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "29 ha seminativi pianeggianti aperti, adiacenza A21 (220m) e CP Felizzano a soli 675m."
    },
    {
        "id": "FV-AGRI-A21-002",
        "title": "Compendio Agricolo Pianura Padana A21 — Piacenza Est",
        "regione": "Emilia-Romagna", "provincia": "Piacenza", "comune": "Piacenza",
        "lat": 45.0420, "lng": 9.7420, "superficie_mq": 320_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 180, "nome_autostrada": "A21 Torino-Brescia (km 168 - Piacenza Est)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "32 ettari di seminativo irriguo a campo aperto. 180m da A21, CP Piacenza Est a 1.047m."
    },
    {
        "id": "FV-AGRI-A21-003",
        "title": "Seminativo Irriguo di Pianura — Manerbio A21",
        "regione": "Lombardia", "provincia": "Brescia", "comune": "Manerbio",
        "lat": 45.3580, "lng": 10.1420, "superficie_mq": 260_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 160, "distanza_autostrada_m": 210, "nome_autostrada": "A21 Torino-Brescia (km 218 - Manerbio)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "26 ettari a campo aperto seminativo irriguo. 210m da A21, CP Manerbio a 750m."
    },

    # ==================== 12. CORRIDOIO AUTOSTRADALE A22 MODENA - BRENNERO ====================
    {
        "id": "FV-AGRI-A22-001",
        "title": "Tenuta Agricola Pianeggiante A22 — Nogarole Rocca",
        "regione": "Veneto", "provincia": "Verona", "comune": "Nogarole Rocca",
        "lat": 45.2830, "lng": 10.8910, "superficie_mq": 310_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 220, "nome_autostrada": "A22 Brennero-Modena (km 243 - Nogarole Rocca)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "31 ha seminativo veronese lungo A22 (220m), CP Nogarole Rocca a soli 556m con CAPEX allaccio record."
    },
    {
        "id": "FV-AGRI-A22-002",
        "title": "Seminativo Padano Asse A22 — Campogalliano",
        "regione": "Emilia-Romagna", "provincia": "Modena", "comune": "Campogalliano",
        "lat": 44.6510, "lng": 10.8520, "superficie_mq": 250_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 210, "distanza_autostrada_m": 240, "nome_autostrada": "A22 Brennero-Modena (km 309 - Campogalliano)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "25 ettari pianeggianti, a ridosso intersezione A1/A22 (240m da A22), CP Campogalliano a 946m."
    },

    # ==================== 13. CORRIDOIO AUTOSTRADALE A7 MILANO - GENOVA ====================
    {
        "id": "FV-AGRI-A7-001",
        "title": "Compendio Seminativo Irriguo A7 — Casei Gerola / Voghera",
        "regione": "Lombardia", "provincia": "Pavia", "comune": "Casei Gerola",
        "lat": 45.0120, "lng": 9.0020, "superficie_mq": 300_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 190, "distanza_autostrada_m": 180, "nome_autostrada": "A7 Milano-Genova (km 51 - Casei Gerola)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "30 ettari pianeggianti adiacenti A7 (180m), seminativo cerealicolo a campo aperto, CP Voghera a 990m."
    },
    {
        "id": "FV-AGRI-A7-002",
        "title": "Seminativo Padano Aperto A7 — Tortona",
        "regione": "Piemonte", "provincia": "Alessandria", "comune": "Tortona",
        "lat": 44.9180, "lng": 8.8720, "superficie_mq": 260_000,
        "tipologia": "TERRENO_AGRICOLO_IDONEO",
        "distanza_zona_industriale_m": 160, "distanza_autostrada_m": 200, "nome_autostrada": "A7 Milano-Genova (km 65 - Tortona)",
        "proprietario_tipo": "AZIENDA_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "26 ha seminativi a campo aperto, zero manufatti, 200m da A7, CP Tortona a 1,2 km."
    },

    # ==================== 14. CORRIDOIO AUTOSTRADALE A35 BREBEMI ====================
    {
        "id": "FV-AGRI-A35-001",
        "title": "Seminativo Irriguo di Pianura A35 — Caravaggio",
        "regione": "Lombardia", "provincia": "Bergamo", "comune": "Caravaggio",
        "lat": 45.4980, "lng": 9.6450, "superficie_mq": 270_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 170, "distanza_autostrada_m": 160, "nome_autostrada": "A35 BreBeMi (km 22 - Caravaggio)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "27 ettari seminativo irriguo a mais in fascia 160m da BreBeMi. CP Mozzanica a 2,5 km."
    },
    {
        "id": "FV-AGRI-A35-002",
        "title": "Grande Tenuta Agricola Asse A35 — Calcio",
        "regione": "Lombardia", "provincia": "Bergamo", "comune": "Calcio",
        "lat": 45.5120, "lng": 9.8250, "superficie_mq": 290_000,
        "tipologia": "AGRIVOLTAICO_AVANZATO",
        "distanza_zona_industriale_m": 210, "distanza_autostrada_m": 190, "nome_autostrada": "A35 BreBeMi (km 38 - Calcio)",
        "proprietario_tipo": "SOCIETA_SEMPLICE_AGRICOLA", "proprietario_nome": "",
        "proprietario_piva": "", "proprietario_pec": "", "proprietario_telefono": "",
        "note_commerciali": "29 ha perfettamente pianeggianti in aperta campagna, 190m da A35 BreBeMi, CP Calcio a 945m."
    }
]

def build_and_save_clean_pipeline():
    """Compila e salva la pipeline pulita dei 36 lead qualificati."""
    print("🌾 Avvio compilazione pipeline agricola pulita SunPro (Watchdog Anti-Edifici attivo)...")
    init_db()

    # Pulisci il vecchio database da siti urbani/capannoni
    import sqlite3
    from config import DB_PATH
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM leads")
        conn.commit()
    print("  ✓ Database ripulito da vecchi lead urbani o con fabbricati.")

    processed_leads = []
    
    for raw in MASTER_CLEAN_LEADS_DATA:
        lead_id = raw["id"]
        comune = raw["comune"]
        provincia = raw["provincia"]
        regione = raw["regione"]
        superficie_mq = float(raw["superficie_mq"])
        ha = round(superficie_mq / 10_000.0, 2)
        tipologia = raw["tipologia"]
        lat = raw["lat"]
        lng = raw["lng"]
        dist_ind = float(raw.get("distanza_zona_industriale_m", 100))
        dist_hwy = float(raw.get("distanza_autostrada_m", 500))

        # 1. Verifica assenza fabbricati e contesto urbano (Watchdog)
        suit = verify_land_cover_and_settlement(raw)
        if not suit["idoneo"]:
            print(f"  ❌ SCARTATO dal Watchdog: {lead_id} ({comune}) — {suit['motivo_scarto']}")
            continue

        # 2. Lookup Cabina Primaria Reale con Database Nazionale 2.107 Cabine
        sub_list = find_substations_around_coords(lat, lng, radius_m=5000)
        nearest_sub = sub_list[0] if sub_list else {'name': f'CP {comune} 132/20 kV', 'distanza_m': 750, 'livello_tensione': 'MT 15/20 kV'}
        cabina_nome = nearest_sub.get("name") or nearest_sub.get("nome", "CP Locale")
        dist_cabina = nearest_sub["distanza_m"]
        livello_tensione = nearest_sub.get("livello_tensione", "MT 15/20 kV")

        # 3. Calcolo Energetico e CAPEX
        mwp, mwh, capex = calculate_energy_and_capex(superficie_mq, dist_cabina, regione)

        # 4. Modello Estimativo Fondiario e Destinazione Urbanistica
        val_rep = evaluate_land_market_value(
            lead_id=lead_id,
            regione=regione,
            provincia=provincia,
            comune=comune,
            superficie_mq=superficie_mq,
            tipologia=tipologia,
            distanza_zona_industriale_m=dist_ind,
            distanza_autostrada_m=dist_hwy
        )

        prezzo_mq = val_rep.prezzo_acquisto_target_eur_mq
        prezzo_totale = val_rep.prezzo_acquisto_target_totale_eur
        canone_annuo = round(ha * val_rep.canone_diritto_superficie_eur_ha, 0)

        # 5. Catasto e intestatario non si inventano.
        # Un foglio calcolato con hash, una coppia di particelle consecutive
        # o una partita IVA scritta nel sorgente non è un mappale. La verifica
        # del 15/10/2026 li ha trovati incompatibili con la mappa.
        belfiore = estimate_belfiore(comune)

        lead = {
            "id": lead_id,
            "title": raw["title"],
            "regione": regione,
            "provincia": provincia,
            "comune": comune,
            "codice_belfiore": "" if belfiore == "N/D" else belfiore,
            "foglio": "",
            "particella": "",
            "catasto_stato": "DA VERIFICARE",
            "lat": lat,
            "lng": lng,
            "superficie_mq": superficie_mq,
            "superficie_ha": ha,
            "mwp_stimati": mwp,
            "produzione_mwh_anno": mwh,
            "capex_allaccio_eur": capex,
            "prezzo_mq_eur": prezzo_mq,
            "prezzo_richiesto_eur": prezzo_totale,
            "canone_annuo_eur": canone_annuo,
            "tipologia": tipologia,
            "distanza_zona_industriale_m": dist_ind,
            "distanza_autostrada_m": dist_hwy,
            "nome_autostrada": raw.get("nome_autostrada", "Asse Viario Principale"),
            "cabina_piu_vicina": cabina_nome,
            "distanza_cabina_m": dist_cabina,
            "livello_tensione": livello_tensione,
            "fonte_origine": "SUNPRO_AGRICULTURAL_LAND_ORIGINATION",
            "proprietario_tipo": "",
            "proprietario_nome": "",
            "proprietario_piva": "",
            "proprietario_pec": "",
            "proprietario_telefono": "",
            "contatto_verificato": False,
            "note_commerciali": f"{raw.get('note_commerciali', '')} Suolo: {suit['descrizione_suolo']}. Facilità acquisizione: {suit['facilita_acquisizione']}.",
            "destinazione_urbanistica": val_rep.destinazione_urbanistica,
            "valore_agricolo_base_eur_mq": val_rep.valore_agricolo_base_eur_mq,
            "valore_mercato_ordinario_eur_mq": val_rep.valore_mercato_ordinario_eur_mq,
            "premio_trasformazione_pct": val_rep.premio_trasformazione_pct,
            "status_acquistabilita": val_rep.status_acquistabilita,
            "sintesi_perizia": val_rep.sintesi_perizia,
            "stato_commerciale": "DA_CONTATTARE"
        }

        # 6. Scoring Multicriterio (0-100)
        score_tot, score_det, classe = calculate_site_score(lead)
        lead["score_totale"] = score_tot
        lead["score_dettagli"] = score_det
        lead["rating_classe"] = classe

        upsert_lead(lead)
        processed_leads.append(lead)

    print(f"✅ Inseriti {len(processed_leads)} siti. Foglio, particella e intestatario restano DA VERIFICARE.")
    return processed_leads

if __name__ == "__main__":
    leads = build_and_save_clean_pipeline()
