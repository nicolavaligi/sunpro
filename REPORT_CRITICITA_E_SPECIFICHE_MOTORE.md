# ☀️ SunPro Engine — Documento Tecnico-Esecutivo
## Specifiche di Ricerca, Architettura del Motore e Report delle Criticità

> **Documento ad uso interno per Soci, Sviluppatori e Partner Strategici**  
> **Oggetto:** Origination geospaziale, qualificazione normativa e modello finanziario per terreni Fotovoltaici & Agrivoltaici Utility-Scale in Italia.  
> **Piattaforma:** SunPro Geo-Intelligence 3D  
> **Autore & Proprietà Intellettuale:** Nicola Valigi (Houdinick)  
> **Data:** Ottobre 2026  

---

## 📑 Indice del Documento
1. [Sintesi Esecutiva: Cosa fa il Motore SunPro](#1-sintesi-esecutiva)
2. [Specifiche Tecniche di Ricerca & Filtri Applicati](#2-specifiche-tecniche-di-ricerca)
3. [Ingegneria di Rete & Resa Energetica Scientifica](#3-ingegneria-di-rete--resa-energetica)
4. [Algoritmo di Scoring Multicriterio (0–100)](#4-algoritmo-di-scoring-multicriterio)
5. [Modello Finanziario & Parametri di Redditività](#5-modello-finanziario--parametri-di-redditività)
6. [Report delle Criticità & Analisi dei Rischi (Gap Analysis)](#6-report-delle-criticità--analisi-dei-rischi)
7. [Roadmap di Scalabilità & Consigli per i Soci](#7-roadmap-di-scalabilità--consigli-per-i-soci)

---

## 1. Sintesi Esecutiva

Il motore **SunPro** è una piattaforma di **Geo-Intelligence predittiva** progettata per automatizzare il lavoro più costoso, lento e rischioso dello sviluppo fotovoltaico: l'**Origination fondiaria**.

Invece di mandare tecnici sul territorio o consultare manualmente mappe catastali, il motore scansiona il territorio italiano e incrocia simultaneamente:
1. **La conformità normativa ex lege** (D.Lgs. 199/2021).
2. **La prossimità infrastrutturale alla rete elettrica** (Media e Alta Tensione).
3. **La resa solare scientifica** della Commissione Europea (PVGIS v5.2 JRC).
4. **I vincoli ambientali ostativi** (Rete Natura 2000 e Rischio Idrogeologico PAI).
5. **Il modello economico-finanziario** (Acquisto vs Diritto di Superficie 30ennale).

Il risultato finale è una pipeline di terreni già **pre-qualificati, quotati finanziariamente e pronti per l'iter autorizzativo accelerato (PAS in 60–90 giorni)**.

---

## 2. Specifiche Tecniche di Ricerca

Il crawler scarta a monte il 98% del territorio agricolo ordinario e isola esclusivamente le aree che presentano i requisiti di fattibilità tecnica e normativa:

### A. Dimensione Fondiaria
* **Superficie Minima:** **$\ge 2,0$ Ettari (20.000 mq)**.  
  *Razionale:* 2 ha è la soglia minima per giustificare i costi fissi di sviluppo, la cabina MT/AT e gli oneri autorizzativi di un impianto utility-scale (~1,6 – 2,0 MWp).
* **Superficie Massima Censita:** Fino a **150 Ettari (1.500.000 mq)** per parchi fotovoltaici ed agrivoltaici su larga scala.
* **Rapporto di Densità:** Standard di mercato di **1,2 ettari per ogni 1,0 MWp** di potenza installata (compatibile sia con strutture a terra fisse che con inseguitori monoassiali).

### B. Idoneità Normativa Ex Lege (D.Lgs. 199/2021, Art. 20)
Il motore ricerca geometricamente solo le tipologie che godono di presunzione di idoneità per legge:
1. **Fascia Industriale:** Aree situate entro **350 metri** dal perimetro di zone industriali, artigianali o commerciali.
2. **Corridoio Autostradale:** Aree situate entro **300 metri** dagli assi autostradali, raccordi o tangenziali primarie.
3. **Cave e Bacini Estrattivi:** Ex cave dismesse, cave in fase di ripristino o bacini chiusi.
4. **Discariche & Siti Bonificati:** Discariche esaurite o brownfield industriali ripristinati.

*Vantaggio strategico:* Su queste aree l'autorizzazione è per legge agevolata, riducendo drasticamente il rischio di blocco paesaggistico della Soprintendenza.

### C. Watchdog Vincoli Ambientali & Idrogeologici (Screening No-Go)
Prima di promuovere un'area, il motore verifica l'assenza di interferenze bloccanti:
* **Rete Natura 2000:** Verifica l'assenza di sovrapposizioni con Zone di Protezione Speciale (ZPS) o Siti di Importanza Comunitaria (SIC/ZSC), evitando costose Valutazioni di Incidenza (VInCA).
* **Idrogeologia PAI:** Verifica che l'area sia esterna alle Fasce Fluviali A (esondazione frequente / flusso di piena), garantendo l'assicurabilità dell'impianto.
* **Procedura Presunta:** Se l'area è idonea ex lege e libera da vincoli ostativi, viene classificata per l'iter **PAS (Procedura Abilitativa Semplificata, 60–90 giorni)** con certezza autorizzativa stimata al **95%**.

---

## 3. Ingegneria di Rete & Resa Energetica Scientifica

### A. Database Nazionale 2.107 Cabine Primarie (ARERA / GSE)
Il motore integra in locale l'intero dataset ufficiale italiano delle **2.107 Cabine Primarie** di tutti i distributori nazionali:
* **Operatori Mappati:** *E-Distribuzione, Unareti (A2A), Areti (Acea), Ireti, INRETE (Hera), V-Reti, Edyna, Set Distribuzione, Deval* e cooperative locali.
* **Lookup Istantaneo:** Calcolo delle distanze in **1 millisecondo** per qualsiasi punto GPS in Italia.

### B. Fattore di Tortuosità Stradale Cavidotto (1,30x)
* **Limite delle soluzioni concorrenti:** Calcolano la distanza in linea d'aria euclidea, sottostimando i costi di allaccio del 30–40%.
* **Soluzione SunPro:** Applica un coefficiente geometrico infrastrutturale di **1,30x** lungo la viabilità pubblica e le servitù di passaggio obbligate.
* **Parametri CAPEX Allaccio Rete MT:**
  $$\text{CAPEX Allaccio} = (\text{Distanza Stradale in km} \times 65.000\text{ €/km}) + 45.000\text{ € (Stallo Cabina Primaria)}$$

### C. Resa Solare Scientifica PVGIS JRC (Strutture Fisse vs Tracker Monoassiale)
Il motore interroga l'algoritmo scientifico **PVGIS v5.2 del Joint Research Centre della Commissione Europea**:
* **Configurazione a Inclinazione Fissa:** Calcola il tilt ottimale (28°–34°) e la produzione specifica ($1.250 – 1.450\text{ kWh/kWp/anno}$ al Nord/Centro).
* **Configurazione Tracker Monoassiale (Inseguitori asse N-S con rotazione Est-Ovest):**
  * Modella l'incremento di producibilità tipico del mercato utility-scale: **$+19,2\%$ al Nord fino a $+22,0\%$ al Centro/Sud**.
  * Consente di comparare immediatamente il maggior costo dei tracker con l'extra-ricavo energetico annuo.

---

## 4. Algoritmo di Scoring Multicriterio (0–100)

Ogni terreno analizzato riceve un punteggio deterministico ponderato su **5 pilastri chiave**:

| Pilastro | Peso Max | Criteri di Assegnazione Punti |
| :--- | :---: | :--- |
| **1. Idoneità Normativa D.Lgs. 199/21** | **30 pt** | Cave/Discariche: 30 pt \| Entro 350m Z.I.: 26 pt \| Entro 300m Autostrada: 22 pt \| Buffer 500m: 14 pt \| Altro: 6 pt |
| **2. Prossimità Cabina Primaria** | **25 pt** | $\le 500\text{ m}$: 25 pt \| $\le 1.000\text{ m}$: 21 pt \| $\le 1.500\text{ m}$: 16 pt \| $\le 2.500\text{ m}$: 11 pt \| $> 3.500\text{ m}$: 2 pt |
| **3. Convenienza Economica Prezzo** | **20 pt** | Prezzo $\le 7,5\text{ €/mq}$: 20 pt \| Nel target $7,5 – 9,0\text{ €/mq}$: 18 pt \| $9 – 10\text{ €/mq}$: 11 pt \| $> 12\text{ €/mq}$: 1 pt |
| **4. Resa Energetica & Dimensione** | **15 pt** | Insolazione regionale PVGIS (max 10 pt) + Bonus superficie (mq $\ge 100\text{k}$: +5 pt, $\ge 50\text{k}$: +4 pt, $\ge 20\text{k}$: +3 pt) |
| **5. Reperibilità della Proprietà** | **10 pt** | PEC + Telefono verificati: 10 pt \| Solo PEC o Telefono: 8 pt \| Persona Giuridica censita: 7 pt \| Particella nota: 4 pt |

### Classi di Rating Commerciale:
* 🟢 **TOP OPPORTUNITÀ (Score $\ge 75$):** Priorità massima, allaccio a breve raggio, conformità piena, prezzo in target.
* 🟡 **QUALIFICATO (Score $60 – 74$):** Ottima area, richiede verifica su un parametro (es. distanza cabina tra 1,5 e 2 km).
* ⚪ **SECONDARIO (Score $< 60$):** Da archiviare o tenere in pipeline di riserva.

---

## 5. Modello Finanziario & Parametri di Redditività

Il motore confronta per ciascun terreno due strategie contrattuali:

### Parametri Finanziari Standard Italia 2026:
* **CAPEX EPC Impianto Fisso:** $680.000\text{ €/MWp}$ (chiavi in mano, moduli, inverter, montaggio).
* **CAPEX EPC Impianto Tracker:** $750.000\text{ €/MWp}$ ($+70.000\text{ €/MWp}$ per strutture motorizzate).
* **Prezzo Cattura Energia PPA / Mercato:** $85,0\text{ €/MWh}$.
* **OPEX O&M, Assicurazione & Sicurezza:** $14.000\text{ €/MWp/anno}$ (Fisso) \| $16.000\text{ €/MWp/anno}$ (Tracker).

### Le Due Opzioni a Confronto:
1. **Opzione Diritto di Superficie (30 Anni) — *Consigliata per Sviluppatori / Fondi*:**
   * Canone annuo benchmark: **$3.000\text{ €/ettaro/anno}$** (pari a circa $0,30\text{ €/mq/anno}$).
   * Azzeramento del CAPEX di acquisto terreno, massimizzazione dell'IRR del progetto.
2. **Opzione Acquisto Diretto del Terreno:**
   * Prezzo target benchmark: **$8,0 – 9,0\text{ €/mq}$**.
   * Payback medio dell'investimento: **$6,3 – 7,1\text{ Anni}$** (ancora più rapido con tracker grazie all'extra-ricavo annuo).

---

## 6. Report delle Criticità & Analisi dei Rischi (Gap Analysis)

Di seguito sono evidenziati i **5 colli di bottiglia attuali** del processo di ricerca e le soluzioni operative per mitigarli:

### ⚠️ Criticità 1: Capacità di Accoglienza della Cabina Primaria (Hosting Capacity)
* **Descrizione del Rischio:** Il motore calcola con esattezza la distanza fisica e il costo del cavidotto per la cabina primaria più vicina. Tuttavia, la cabina potrebbe essere **elettricamente satura** (in congestione di rete MT per troppe domande di connessione già presentate da altri sviluppatori).
* **Impatto:** Se la cabina è satura, Enel/Terna emette una Soluzione Tecnica Minima di Connessione (STMG) che impone l'allaccio in Alta Tensione su stazioni remote, facendo lievitare i costi.
* **Soluzione / Mitigazione:** Incrociare periodicamente i codici `COD_AC` con i report trimestrali di saturazione virtuale pubblicati da E-Distribuzione, penalizzando nello score le cabine dichiarate "Rosse".

### ⚠️ Criticità 2: Risoluzione Catastale Puntuale da Open Data
* **Descrizione del Rischio:** Gli Open Data regionali identificano perfettamente la posizione baricentrica, il comune e l'estensione dell'area, ma per avere la lista certificata di tutti i singoli numeri di **Foglio e Particella catastale** serve un'interrogazione al Catasto dell'Agenzia delle Entrate.
* **Impatto:** Fino a quando non si effettua la visura puntuale, non si possono depositare le istanze formali.
* **Soluzione / Mitigazione:** Mantenere la strategia a "imbuto": usare i dati attuali per la selezione e la presentazione dei **Blind Teaser**; acquistare le visure catastali puntuali (costo: ~0,20 € – 1,00 € a particella) solo sulle aree per cui uno sviluppatore firma una Lettera d'Intenti (LOI/NDA).

### ⚠️ Criticità 3: Frammentazione della Proprietà Fondiaria
* **Descrizione del Rischio:** Su appezzamenti agricoli superiori a 10–15 ettari, il terreno può essere suddiviso tra decine di eredi o piccoli comproprietari privati, allungando i tempi di firma del preliminare di opzione.
* **Impatto:** Rischio di stallo contrattuale per mancato accordo di tutti i comproprietari.
* **Soluzione / Mitigazione:** L'algoritmo di SunPro assegna un **punteggio preferenziale alle Persone Giuridiche (Aziende agricole, società immobiliari, cave, curatele fallimentari)** rispetto alle persone fisiche, privilegiando interlocutori singoli capaci di decidere rapidamente.

### ⚠️ Criticità 4: Pendenza e Morfologia Locale di Dettaglio
* **Descrizione del Rischio:** Nelle aree collinari o pedemontane, un terreno può avere un'ottima esposizione generale ma presentare micro-avvallamenti, pendenze verso Nord superiori al 10% o zone d'ombra orografica.
* **Impatto:** Costi imprevisti di sbancamento o perdite di producibilità del 5–10%.
* **Soluzione / Mitigazione:** Screening preliminare dell'orografia con modelli di elevazione digitale (DEM SRTM/Copernicus 25m) ed esame visivo satellitare in 3D prima del sopralluogo in campo.

### ⚠️ Criticità 5: Decreti Regionali sulle Aree Idonee
* **Descrizione del Rischio:** In attuazione del D.M. Aree Idonee (giugno 2024), le Regioni stanno emanando leggi regionali che potrebbero introdurre fasce di rispetto aggiuntive rispetto a beni culturali tutelati.
* **Impatto:** Possibile variazione dei buffer autorizzativi da regione a regione.
* **Soluzione / Mitigazione:** Mantenere il focus prioritario sulle **aree brownfield (cave dismesse, discariche, adiacenze Z.I. 350m)** che rimangono blindate e idonee ex lege per legge statale primaria indipendentemente dalle delibere regionali.

---

## 7. Roadmap di Scalabilità & Consigli per i Soci

Per trasformare la piattaforma in un generatore massivo di deal commerciali ad alto rendimento, si raccomanda il seguente piano operativo:

1. **Fase Immediata (Goz-to-Market sui 36 Lead Qualificati):**
   * Utilizzare i **36 Blind Teaser PDF One-Pager** generati nella cartella `blind_teasers/` per contattare sviluppatori primari (CPO, fondi rinnovabili, general contractor EPC).
   * Proporre l'accesso ai dati completi e la stipula del preliminare fondiario solo previa firma di **NDA / Accordo di Riservatezza**.
2. **Espansione Territoriale a Costo Zero (Nord & Centro):**
   * Sfruttare il **Database Nazionale delle 2.107 Cabine Primarie ARERA/GSE** per estendere la scansione alle regioni Toscana, Veneto, Piemonte e Puglia senza costi infrastrutturali aggiuntivi.
3. **Budget Mirato per Visure di Chiusura:**
   * Non spendere soldi a monte in banche dati a pagamento massive. Allocare un micro-budget di **50 € – 150 € in crediti API catastali (es. Openapi.it)** da spendere unicamente sui terreni con trattativa calda avviata.

---

*Documento riservato redatto e autenticato dal motore di sviluppo SunPro (Nicola Valigi Engine System).*
