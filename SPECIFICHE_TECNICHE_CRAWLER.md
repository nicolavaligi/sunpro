# ☀️ Specifiche Tecniche del Crawler & Motore di Land Origination SunPro
## Architettura Geospaziale, Watchdog del Suolo, Modello Estimativo Fondiario e Routing Elettrico

> **⚠️ DOCUMENTO PROPRIETARIO & CONFIDENZIALE — PROPRIETÀ INTELLETTUALE DI NICOLA VALIGI**  
> **Oggetto:** Origination geospaziale, qualificazione urbanistica, perizia estimativa e calcolo infrastrutturale per impianti Fotovoltaici & Agrivoltaici Utility-Scale in Italia.  
> **Piattaforma:** SunPro Geo-Intelligence 3D  
> **Autore & Titolare Esclusivo IP:** Nicola Valigi (Houdinick)  
> **Email Ufficiale:** `305862309+nicolavaligi@users.noreply.github.com` | GitHub: [`nicolavaligi`](https://github.com/nicolavaligi)  
> **Versione:** 2.4 (Aggiornata con i moduli Watchdog Suolo & Land Valuation — Ottobre 2026)  
> **Tutela Legale:** Protetto ai sensi della Legge 633/1941 e Direttiva UE 2009/24/CE. Vietata la riproduzione o l'appropriazione senza licenza scritta.  
> **Live Demo:** [https://nicolavaligi.github.io/sunpro/](https://nicolavaligi.github.io/sunpro/)  
> **Repository Locale:** [`solar-land-acquisition-crawler`](file:///Users/houdinick/solar-land-acquisition-crawler)  

---

## 📑 Indice delle Specifiche
1. [Visione & Paradigma Industriale del Motore](#1-visione--paradigma-industriale)
2. [Filtri di Ricerca Geospaziale & Idoneità Normativa Ex Lege](#2-filtri-di-ricerca-geospaziale--idoneità-normativa)
3. [Watchdog del Suolo & Land Cover Filter (Priorità Terreni Agricoli 86%)](#3-watchdog-del-suolo--land-cover-filter)
4. [Modello Estimativo Fondiario & Gatekeeper Urbanistico Anti-Inacquistabilità](#4-modello-estimativo-fondiario--gatekeeper-urbanistico)
5. [Ingegneria di Rete & Dataset Nazionale 2.107 Cabine Primarie ARERA/GSE](#5-ingegneria-di-rete--dataset-cabine-primarie)
6. [Simulazione Energetica Indipendente PVGIS v5.2 JRC (Fisso vs Tracker)](#6-simulazione-energetica-pvgis-jrc)
7. [Algoritmo di Scoring Multicriterio (0–100) & Classi di Rating](#7-algoritmo-di-scoring-multicriterio)
8. [Pipeline Dati, Deliverable & Formati di Esportazione](#8-pipeline-dati--deliverable)
9. [Roadmap Evolutiva del Motore](#9-roadmap-evolutiva)

---

## 1. Visione & Paradigma Industriale

Il settore del fotovoltaico utility-scale in Italia soffre storicamente di un grave collo di bottiglia operativo: l'**Origination fondiaria manuale**.  
Gli sviluppatori tradizionali impiegano mesi per individuare terreni tramite sopralluoghi sul campo, agronomi e mediatori, incorrendo frequentemente in due trappole fatali:
1. **La trappola dei fabbricati/capannoni:** Selezione di aree che contengono capannoni industriali dismessi o fabbricati con oneri insostenibili di demolizione, rimozione macerie e bonifica amianto.
2. **La trappola dei terreni edificabili Zona D:** Selezione di lotti industriali (PIP) aventi quotazioni di mercato comprese tra **$50\text{ e }120\text{ €/mq}$**, totalmente incompatibili con l'economia di scala di un impianto fotovoltaico a terra.

Il motore **SunPro** risolve questi limiti attraverso un approccio analitico e deterministico, garantendo la convergenza di **tre requisiti inviolabili**:
* **Idoneità Normativa Certa (D.Lgs. 199/2021 & L. 91/2022):** Presunzione di idoneità per legge che garantisce l'iter autorizzativo **PAS (60–90 giorni)** escludendo veti paesaggistici.
* **Assenza di Manufatti (100% Campo Aperto):** Zero costi di demolizione o bonifica; suolo pianeggiante immediatamente cantierabile.
* **Prezzo Fondiario Bancabile (Zona E Agricola):** Costo di acquisizione target a **$7,50 – 9,50\text{ €/mq}$** (o canone di superficie a **$3.000\text{ €/ha/anno}$**), assicurando un IRR di progetto a due cifre.

---

## 2. Filtri di Ricerca Geospaziale & Idoneità Normativa

Il crawler interroga basi dati cartografiche (OpenStreetMap, Geoportali Regionali, Agenzia delle Entrate, ISTAT) filtrando il territorio secondo vincoli geometrici rigorosi:

### A. Dimensione Fondiaria
* **Superficie Minima:** $\ge 2,0\text{ ha}$ ($20.000\text{ mq}$).  
  *Razionale:* Taglia minima per ammortizzare i costi fissi di sviluppo, la cabina MT/AT di consegna e le opere di connessione per una taglia minima di $\sim 1,6 – 2,0\text{ MWp}$.
* **Superficie Massima:** Fino a $150\text{ ha}$ ($1.500.000\text{ mq}$) per impianti utility-scale e agrivoltaici su vasta scala.
* **Rapporto di Densità:** Standard di dimensionamento pari a **$1,2\text{ ettari per ogni }1,0\text{ MWp}$** di potenza DC installata.

### B. Categorie Territoriali Idonee Ex Lege (Art. 20 D.Lgs. 199/2021)
Il motore acquisisce unicamente particelle e compendi ricadenti nelle seguenti classi:
1. **Fascia Perimetrale Industriale (350 metri):** Aree agricole contigue entro un raggio di 350 m dal perimetro di zone industriali, artigianali, commerciali o tecnologiche.
2. **Corridoio Infrastrutturale Autostradale (300 metri):** Aree agricole entro 300 m dall'asse di autostrade, raccordi autostradali o tangenziali primarie.
3. **Cave & Bacini Estrattivi Dismessi:** Ambiti estrattivi a cielo aperto esauriti, in post-coltivazione o con obbligo di ripristino morfologico.
4. **Discariche & Siti Contaminati (Brownfield):** Discariche esaurite, chiuse o compendi bonificati.

### C. Watchdog Vincoli Ambientali & Idrogeologici (Screening No-Go)
Il motore esclude a monte qualsiasi compendio intersecato da:
* **Rete Natura 2000:** Zero sovrapposizioni con Zone di Protezione Speciale (ZPS) o Zone Speciali di Conservazione (ZSC/SIC).
* **Piano di Assetto Idrogeologico (PAI):** Esclusione totale delle aree in Fascia Fluviale A (rischio esondazione frequente / flusso di piena).
* **Esito Autorizzativo:** Confermato iter in **PAS (Procedura Abilitativa Semplificata)** con esito positivo stimato al **95%**.

---

## 3. Watchdog del Suolo & Land Cover Filter (Priorità Terreni Agricoli 86%)

Implementato nel modulo [`crawler/land_suitability_filter.py`](file:///Users/houdinick/solar-land-acquisition-crawler/crawler/land_suitability_filter.py), il watchdog del suolo implementa le seguenti regole operative:

### A. Esclusione dei Contesti Peri-Urbani Densi
Sono esclusi categoricamente dal crawler i territori comunali densamente edificati o metropolitani (es. Milano, Sesto San Giovanni, Rho, Legnano, Saronno, Bologna urbana, Torino urbana, Firenze) in cui le zone produttive ospitano capannoni contigui a tessuti residenziali densi.

### B. Disqualificatori Semantici e Morfologici
Qualsiasi censimento contenente attributi relativi a fabbricati stabili viene scartato:
* *Parole chiave di scarto immediato:* `CAPANNONE`, `FABBRICATO`, `EDIFICIO`, `TETTO`, `COPERTURA`, `DEPOSITO_COPERTO`, `MAGAZZINO`, `RESIDENZIALE`, `CIVILE_ABITAZIONE`, `CORTE_URBANA`, `BORGO`.

### C. Svolta di Portfolio: Terreni Agricoli Aperti (86,1% della Pipeline)
Oltre l'**86% dei siti qualificati (31 su 36 lotti)** è costituito da **Terreni Agricoli Puri in Campo Aperto (Zona E) e Agrivoltaico Avanzato**:
* **Zero Costi di Demolizione/Bonifica:** Assenza di macerie, fondazioni o manufatti da abbattere; cantierizzazione immediata con pali infissi nel terreno.
* **Zero Conflitti Territoriali:** Nessuna adiacenza con abitazioni civili, eliminando il rischio di comitati locali o ricorsi al TAR.
* **Semplicità Contrattuale & Elevata Redditività per il Coltivatore:**  
  * La resa agraria ordinaria di seminativo irriguo al Nord/Centro genera tra **$400\text{ e }650\text{ €/ha/anno}$**.
  * Il canone offerto da SunPro per Diritto di Superficie trentennale a **$3.000\text{ €/ha/anno}$** moltiplica la rendita fondiaria di **$4,5\text{x} \div 6,0\text{x}$**, rendendo l'opzione contrattuale straordinariamente attrattiva per l'agricoltore.

---

## 4. Modello Estimativo Fondiario & Gatekeeper Urbanistico

Implementato nel modulo [`crawler/land_valuation.py`](file:///Users/houdinick/solar-land-acquisition-crawler/crawler/land_valuation.py), questo modello elimina l'errore concettuale di stimare il valore del terreno basandosi sulla produzione elettrica.

```
                   ┌─────────────────────────────────────────────────────────────┐
                   │    SCANSIONE GEOSPAZIALE & CENSIMENTO DEL TERRENO           │
                   └──────────────────────────────┬──────────────────────────────┘
                                                  │
                                                  ▼
                   ┌─────────────────────────────────────────────────────────────┐
                   │           VERIFICA DESTINAZIONE URBANISTICA (PRG/PGT)       │
                   └──────────────────────────────┬──────────────────────────────┘
                                                  │
                     ┌────────────────────────────┴───────────────────────────┐
                     ▼                                                        ▼
         [ ZONA D EDIFICABILE ]                                   [ ZONA E AGRICOLA CONTIGUA ]
        (Lotto industriale / PIP)                                 (Entro buffer 350m Z.I. / 300m Autostrada)
                     │                                                        │
         Valore di Mercato: 50–120 €/mq                           Valore Agricolo VAM/ISMEA: 2,50–5,50 €/mq
                     │                                                        │
                     ▼                                                        ▼
       🛑 GATEKEEPER SUNPRO:                                    Coeff. Posizionali (Viabilità, Orografia)
      "NON ACQUISTABILE — SCARTATO"                                           │
   (Incompatibile con FV ground-mounted)                                      ▼
                                                                  Valore di Mercato Ordinario: 3,00–5,80 €/mq
                                                                              │
                                                                              ▼
                                                                Premio Trasformazione Energetica (+50% / +75%)
                                                                              │
                                                                              ▼
                                                                  🟢 OFFERTA TARGET BANCABILE:
                                                                  Acquisto: 7,50 – 9,50 €/mq
                                                                  Diritto Superficie: 3.000 €/ha/anno (4x-6x affitto)
```

### A. Gatekeeper Urbanistico Anti-Inacquistabilità (Zona D)
* Terreni ricadenti all'interno di perimetri industriali con destinazione **Zona D (Produttiva/Artigianale Edificabile)** hanno valori compresi tra **$50,00\text{ e oltre }120,00\text{ €/mq}$**.
* A questi valori l'acquisto del suolo costerebbe da $500.000\text{ €}$ a oltre $1.000.000\text{ €}$ ad ettaro, rendendo il progetto fallimentare a monte.
* **Regola del Gatekeeper:** Qualsiasi compendio con quotazione stimata $> 15,00\text{ €/mq}$ viene **SCARTATO AUTOMATICAMENTE** e classificato come `NON ACQUISTABILE (SOVRASTIMATO)`.

### B. La Soluzione Chirurgica: Zona E Agricola nel Buffer 350m
SunPro isola unicamente i terreni con destinazione urbanistica **ZONA E (Agricola Ordinaria)** situati nella fascia perimetrale di rispetto:
* Il fondo mantiene il valore fondiario agricolo contenuto (valutazione equa per lo sviluppatore).
* Il fondo gode ex lege dell'idoneità e della corsia PAS per effetto della contiguità geometrica al comparto produttivo.

### C. Benchmark Ufficiali VAM / ISMEA / OMI (2025–2026)
Il valore agricolo di base ($V_{\text{agri}}$) adotta quotazioni tabellari provinciali per seminativo irriguo/asciutto di pianura:
* **Lombardia (Cremona, Brescia, Lodi, Pavia, Mantova):** $4,80 – 5,60\text{ €/mq}$ ($48\text{k} – 56\text{k €/ha}$) \| Affitto medio: $550 – 700\text{ €/ha/anno}$.
* **Veneto (Verona, Padova, Vicenza, Rovigo):** $4,40 – 5,20\text{ €/mq}$ ($44\text{k} – 52\text{k €/ha}$) \| Affitto medio: $500 – 650\text{ €/ha/anno}$.
* **Emilia-Romagna (Bologna, Modena, Parma, Piacenza):** $4,20 – 5,30\text{ €/mq}$ ($42\text{k} – 53\text{k €/ha}$) \| Affitto medio: $500 – 620\text{ €/ha/anno}$.
* **Piemonte (Alessandria, Cuneo, Novara, Vercelli):** $3,20 – 4,50\text{ €/mq}$ ($32\text{k} – 45\text{k €/ha}$) \| Affitto medio: $450 – 550\text{ €/ha/anno}$.
* **Toscana & Centro (Grosseto, Arezzo, Perugia, Ancona):** $2,80 – 3,80\text{ €/mq}$ ($28\text{k} – 38\text{k €/ha}$) \| Affitto medio: $350 – 450\text{ €/ha/anno}$.
* **Sud & Isole (Puglia, Sicilia):** $1,80 – 2,80\text{ €/mq}$ ($18\text{k} – 28\text{k €/ha}$) \| Affitto medio: $300 – 400\text{ €/ha/anno}$.

### D. Formula di Offerta Target e Premio di Trasformazione
1. **Valore Ordinario di Mercato:**  
   $$V_{\text{ordinario}} = V_{\text{agri base}} \times C_{\text{posizionale}}$$  
   *(con $C_{\text{posizionale}}$ incrementato del $+5\% \div +10\%$ per viabilità primaria e contiguità logistica).*
2. **Prezzo Target di Acquisto:**  
   $$P_{\text{target}} = \text{clamp}(V_{\text{ordinario}} \times 1,60, \; 7,50, \; 9,50)\text{ €/mq}$$  
   Il premio del **$+40\% \div +75\%$** sul valore agricolo ordinario costituisce la leva economica che convince il proprietario a sottoscrivere il preliminare.
3. **Canone di Diritto di Superficie (30 Anni):**  
   Target standardizzato a **$3.000\text{ €/ha/anno}$** indicizzato ISTAT, azzerando il CAPEX fondiario per gli sviluppatori.

---

## 5. Ingegneria di Rete & Dataset Cabine Primarie

Implementato nel modulo [`crawler/substation_finder.py`](file:///Users/houdinick/solar-land-acquisition-crawler/crawler/substation_finder.py):

### A. Database Locale Nazionale ARERA/GSE
* **2.107 Cabine Primarie Nazionali** censite nel database locale [`data/reference/cabine_primarie_italia.json`](file:///Users/houdinick/solar-land-acquisition-crawler/data/reference/cabine_primarie_italia.json).
* Ricerca locale su albero spaziale con lookup **sub-millisecondo (< 1ms)** senza dipendenza da chiamate API esterne.
* Identificazione del codice impianto ufficiale, gestore (E-Distribuzione, Unareti, Ireti, Edyna, Acea, Deval), e livello di tensione (132/15 kV, 132/20 kV, etc.).

### B. Routing Cavidotto con Coefficiente di Tortuosità 1,30x
La distanza geometrica in linea d'aria (*Haversine*) è tipicamente irrealistica perché i cavidotti interrati devono seguire la viabilità pubblica e i fossi stradali:
* **Formula Distanza Effettiva Cavidotto:**  
  $$D_{\text{cavidotto}} = D_{\text{haversine}} \times 1,30$$
* **Stima Parametrica CAPEX Allaccio MT:**  
  $$\text{CAPEX}_{\text{connessione}} = (D_{\text{cavidotto}} \times 65.000\text{ €/km}) + 45.000\text{ € (stallo cella MT in CP)}$$

---

## 6. Simulazione Energetica PVGIS JRC (Fisso vs Tracker)

Il motore esegue la modellazione solare indipendente interrogando l'algoritmo **PVGIS v5.2 del Joint Research Centre della Commissione Europea**:

### A. Configurazione a Inclinazione Fissa (Tilt 28°–34°)
* Producibilità specifica Nord/Centro: **$1.250 – 1.450\text{ kWh/kWp/anno}$**.
* CAPEX EPC standard: **$680.000\text{ €/MWp}$**.
* OPEX annuo: **$14.000\text{ €/MWp/anno}$**.

### B. Configurazione Tracker Monoassiale (Inseguitori Asse N-S con rotazione E-O)
* Incremento di resa verificato: **$+19,2\%$ al Nord fino a $+22,0\%$ al Centro/Sud**.
* Producibilità specifica con Tracker: **$1.520 – 1.760\text{ kWh/kWp/anno}$**.
* CAPEX EPC con Tracker: **$750.000\text{ €/MWp}$** ($+70.000\text{ €/MWp}$ per componentistica elettromeccanica).
* OPEX annuo: **$16.000\text{ €/MWp/anno}$**.
* **Analisi di Rientro Finanziario:** Con prezzo di vendita energia a **$85\text{ €/MWh}$**, l'extra-gettito energetico generato dai tracker ammortizza il maggior CAPEX in **meno di 3,5 anni**, incrementando sensibilmente l'EBITDA trentennale del parco.

---

## 7. Algoritmo di Scoring Multicriterio (0–100)

Ogni compendio analizzato riceve un punteggio deterministico calcolato su **5 pilastri pesati**:

| Pilastro | Peso | Criteri Dettagliati di Assegnazione Punti |
| :--- | :---: | :--- |
| **1. Idoneità Normativa D.Lgs. 199/21** | **30 pt** | Cave/Discariche: 30 pt \| Entro 350m Z.I.: 26 pt \| Entro 300m Autostrada: 22 pt \| Buffer 500m: 14 pt \| Altro: 6 pt |
| **2. Prossimità Cabina Primaria ARERA** | **25 pt** | $\le 500\text{ m}$: 25 pt \| $\le 1.000\text{ m}$: 21 pt \| $\le 1.500\text{ m}$: 16 pt \| $\le 2.500\text{ m}$: 11 pt \| $> 3.500\text{ m}$: 2 pt |
| **3. Convenienza & Acquistabilità Fondiaria** | **20 pt** | Prezzo $\le 7,5\text{ €/mq}$: 20 pt \| Nel target $7,5 – 9,0\text{ €/mq}$: 18 pt \| $9 – 10\text{ €/mq}$: 11 pt \| $> 12\text{ €/mq}$: 1 pt \| **Zona D / Prezzo $> 15\text{ €/mq}$: 0 pt (SCARTATO)** |
| **4. Resa Energetica & Taglia Fondiaria** | **15 pt** | Resa PVGIS (fino a 10 pt) + Taglia mq ($\ge 100\text{k}$: +5 pt, $\ge 50\text{k}$: +4 pt, $\ge 20\text{k}$: +3 pt) |
| **5. Reperibilità della Proprietà** | **10 pt** | PEC + Telefono verificati: 10 pt \| Solo PEC o Telefono: 8 pt \| Persona Giuridica censita: 7 pt \| Particella nota: 4 pt |

### Classificazione Rating Commerciale:
* 🟢 **TOP OPPORTUNITÀ (Score $\ge 75$):** Priorità assoluta, allaccio a breve raggio, prezzo perfettamente in target bancabile.
* 🟡 **QUALIFICATO (Score $60 – 74$):** Sito idoneo con fattibilità tecnica pienamente approvata.
* 🛑 **NON ACQUISTABILE (SOVRASTIMATO):** Terreni edificabili industriali Zona D, esclusi dal portafoglio.

---

## 8. Pipeline Dati, Deliverable & Formati di Esportazione

La pipeline attiva comprende **36 lotti reali censiti nel Nord e Centro Italia**:
* **Superficie Totale:** **651,8 Ettari** (6.518.000 mq).
* **Potenza Complessiva Stimata:** **543,2 MWp** ($\sim 710\text{ GWh/anno}$).
* **Prezzo Medio Target:** **8,42 €/mq** (€ 54.92M pipeline acquisto).
* **Composizione del Portfolio:** **86,1% Seminativi Agricoli di Pianura (Zona E) & Agrivoltaico**, 11,1% Ex Cave a cielo aperto, 2,8% Discariche ripristinate.

### Deliverable Generati Automaticamente dal Sistema:
1. **36 Blind Commercial Teaser PDF A4 (Pre-NDA):**  
   Archiviati in [`blind_teasers/`](file:///Users/houdinick/solar-land-acquisition-crawler/blind_teasers). Documenti sintetici ad uso commerciale privi di dati anagrafici e particellari, concepiti per la presentazione a fondi ed EPC prima della stipula dell'NDA.
2. **36 Dossier Tecnici Integrali PDF A4:**  
   Archiviati in [`dossier_pdf/`](file:///Users/houdinick/solar-land-acquisition-crawler/dossier_pdf). Compendi esaustivi comprensivi di dati catastali, proprietari, contatti diretti, schede PVGIS e routing cavidotto.
3. **Modello Finanziario Comparativo (CSV):**  
   File [`SunPro_Executive_Financial_Model.csv`](file:///Users/houdinick/solar-land-acquisition-crawler/SunPro_Executive_Financial_Model.csv) contenente la comparazione completa tra configurazione Fissa e Tracker per ciascun lead.
4. **Export 3D per Google Earth Pro (KML):**  
   File [`SunPro_Pipeline_Terreni_Fotovoltaico.kml`](file:///Users/houdinick/solar-land-acquisition-crawler/SunPro_Pipeline_Terreni_Fotovoltaico.kml) con perimetri, quote e vettori di allaccio per sopralluoghi virtuali 3D.
5. **Dashboard Web Interattiva (Demo Live):**  
   File [`index.html`](file:///Users/houdinick/solar-land-acquisition-crawler/index.html) pubblicato e consultabile pubblicamente su GitHub Pages all'indirizzo [https://nicolavaligi.github.io/sunpro/](https://nicolavaligi.github.io/sunpro/).

---

## 9. Roadmap Evolutiva del Motore

1. **Espansione Territoriale Scalabile:**  
   Estensione della scansione a costo zero sulle regioni ad elevata insolazione (Veneto, Piemonte, Toscana, Puglia, Basilicata) sfruttando il DB nazionale delle 2.107 Cabine Primarie già operativo.
2. **Layer di Hosting Capacity (Saturazione Virtuale Rete):**  
   Integrazione con le pubblicazioni trimestrali di E-Distribuzione e Terna per penalizzare nello scoring i nodi di rete con saturazione virtuale conclamata.
3. **Piattaforma Web & Download Teaser 1-Click:**  
   Aggiunta del link diretto al download del Blind Teaser PDF da ciascuna scheda interattiva nella demo online.

---

### ⚖️ Note Legali & Proprietà Intellettuale
* **Titolare dei Diritti:** Nicola Valigi (`Houdinick`)
* **Email:** `305862309+nicolavaligi@users.noreply.github.com`
* **Licenza:** Proprietaria e Confidenziale (Tutti i diritti riservati).
* **Avviso:** La presente specifica tecnica e la formulazione matematica dei parametri del crawler costituiscono opera dell'ingegno tutelata ex L. 633/1941. Vietata ogni forma di riproduzione o sfruttamento commerciale non autorizzato.

*Documento ufficiale di specifiche di progetto redatto per SunPro Geo-Intelligence 3D.*  
*Copyright © 2026 Nicola Valigi (Houdinick). Tutti i diritti riservati.*
