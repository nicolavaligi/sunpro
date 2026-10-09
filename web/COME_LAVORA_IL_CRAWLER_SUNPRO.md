# ☀️ SunPro Geo-Intelligence 3D — Come Lavora il Crawler
## Documento Ufficiale di Funzionamento, Architettura e Pipeline di Land Origination

> **⚠️ DOCUMENTO PROPRIETARIO & CONFIDENZIALE — PROPRIETÀ INTELLETTUALE DI NICOLA VALIGI**  
> **Autore & Titolare IP:** Nicola Valigi (Houdinick)  
> **Email Ufficiale:** `305862309+nicolavaligi@users.noreply.github.com` | GitHub: [`nicolavaligi`](https://github.com/nicolavaligi)  
> **Piattaforma:** SunPro Geo-Intelligence 3D  
> **URL Live:** [https://nicolavaligi.github.io/sunpro/](https://nicolavaligi.github.io/sunpro/)  
> **Repository Locale:** [`solar-land-acquisition-crawler`](file:///Users/houdinick/solar-land-acquisition-crawler)  
> **Versione Motore:** 2.4 (Aggiornata con Watchdog Anti-Edifici, Gatekeeper Fondiario e Dataset 2.107 Cabine ARERA)  
> **Tutela Legale:** Protetto a norma della L. 633/1941 sul Diritto d'Autore e della Direttiva UE 2009/24/CE. È fatto espresso divieto a terzi di appropriarsi dei contenuti, riprodurre l'architettura o rimuovere la presente nota d'autore.  
> **Data:** Ottobre 2026  

---

## 📑 Sommario Esecutivo

Il crawler **SunPro** è un motore di **Geo-Intelligence algoritmica predittiva** sviluppato da Nicola Valigi per automatizzare ed eliminare il principale collo di bottiglia economico e operativo dello sviluppo fotovoltaico ed agrivoltaico utility-scale in Italia: l'**Origination Fondiaria manuale**.

A differenza dell'approccio convenzionale — basato su mediatori sul campo, cartografia cartacea e mesi di sopralluoghi empirici — SunPro scansiona il territorio nazionale ed esegue un'analisi deterministica a più livelli:
1. **Verifica Idoneità Normativa Ex Lege (D.Lgs. 199/2021 & L. 91/2022):** Intercetta le aree con presunzione legale di idoneità per accesso diretto alla PAS (60–90 giorni) senza veti paesaggistici.
2. **Watchdog del Suolo & Land Cover:** Scarto categorico di capannoni industriali, fabbricati, macerie e tessuti urbani densi, con priorità assoluta ai **terreni agricoli aperti (86,1% della pipeline)**.
3. **Modello Estimativo Fondiario & Gatekeeper Urbanistico:** Calcolo del valore reale su basi VAM/ISMEA/OMI, scarto categorico dei lotti edificabili industriali Zona D (> 15 €/mq), determinazione del prezzo target bancabile (7,50–9,50 €/mq) e del canone per Diritto di Superficie trentennale (3.000 €/ha/anno).
4. **Ingegneria di Rete Elettrica:** Dataset nazionale proprietario di **2.107 Cabine Primarie ARERA/GSE** in locale (lookup < 1 ms), con routing del cavidotto a fattore di tortuosità stradale **1,30x** e calcolo parametrico del CAPEX di allaccio MT.
5. **Simulazione Energetica Scientifica PVGIS v5.2 JRC:** Calcolo della producibilità specifica su modelli della Commissione Europea per strutture a inclinazione fissa vs Tracker monoassiali (+19,2% - +22,0% di resa).
6. **Screening Ambientale No-Go:** Rete Natura 2000 (ZPS/SIC) e rischio idrogeologico PAI (Fascia A).
7. **Scoring Multicriterio 0–100 & Generazione Automatica di Deliverable:** 36 Blind Commercial Teaser PDF Pre-NDA, 36 Dossier Tecnici Integrali PDF, Modello Finanziario CSV e Mappa 3D KML/Web.

---

## 🔄 Il Flusso Operativo del Crawler (Pipeline a 8 Stadi)

```
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 1. DATA HARVESTING & SCANSIONE GEOSPAZIALE                                  │
  │    OpenStreetMap Overpass, Geoportali Regionali, Dati ISTAT, Catasto Open   │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 2. FILTRI GEOMETRICI & IDONEITÀ EX LEGE (D.Lgs. 199/2021)                   │
  │    Superficie >= 2 ha | Buffer Z.I. 350m | Corridoio Autostrada 300m | Cave │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 3. WATCHDOG DEL SUOLO & LAND COVER FILTER                                   │
  │    Scarto capannoni, coperture, borghi densi -> 86,1% Seminativi Aperti     │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 4. GATEKEEPER URBANISTICO & STIMA FONDIARIA COMPARATIVA                     │
  │    Zona D Edificabile (>15 €/mq) -> SCARTATO | Zona E Agricola -> 7,5-9,5 € │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 5. INGEGNERIA DI RETE & ROUTING CABINE ARERA/GSE (2.107 CP)                 │
  │    Lookup <1ms | Routing Cavidotto 1.30x | Stima CAPEX Allaccio MT          │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 6. MODELLAZIONE ENERGETICA SCIENTIFICA (PVGIS v5.2 JRC)                     │
  │    Inclinazione Fissa vs Tracker Monoassiale (+20% resa, Delta EBITDA)      │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 7. ALGORITMO DI SCORING MULTICRITERIO (0–100) & CLASSIFICAZIONE RATING      │
  │    TOP Opportunità (>=75) | Qualificato (60-74) | Non Acquistabile (Zona D) │
  └──────────────────────────────────────┬──────────────────────────────────────┘
                                         │
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │ 8. DELIVERABLE ENGINE & PUBBLICAZIONE                                       │
  │    36 Blind Teaser PDF | 36 Dossier PDF | CSV Finanziario | Web 3D (Pages)  │
  └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Origination Geospaziale & Idoneità Normativa Ex Lege

Il modulo crawler acquisisce le geometrie territoriali e applica filtri geometrici rigorosi basati sul **D.Lgs. 199/2021 (Art. 20)** e sulla **Legge 91/2022**:

### A. Parametri Dimensionali
* **Superficie Minima:** $\ge 2,0\text{ Ettari}$ ($20.000\text{ mq}$).
  * *Razionale tecnico:* Taglia minima per ammortizzare i costi fissi di sviluppo, la cabina MT/AT di consegna e gli oneri di connessione per una taglia minima di $\sim 1,6 – 2,0\text{ MWp}$.
* **Superficie Massima Censita:** Fino a $150\text{ ha}$ ($1.500.000\text{ mq}$) per parchi utility-scale e agrivoltaici su vasta scala.
* **Ratio di Potenza:** Standard parametrico di **$1,2\text{ ettari per ogni }1,0\text{ MWp}$** di potenza DC installata.

### B. Categorie Idonee Presunte Ex Lege
Il motore ricerca geometricamente solo le tipologie che godono di presunzione di idoneità per legge statale:
1. **Fascia Perimetrale Industriale (350 metri):** Aree agricole contigue entro 350 m dal perimetro di zone industriali, artigianali, commerciali o tecnologiche.
2. **Corridoio Infrastrutturale Autostradale (300 metri):** Aree agricole entro 300 m dall'asse di autostrade, raccordi autostradali o tangenziali primarie.
3. **Cave & Bacini Estrattivi Dismessi:** Ambiti estrattivi a cielo aperto esauriti, in post-coltivazione o con obbligo di ripristino morfologico.
4. **Discariche & Siti Contaminati (Brownfield):** Discariche esaurite, chiuse o compendi industriali bonificati.

### C. Iter Autorizzativo PAS Garantito (60–90 Giorni)
I siti intercettati rientrano nella **Procedura Abilitativa Semplificata (PAS)**, escludendo a monte la complessa Procedura Unica (AU) regionale o i veti paesaggistici della Soprintendenza, con una certezza autorizzativa stimata al **95%**.

---

## 2. Watchdog del Suolo & Land Cover Filter (`crawler/land_suitability_filter.py`)

Uno dei rischi critici dell'origination fotovoltaica è localizzare aree industriali occupate da capannoni o fabbricati da demolire. SunPro elimina questo rischio tramite un modulo watchdog a tre livelli:

### A. Esclusione dei Contesti Peri-Urbani Densi
Vengono scartati a monte i territori comunali densamente edificati o metropolitani (*Milano, Sesto San Giovanni, Rho, Legnano, Saronno, Bologna urbana, Torino urbana, Firenze, Napoli, Roma, Genova*).

### B. Disqualificatori Semantici e Morfologici
Qualsiasi censimento contenente attributi relativi a fabbricati stabili viene scartato all'istante:
* *Parole chiave di scarto immediato:* `CAPANNONE`, `FABBRICATO`, `EDIFICIO`, `TETTO`, `COPERTURA`, `DEPOSITO_COPERTO`, `MAGAZZINO`, `RESIDENZIALE`, `CIVILE_ABITAZIONE`, `CORTE_URBANA`, `BORGO`.

### C. Focus Assoluto sui Terreni Agricoli Aperti (86,1% della Pipeline)
Oltre l'**86% dei siti qualificati (31 su 36 lotti)** è costituito da **Terreni Agricoli Puri in Campo Aperto (Zona E) e Agrivoltaico Avanzato**:
* **Zero Costi di Demolizione/Bonifica:** Assenza di macerie, fondazioni o manufatti da abbattere; cantierizzazione immediata con pali infissi nel terreno.
* **Zero Conflitti Territoriali:** Nessuna adiacenza con complessi residenziali.
* **Massima Fattibilità Contrattuale:** Elevata disponibilità dei coltivatori a fronte di un canone che quintuplica la resa agraria ordinaria.

---

## 3. Modello Estimativo Fondiario & Gatekeeper Urbanistico (`crawler/land_valuation.py`)

### ⚠️ Errore Concettuale Evitato
Il motore SunPro **NON stima il valore del terreno basandosi sui MWh prodotti**.  
Calcolare il prezzo del terreno moltiplicando l'energia prodotta produrrebbe una valutazione astratta e circolare fuori mercato. La produzione solare serve solo a valle per stimare EBITDA e IRR.  
Il prezzo del suolo è invece determinato tramite un **Modello Estimativo Sintetico-Comparativo Immobiliare**, ancorato al **mercato fondiario reale e alla destinazione urbanistica (PRG/PGT)**.

### A. Gatekeeper Urbanistico Anti-Inacquistabilità (Zona D)
* **La Trappola dei Lotti Industriali:** I terreni interni a perimetri industriali con destinazione **Zona D (Produttiva/PIP Edificabile)** quotano tra **$50\text{ e }120\text{ €/mq}$**. A questi prezzi l'acquisto costerebbe da 500k € a 1,2M € per ettaro, superando l'intero costo dell'impianto fotovoltaico.
* **Regola del Gatekeeper:** Qualsiasi compendio con quotazione stimata $> 15,00\text{ €/mq}$ o destinazione Zona D viene **CATEGORICAMENTE SCARTATO** e classificato come `NON ACQUISTABILE (SOVRASTIMATO)`.

### B. La Soluzione Chirurgica: Zona E Agricola nel Buffer 350m
SunPro seleziona unicamente i terreni che a livello di PRG/PGT mantengono la destinazione **ZONA E (Agricola Ordinaria)** all'interno della fascia di rispetto dei 350 m:
* **Valore Fondiario Contenuto:** Valutato a prezzi agricoli di base.
* **Procedura PAS Agevolata:** Gode ex lege dell'idoneità statale per contiguità geometrica.

### C. Benchmark Fondiari Provinciali (VAM / ISMEA / OMI 2025–2026)
* **Lombardia (Pianura Irrigua):** $4,80 – 5,60\text{ €/mq}$ ($48k – 56k\text{ €/ha}$) \| Affitto: $550 – 700\text{ €/ha/anno}$.
* **Veneto (Pianura Veneta):** $4,40 – 5,20\text{ €/mq}$ ($44k – 52k\text{ €/ha}$) \| Affitto: $500 – 650\text{ €/ha/anno}$.
* **Emilia-Romagna:** $4,20 – 5,30\text{ €/mq}$ ($42k – 53k\text{ €/ha}$) \| Affitto: $500 – 620\text{ €/ha/anno}$.
* **Piemonte:** $3,20 – 4,50\text{ €/mq}$ ($32k – 45k\text{ €/ha}$) \| Affitto: $450 – 550\text{ €/ha/anno}$.
* **Toscana & Centro:** $2,80 – 3,80\text{ €/mq}$ ($28k – 38k\text{ €/ha}$) \| Affitto: $350 – 450\text{ €/ha/anno}$.
* **Sud & Isole:** $1,80 – 2,80\text{ €/mq}$ ($18k – 28k\text{ €/ha}$) \| Affitto: $300 – 400\text{ €/ha/anno}$.

### D. Formula di Offerta Target e Premio di Trasformazione
1. **Valore Ordinario di Mercato:**  
   $$V_{\text{ordinario}} = V_{\text{agri base}} \times C_{\text{posizionale}}$$  
   *(con $C_{\text{posizionale}}$ maggiorato del $+5\% \div +10\%$ per viabilità primaria e contiguità logistica).*
2. **Prezzo Target di Acquisto:**  
   $$P_{\text{target}} = \text{clamp}(V_{\text{ordinario}} \times 1,60, \; 7,50, \; 9,50)\text{ €/mq}$$  
   Il premio del **$+40\% \div +75\%$** convince il proprietario a firmare il preliminare, mentre per lo sviluppatore incide per appena l'**$8\% – 11\%$ del CAPEX complessivo**.
3. **Canone di Diritto di Superficie (30 Anni):**  
   Standardizzato a **$3.000\text{ €/ha/anno}$** indicizzato ISTAT. A fronte di una resa agraria di $400 – 650\text{ €/ha/anno}$, genera un **Moltiplicatore di Rendita di 4,5x – 6,0x** per l'agricoltore azzerando il CAPEX fondiario per il fondo.

---

## 4. Ingegneria di Rete & Dataset Cabine Primarie (`crawler/substation_finder.py`)

### A. Database Locale Nazionale 2.107 Cabine Primarie ARERA/GSE
* **2.107 Cabine Primarie Nazionali** censite nel database locale [`data/reference/cabine_primarie_italia.json`](file:///Users/houdinick/solar-land-acquisition-crawler/data/reference/cabine_primarie_italia.json).
* Mappatura completa di tutti i distributori: *E-Distribuzione, Unareti, Areti, Ireti, INRETE, Edyna, Set Distribuzione, Deval*.
* Ricerca locale istantanea in **< 1 millisecondo** per qualsiasi coordinata GPS in Italia.

### B. Routing Cavidotto con Coefficiente di Tortuosità 1,30x
La distanza in linea d'aria (*Haversine*) sottostima i costi del 30–40% perché i cavidotti devono seguire strade pubbliche e servitù:
* **Distanza Effettiva Cavidotto:**  
  $$D_{\text{cavidotto}} = D_{\text{haversine}} \times 1,30$$
* **Stima Parametrica CAPEX Allaccio Rete MT:**  
  $$\text{CAPEX}_{\text{allaccio}} = (D_{\text{cavidotto}} \times 65.000\text{ €/km}) + 45.000\text{ € (stallo cella MT in CP)}$$

---

## 5. Simulazione Energetica Scientifica PVGIS JRC (`crawler/pvgis.py`)

Il motore interroga l'algoritmo **PVGIS v5.2 del Joint Research Centre della Commissione Europea**:
* **Configurazione a Inclinazione Fissa (Tilt 28°–34°):**
  * Resa specifica Nord/Centro: $1.250 – 1.450\text{ kWh/kWp/anno}$.
  * CAPEX EPC standard: $680.000\text{ €/MWp}$.
  * OPEX annuo: $14.000\text{ €/MWp/anno}$.
* **Configurazione Tracker Monoassiale (Inseguitori asse N-S con rotazione E-O):**
  * Boost producibilità: **$+19,2\%$ al Nord fino a $+22,0\%$ al Centro/Sud**.
  * Resa specifica con Tracker: $1.520 – 1.760\text{ kWh/kWp/anno}$.
  * CAPEX EPC con Tracker: $750.000\text{ €/MWp}$ ($+70.000\text{ €/MWp}$).
  * OPEX annuo: $16.000\text{ €/MWp/anno}$.
  * **Rientro Finanziario:** Con prezzo energia PPA a **$85\text{ €/MWh}$**, l'extra-gettito ammortizza il maggior costo in **meno di 3,5 anni**, massimizzando l'EBITDA trentennale.

---

## 6. Algoritmo di Scoring Multicriterio (0–100)

Ogni compendio riceve un punteggio deterministico calcolato su **5 pilastri ponderati**:

| Pilastro | Peso | Criteri di Assegnazione Punti |
| :--- | :---: | :--- |
| **1. Idoneità Normativa D.Lgs. 199/21** | **30 pt** | Cave/Discariche: 30 pt \| Buffer 350m Z.I.: 26 pt \| Corridoio 300m Autostrada: 22 pt \| Buffer 500m: 14 pt |
| **2. Prossimità Cabina Primaria ARERA** | **25 pt** | $\le 500\text{ m}$: 25 pt \| $\le 1.000\text{ m}$: 21 pt \| $\le 1.500\text{ m}$: 16 pt \| $\le 2.500\text{ m}$: 11 pt \| $> 3.500\text{ m}$: 2 pt |
| **3. Convenienza & Acquistabilità Fondiaria** | **20 pt** | Prezzo $\le 7,5\text{ €/mq}$: 20 pt \| Target $7,5 – 9,0\text{ €/mq}$: 18 pt \| $9 – 10\text{ €/mq}$: 11 pt \| **Zona D / Prezzo $> 15\text{ €/mq}$: 0 pt (SCARTATO)** |
| **4. Resa Energetica & Taglia Fondiaria** | **15 pt** | Resa PVGIS (fino a 10 pt) + Bonus superficie ($\ge 100\text{k}$: +5 pt, $\ge 50\text{k}$: +4 pt, $\ge 20\text{k}$: +3 pt) |
| **5. Reperibilità della Proprietà** | **10 pt** | PEC + Telefono verificati: 10 pt \| Solo PEC o Telefono: 8 pt \| Persona Giuridica censita: 7 pt \| Particella nota: 4 pt |

### Rating Commerciale:
* 🟢 **TOP OPPORTUNITÀ (Score $\ge 75$):** Priorità assoluta, allaccio a breve raggio, prezzo perfettamente bancabile.
* 🟡 **QUALIFICATO (Score $60 – 74$):** Fattibilità tecnica pienamente approvata.
* 🛑 **NON ACQUISTABILE (SOVRASTIMATO):** Terreni edificabili industriali Zona D, esclusi dal portafoglio.

---

## 7. Deliverable & Pipeline Attiva di SunPro

La pipeline qualificata comprende **36 opportunità reali censite nel Nord e Centro Italia**:
* **Superficie Complessiva:** **651,8 Ettari** (6.518.000 mq).
* **Potenza Stimata:** **543,2 MWp** ($\sim 710\text{ GWh/anno}$).
* **Composizione del Portfolio:** **86,1% Seminativi Agricoli di Pianura (Zona E) & Agrivoltaico**, 11,1% Ex Cave a cielo aperto, 2,8% Discariche ripristinate.
* **Prezzo Medio Target:** **8,42 €/mq** (€ 54.92M pipeline acquisto).

### Asset e Deliverable Generati Automaticamente:
1. **36 Blind Commercial Teaser PDF A4 (Pre-NDA):** Archiviati in [`blind_teasers/`](file:///Users/houdinick/solar-land-acquisition-crawler/blind_teasers). One-pager confidenziali privi di dati particellari per l'outreach verso fondi ed EPC prima della stipula dell'NDA.
2. **36 Dossier Tecnici Integrali PDF A4:** Archiviati in [`dossier_pdf/`](file:///Users/houdinick/solar-land-acquisition-crawler/dossier_pdf). Compendi con dati catastali, proprietari, contatti diretti, schede PVGIS e routing cabina.
3. **Modello Finanziario Comparativo (CSV):** File [`SunPro_Executive_Financial_Model.csv`](file:///Users/houdinick/solar-land-acquisition-crawler/SunPro_Executive_Financial_Model.csv) con comparazione Fissa vs Tracker per ogni lead.
4. **Export 3D per Google Earth Pro (KML):** File [`SunPro_Pipeline_Terreni_Fotovoltaico.kml`](file:///Users/houdinick/solar-land-acquisition-crawler/SunPro_Pipeline_Terreni_Fotovoltaico.kml) per visualizzazione orografica 3D.
5. **Dashboard Web Interattiva (Demo Live):** File [`index.html`](file:///Users/houdinick/solar-land-acquisition-crawler/index.html) pubblicato e consultabile pubblicamente su GitHub Pages: **[https://nicolavaligi.github.io/sunpro/](https://nicolavaligi.github.io/sunpro/)**.

---

## 8. Analisi delle Criticità & Mitigazione Operativa (Gap Analysis)

| Criticità Operativa | Descrizione del Rischio | Mitigazione Implementata nel Crawler SunPro |
| :--- | :--- | :--- |
| **1. Hosting Capacity Cabina** | Cabina primaria fisicamente vicina ma elettricamente satura per congestione di rete MT. | Incrocio periodico con i report trimestrali di saturazione di E-Distribuzione/Terna e penalizzazione score su cabine sature. |
| **2. Risoluzione Catastale Open Data** | Mancanza di visure puntuali per singoli fogli e particelle negli open data regionali. | **Strategia a Imbuto:** i Blind Teaser aprono la trattativa; le visure catastali a pagamento (~0,20–1,00 €) vengono acquistate solo dopo la firma di LOI/NDA. |
| **3. Frammentazione Fondiaria** | Appezzamenti > 10 ha frazionati tra decine di eredi con rischio di stallo decisionale. | Punteggio preferenziale per Persone Giuridiche (Aziende Agricole, Società Semplici, curatele) con interlocutore unico. |
| **4. Morfologia di Dettaglio** | Micro-pendenze a Nord o avvallamenti orografici con costi di sbancamento imprevisti. | Screening orografico preliminare con DEM SRTM/Copernicus 25m e verifica visiva 3D Google Earth. |
| **5. Decreti Regionali Attuativi** | Regioni che introducono buffer aggiuntivi rispetto a beni culturali. | Focus prioritario su aree brownfield e buffer 350m Z.I., blindati per legge statale primaria. |

---

### ⚖️ Note Legali & Tutela della Proprietà Intellettuale
* **Titolare Esclusivo dei Diritti d'Autore:** Nicola Valigi (Houdinick)
* **Email Ufficiale:** `305862309+nicolavaligi@users.noreply.github.com`
* **Licenza:** Proprietaria e Confidenziale.
* **Clausola di Tutela:** Il presente documento, i dati analitici, il modello estimativo zonale e le formule parametriche costituiscono opera dell'ingegno di Nicola Valigi protetta ai sensi della Legge 633/1941. Qualsiasi utilizzo non autorizzato, riproduzione anche parziale, cessione o appropriazione da parte di terzi è vietata ed è perseguibile civilmente e penalmente.

*Documento tecnico ufficiale redatto per SunPro Geo-Intelligence 3D.*  
*Copyright © 2026 Nicola Valigi (Houdinick). Tutti i diritti riservati.*
