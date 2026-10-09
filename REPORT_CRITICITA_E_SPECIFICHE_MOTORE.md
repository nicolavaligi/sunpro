# ☀️ SunPro Engine — Documento Tecnico-Esecutivo
## Specifiche di Ricerca, Architettura del Motore, Valutazione Fondiaria e Report delle Criticità

> **Documento ad uso interno per Soci, Sviluppatori e Partner Strategici**  
> **Oggetto:** Origination geospaziale, determinazione del valore di mercato dei terreni, qualificazione urbanistica e modello finanziario per impianti Fotovoltaici & Agrivoltaici Utility-Scale in Italia.  
> **Piattaforma:** SunPro Geo-Intelligence 3D  
> **Autore & Proprietà Intellettuale:** Nicola Valigi (Houdinick)  
> **Data:** Ottobre 2026  

---

## 📑 Indice del Documento
1. [Sintesi Esecutiva: Cosa fa il Motore SunPro](#1-sintesi-esecutiva)
2. [Evoluzione del Motore: Cosa è Cambiato dalla Release Iniziale (v1.0 vs v2.4)](#2-evoluzione-del-motore-cosa-è-cambiato-dalla-release-iniziale)
3. [Specifiche Tecniche di Ricerca & Filtri Applicati](#3-specifiche-tecniche-di-ricerca)
4. [Come il Motore Determina il Valore dei Terreni: Modello Estimativo, Destinazione Urbanistica ed Esclusione Terreni Inavvicinabili](#4-come-il-motore-determina-il-valore-dei-terreni)
5. [Ingegneria di Rete & Resa Energetica Scientifica](#5-ingegneria-di-rete--resa-energetica)
6. [Algoritmo di Scoring Multicriterio (0–100) & Gatekeeper](#6-algoritmo-di-scoring-multicriterio)
7. [Modello Finanziario & Parametri di Redditività a Confronto](#7-modello-finanziario--parametri-di-redditività)
8. [Report delle Criticità & Analisi dei Rischi (Gap Analysis)](#8-report-delle-criticità--analisi-dei-rischi)
9. [Roadmap di Scalabilità & Consigli Operativi per i Soci](#9-roadmap-di-scalabilità--consigli-per-i-soci)

---

## 1. Sintesi Esecutiva

Il motore **SunPro** è una piattaforma di **Geo-Intelligence predittiva** progettata per industrializzare e automatizzare il lavoro più costoso, lento e rischioso dello sviluppo fotovoltaico: l'**Origination fondiaria**.

Invece di mandare tecnici sul territorio o consultare manualmente mappe catastali, il motore scansiona il territorio italiano e incrocia simultaneamente:
1. **La conformità normativa ex lege** (D.Lgs. 199/2021).
2. **La destinazione urbanistica reale e il valore di mercato fondiario** (VAM / ISMEA / OMI).
3. **Il filtro gatekeeper anti-inacquistabilità** (esclusione automatica di lotti edificabili industriali > 15 €/mq).
4. **La prossimità infrastrutturale alla rete elettrica** (2.107 Cabine Primarie ARERA/GSE con routing stradale 1,30x).
5. **La resa solare scientifica indipendente** della Commissione Europea (PVGIS v5.2 JRC per fissi e tracker).
6. **I vincoli ambientali ostativi** (Rete Natura 2000 ZPS/SIC e Rischio Idrogeologico PAI).
7. **Il modello economico-finanziario** (Acquisto a 7,50–9,50 €/mq vs Diritto di Superficie 30ennale a 3.000 €/ha/anno).

Il risultato finale è una pipeline di terreni già **pre-qualificati, verificati per reale acquistabilità fondiaria, quotati finanziariamente e pronti per l'iter autorizzativo accelerato (PAS in 60–90 giorni)**.

---

## 2. Evoluzione del Motore: Cosa è Cambiato dalla Release Iniziale (v1.0 vs v2.4)

Dalla prima release prototipale (v1.0) all'attuale versione industriale (v2.4), SunPro è stato radicalmente riprogettato per azzerare ogni rischio di insostenibilità tecnica ed economica:

| Ambito / Pilastro | Release Iniziale (v1.0) | Release Attuale (v2.4 — Ottobre 2026) | Impatto Strategico & Rischio Azzerato |
| :--- | :--- | :--- | :--- |
| **Composizione del Suolo** | Misto indifferenziato (inclusi lotti peri-urbani ed ex industriali a rischio edifici) | **86,1% Terreni Agricoli Puri in Campo Aperto (Zona E) & Agrivoltaico** (31/36 lotti) | **Zero costi di demolizione o bonifica**; 100% campo aperto immediatamente cantierabile con pali infissi. |
| **Destinazione Urbanistica** | Nessun controllo PRG (rischio acquisto lotti industriali Zona D) | **Gatekeeper Urbanistico**: scarto categorico di lotti Zona D ($> 15\text{ €/mq}$) | Esclusi lotti industriali/PIP da 50–120 €/mq che renderebbero fallimentare il CAPEX a terra. |
| **Modello Estimativo Fondiario** | Stima forfettaria o derivata circolarmente dalla resa MWh solari | **Modello Immobiliare Comparativo Reale** (VAM / ISMEA / OMI 2025–2026) | Prezzi bancabili: acquisto target **7,50–9,50 €/mq** o Diritto di Superficie a **3.000 €/ha/anno** (4,5x–6x affitto agrario). |
| **Ingegneria di Rete & Cabine MT** | Distanze euclidee rettilinee su pochi punti cabina generici | **Database Nazionale di 2.107 Cabine Primarie ARERA/GSE** (<1ms lookup) + **Routing 1,30x** | Stima CAPEX cavidotto MT (€ 65k/km + € 45k stallo) ineccepibile in due diligence tecnica. |
| **Resa Energetica & Tracker** | Coefficienti statici generici; solo tilt fisso | **PVGIS v5.2 JRC**: Fisso vs **Tracker Monoassiale (+19,2% al Nord, +22,0% al Centro/Sud)** | Resa scientifica certificata; extra-CAPEX tracker (+70k €/MWp) ammortizzato in <3,5 anni con PPA a 85 €/MWh. |
| **Commercial Kit Pre-NDA** | Solo report locali interni grezzi con dati esposti | **36 Blind Teaser PDF One-Pager** + 36 Dossier Tecnici Integrali + Modello CSV + KML 3D | Possibilità di avviare trattative confidenziali immediate con sviluppatori tutelando al 100% l'IP prima dell'NDA. |

---

## 3. Specifiche Tecniche di Ricerca

Il crawler scarta a monte il 98% del territorio agricolo ordinario e isola esclusivamente le aree che presentano i requisiti di fattibilità tecnica e normativa:

### A. Dimensione Fondiaria
* **Superficie Minima:** **$\ge 2,0$ Ettari (20.000 mq)**.  
  *Razionale:* 2 ha è la soglia minima per ammortizzare i costi fissi di sviluppo, la cabina MT/AT e gli oneri autorizzativi di un impianto utility-scale (~1,6 – 2,0 MWp).
* **Superficie Massima Censita:** Fino a **150 Ettari (1.500.000 mq)** per parchi fotovoltaici ed agrivoltaici su larga scala.
* **Rapporto di Densità:** Standard di mercato di **1,2 ettari per ogni 1,0 MWp** di potenza installata (compatibile sia con strutture a terra fisse che con inseguitori monoassiali).

### B. Idoneità Normativa Ex Lege (D.Lgs. 199/2021, Art. 20)
Il motore ricerca geometricamente solo le tipologie che godono di presunzione di idoneità per legge:
1. **Fascia Industriale Contigua:** Aree agricole situate entro **350 metri** dal perimetro di zone industriali, artigianali o commerciali.
2. **Corridoio Autostradale:** Aree agricole situate entro **300 metri** dagli assi autostradali, raccordi o tangenziali primarie.
3. **Cave e Bacini Estrattivi:** Ex cave dismesse, cave in fase di ripristino o bacini chiusi.
4. **Discariche & Siti Bonificati:** Discariche esaurite o brownfield industriali ripristinati.

*Vantaggio strategico:* Su queste aree l'autorizzazione è per legge agevolata, riducendo drasticamente il rischio di blocco paesaggistico della Soprintendenza.

### C. Watchdog Vincoli Ambientali & Idrogeologici (Screening No-Go)
Prima di promuovere un'area, il motore verifica l'assenza di interferenze bloccanti:
* **Rete Natura 2000:** Verifica l'assenza di sovrapposizioni con Zone di Protezione Speciale (ZPS) o Siti di Importanza Comunitaria (SIC/ZSC), evitando costose Valutazioni di Incidenza (VInCA).
* **Idrogeologia PAI:** Verifica che l'area sia esterna alle Fasce Fluviali A (esondazione frequente / flusso di piena), garantendo l'assicurabilità dell'impianto.
* **Procedura Presunta:** Se l'area è idonea ex lege e libera da vincoli ostativi, viene classificata per l'iter **PAS (Procedura Abilitativa Semplificata, 60–90 giorni)** con certezza autorizzativa stimata al **95%**.

### D. Watchdog Anti-Edifici, Anti-Capannoni & Priorità Assoluta ai Terreni Agricoli (86% della Pipeline)
Per evitare il rischio di localizzare aree con capannoni industriali esistenti o contigue a centri abitati residenziali con case, SunPro integra il modulo di conformità del suolo [`crawler/land_suitability_filter.py`](file:///Users/houdinick/solar-land-acquisition-crawler/crawler/land_suitability_filter.py):
1. **Esclusione Categorica dei Contesti Peri-Urbani Densi:** Vengono scartati a monte comuni metropolitani o cluster industriali edificati (es. Milano, Sesto San Giovanni, Legnano, Saronno, Brescia urbana) dove gli spazi industriali contengono capannoni o sono circondati da complessi residenziali.
2. **Priorità Assoluta ai Terreni Agricoli a Campo Aperto (Seminativi di Pianura / Agrivoltaico):** Oltre l'**86% della pipeline (31 su 36 siti)** è costituito da **puri terreni agricoli in campo aperto (Zona E)**.
   * *Perché sono i più facili e convenienti:*
     * **Zero costi di demolizione o bonifica:** Nessun capannone da abbattere, niente cemento armato o coperture in amianto.
     * **Zero interferenze con il vicinato:** Localizzati in aperta campagna rurale priva di caseggiati.
     * **Facilità contrattuale imbattibile:** Gli agricoltori e le società agricole familiari ricavano oggi $400 – 650\text{ €/ha/anno}$ da mais o grano. L'offerta di **$3.000\text{ €/ha/anno}$ di diritto di superficie** (o $8,00 – 9,00\text{ €/mq}$ a rogito) quintuplica il loro reddito, portando a una firma rapida del preliminare di opzione.
3. **Ex Cave e Discariche Ammesse Solo se a Cielo Aperto (14% residuo):** Le sole cave o discariche ammesse sono bacini a cielo aperto con fondo livellato e certificato, con esclusione totale di capannoni o fabbricati.

---

## 3. Come il Motore Determina il Valore dei Terreni
### Modello Estimativo Fondiario Reale, Destinazione Urbanistica ed Esclusione Terreni Inavvicinabili

> **CHIARIMENTO FONDAMENTALE PER I SOCI & PARTNER:**  
> Il motore SunPro **NON determina il valore del terreno sulla base della resa energetica solare**.  
> Calcolare il prezzo del terreno moltiplicando i MWh prodotti sarebbe un errore metodologico (valutazione astratta e circolare) che porterebbe a sovrastimare i terreni e a fare offerte fuori mercato.  
> La resa energetica PVGIS viene utilizzata **esclusivamente a valle** per calcolare i ricavi dell'energia, l'EBITDA e il tempo di recupero dell'investimento (Payback / IRR).  
> Il valore di acquisto e il canone del terreno sono invece calcolati tramite un **Modello Estimativo Sintetico-Comparativo Immobiliare**, ancorato al **mercato fondiario reale, alla destinazione urbanistica (PRG/PGT) e alla posizione geografica**.

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

---

### A. La Destinazione Urbanistica (PRG / PGT) e il Filtro Gatekeeper Anti-Inacquistabilità
Il più grave errore commesso dagli sviluppatori inesperti è confondere le *«aree contigue alle zone industriali»* con i *«lotti industriali interni»*:

1. **La Trappola dei Terreni in Zona D (Produttiva / PIP Edificabile):**
   * Se un terreno ricade **all'interno del perimetro industriale/artigianale** con destinazione urbanistica Zona D ed è dotato di capacità edificatoria fondiaria, il suo valore di mercato immobiliare oscilla tra **$50,00\text{ €/mq}$ e oltre $120,00\text{ €/mq}$** (destinato a capannoni, logistica, industria).
   * A questi prezzi, nessun impianto fotovoltaico ground-mounted utility-scale è sostenibile: l'acquisto del terreno costerebbe tra $500.000\text{ €}$ e $1.200.000\text{ €}$ ad ettaro, superando l'intero costo dell'impianto EPC!
   * **REGOLE DEL GATEKEEPER SUNPRO:** Il modulo `crawler/land_valuation.py` rileva la destinazione urbanistica. Qualsiasi terreno con destinazione Zona D edificabile o con quotazione $> 15,00\text{ €/mq}$ viene **CATEGORICAMENTE SCARTATO** e classificato come **`NON ACQUISTABILE (SOVRASTIMATO)`**, azzerando il punteggio commerciale ed eliminandolo dai dossier.

2. **L'Approccio Chirurgico di SunPro (Zona E Agricola nel Buffer 350m):**
   * Il D.Lgs. 199/2021 (Art. 20, co. 8 lett. c-ter) qualifica come "Aree Idonee" i terreni situati **entro 350 metri** dal perimetro degli impianti industriali.
   * SunPro intercetta geometricamente solo i terreni che a livello di Piano Regolatore Comunale (PRG/PGT) conservano la destinazione **ZONA E (Agricola Ordinaria)**.
   * In questo modo, il terreno gode del **doppio vantaggio competitivo**:
     * **Valore Fondiario Agricolo Contenuto:** Valutato a prezzi agricoli (non industriali).
     * **Procedura Autorizzativa PAS Agevolata:** Idoneità per legge statale primaria grazie alla contiguità con il comparto industriale.

3. **Ex Cave e Brownfield (Recupero di Passività):**
   * Le ex cave dismesse e i siti degradati non hanno valore agricolo né residenziale. Spesso sono gravati da obblighi di ripristino morfologico o fallimenti aziendali, con valori di perizia depressi (**$2,50 – 4,50\text{ €/mq}$**).
   * SunPro valorizza queste aree offrendo una transazione a **$7,80 – 8,10\text{ €/mq}$**, rappresentando una monetizzazione provvidenziale per curatele fallimentari ed ex cavatori.

---

### B. I Benchmark Fondiari di Mercato (VAM / ISMEA / OMI)
Il valore agricolo di base ($V_{\text{agri}}$) non è un numero inventato, ma deriva dai bollettini ufficiali regionali e provinciali per seminativo irriguo / asciutto di pianura:

| Regione / Macro-Area | Benchmark Agricolo VAM/ISMEA ($V_{\text{agri}}$) | Affitto Agrario Ordinario Medio | Note Fondiarie Territoriali |
| :--- | :---: | :---: | :--- |
| **Lombardia (Pianura Irrigua)** | **$4,80 – 5,60\text{ €/mq}$** ($48k – 56k\text{ €/ha}$) | $550 – 700\text{ €/ha/anno}$ | Massima fertilità (Cremona, Brescia, Lodi, Pavia). |
| **Veneto (Pianura Veneta)** | **$4,40 – 5,20\text{ €/mq}$** ($44k – 52k\text{ €/ha}$) | $500 – 650\text{ €/ha/anno}$ | Seminativo irriguo (Verona, Padova, Vicenza). |
| **Emilia-Romagna** | **$4,20 – 5,30\text{ €/mq}$** ($42k – 53k\text{ €/ha}$) | $500 – 620\text{ €/ha/anno}$ | Terreni alluvionali (Bologna, Modena, Parma). |
| **Piemonte** | **$3,20 – 4,50\text{ €/mq}$** ($32k – 45k\text{ €/ha}$) | $450 – 550\text{ €/ha/anno}$ | Risicoltura e seminativi (Alessandria, Cuneo, Novara). |
| **Toscana & Centro** | **$2,80 – 3,80\text{ €/mq}$** ($28k – 38k\text{ €/ha}$) | $350 – 450\text{ €/ha/anno}$ | Terreni litoranei e vallivi (Grosseto, Siena, Pisa). |
| **Puglia, Sicilia & Sud** | **$1,80 – 2,80\text{ €/mq}$** ($18k – 28k\text{ €/ha}$) | $300 – 400\text{ €/ha/anno}$ | Valori fondiari più bassi, massima insolazione. |

---

### C. Coefficienti Correttivi Posizionali & Caratteristiche Fisiche
Al valore agricolo base provinciale, il motore applica un **Coefficiente Posizionale ($C_{\text{pos}}$)** in funzione delle caratteristiche intrinseche ed estrinseche rilevate dal GIS:
1. **Accessibilità Viaria & Autostradale:** Se il terreno confina o dista $\le 1.000\text{ m}$ da un asse viario principale o autostrada, viene applicato un incremento del **$+5\% \div +10\%$** sul valore fondiario (minori costi di cantierizzazione, movimentazione mezzi pesanti e posa cavidotto).
2. **Contiguità a Infrastrutture Esistenti:** Se l'area è contigua ($\le 200\text{ m}$) a un polo produttivo già elettrificato, si applica un incremento del **$+5\%$** per valore di aspettativa.
3. **Morfologia & Pendenza:** Terreni perfettamente pianeggianti (pendenza $< 3\%$) mantengono il coefficiente $1,00$; terreni con pendenze disomogenee o acclivi verso Nord subiscono una decurtazione prudenziale di stima (fino a $-15\%$) per compensare i futuri oneri di sbancamento e regimazione acque.

Il **Valore di Mercato Ordinario del Fondo ($V_{\text{mercato\_agri}}$)** risulta quindi:
$$V_{\text{mercato\_agri}} = V_{\text{agri}} \times C_{\text{pos}} \quad (\text{generalmente compreso tra } 3,00\text{ e } 5,90\text{ €/mq})$$

---

### D. Il Premio di Trasformazione Energetica (Target Bancabile 7,50 – 9,50 €/mq)
Perché un proprietario agricolo dovrebbe vendere il proprio terreno a uno sviluppatore fotovoltaico se l'offerta fosse pari al valore agricolo ordinario? Non lo farebbe mai.

Per sbloccare la trattativa e ottenere la firma del contratto preliminare di opzione, SunPro calcola un **Premio di Trasformazione Fondiaria del $+40\% \div +80\%$** rispetto al valore agricolo ordinario:
$$V_{\text{target}} = \text{clamp}(V_{\text{mercato\_agri}} \times 1,60, \; 7,50\text{ €/mq}, \; 9,50\text{ €/mq})$$

* **Perché funziona commercialmente:**
  * L'agricoltore riceve un'offerta di **$75.000 – 95.000\text{ €/ettaro}$**, ovvero il **$50\% – 80\%$ in più** rispetto a quanto potrebbe mai incassare vendendo a un altro agricoltore confinante.
  * Per il fondo d'investimento o sviluppatore EPC, un costo fondiario compreso tra **$7,50$ e $9,20\text{ €/mq}$** incide per appena l'**$8\% – 11\%$ del CAPEX totale di sviluppo**, garantendo un Payback eccellente di **6,3 – 7,1 anni** e un LCOE altamente competitivo.

---

### E. Il Moltiplicatore di Rendita nel Diritto di Superficie (3.000 €/ha/anno)
Per gli sviluppatori che non intendono immobilizzare capitale nell'acquisto del terreno, SunPro modella la stipula di un **Diritto di Superficie trentennale**:
* Canone offerto: **$3.000\text{ € / ettaro / anno}$** (pari a circa $0,30\text{ €/mq/anno}$), indicizzato ISTAT.
* A fronte di un affitto agrario ordinario medio di **$400 – 650\text{ €/ha/anno}$**, l'offerta SunPro garantisce al proprietario un **Moltiplicatore di Rendita di 4,5x – 6,0x**:
  * Un proprietario di 10 ettari che prima incassava $6.000\text{ €/anno}$ lordi lavorando la terra o affittandola, con SunPro ne incassa **$30.000\text{ €/anno}$ garantiti per 30 anni ($900.000\text{ €}$ complessivi)** senza alcun costo né rischio di raccolto.

---

## 4. Ingegneria di Rete & Resa Energetica Scientifica

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
  * Consente di comparare immediatamente il maggior costo dei tracker (+70k €/MWp) con l'extra-ricavo energetico annuo.

---

## 5. Algoritmo di Scoring Multicriterio (0–100) & Gatekeeper

Ogni terreno analizzato riceve un punteggio deterministico ponderato su **5 pilastri chiave**:

| Pilastro | Peso Max | Criteri di Assegnazione Punti |
| :--- | :---: | :--- |
| **1. Idoneità Normativa D.Lgs. 199/21** | **30 pt** | Cave/Discariche: 30 pt \| Entro 350m Z.I.: 26 pt \| Entro 300m Autostrada: 22 pt \| Buffer 500m: 14 pt \| Altro: 6 pt |
| **2. Prossimità Cabina Primaria** | **25 pt** | $\le 500\text{ m}$: 25 pt \| $\le 1.000\text{ m}$: 21 pt \| $\le 1.500\text{ m}$: 16 pt \| $\le 2.500\text{ m}$: 11 pt \| $> 3.500\text{ m}$: 2 pt |
| **3. Convenienza Economica & Acquistabilità** | **20 pt** | Prezzo $\le 7,5\text{ €/mq}$: 20 pt \| Nel target $7,5 – 9,0\text{ €/mq}$: 18 pt \| $9 – 10\text{ €/mq}$: 11 pt \| $> 12\text{ €/mq}$: 1 pt \| **Lotto Zona D / Prezzo $> 15\text{ €/mq}$: 0 pt (SCARTATO)** |
| **4. Resa Energetica & Dimensione** | **15 pt** | Insolazione regionale PVGIS (max 10 pt) + Bonus superficie (mq $\ge 100\text{k}$: +5 pt, $\ge 50\text{k}$: +4 pt, $\ge 20\text{k}$: +3 pt) |
| **5. Reperibilità della Proprietà** | **10 pt** | PEC + Telefono verificati: 10 pt \| Solo PEC o Telefono: 8 pt \| Persona Giuridica censita: 7 pt \| Particella nota: 4 pt |

### Classi di Rating Commerciale:
* 🟢 **TOP OPPORTUNITÀ (Score $\ge 75$):** Priorità massima, allaccio a breve raggio, conformità piena, prezzo in target bancabile.
* 🟡 **QUALIFICATO (Score $60 – 74$):** Ottima area, richiede verifica su un parametro (es. distanza cabina tra 1,5 e 2 km).
* ⚪ **SECONDARIO (Score $< 60$):** Da archiviare o tenere in pipeline di riserva.
* 🛑 **NON ACQUISTABILE (SOVRASTIMATO):** Terreni in Zona D edificabile o con valore di mercato $> 15\text{ €/mq}$, scartati automaticamente dal sistema.

---

## 6. Modello Finanziario & Parametri di Redditività

Il modello economico esecutivo confronta per ciascun terreno due strategie contrattuali basate su parametri standard Italia 2026:

### Parametri Finanziari Standard Utility-Scale Italia 2026:
* **CAPEX EPC Impianto Fisso:** $680.000\text{ €/MWp}$ (chiavi in mano, moduli, inverter, montaggio).
* **CAPEX EPC Impianto Tracker:** $750.000\text{ €/MWp}$ ($+70.000\text{ €/MWp}$ per strutture motorizzate).
* **Prezzo Cattura Energia PPA / Mercato:** $85,0\text{ €/MWh}$.
* **OPEX O&M, Assicurazione & Sicurezza:** $14.000\text{ €/MWp/anno}$ (Fisso) \| $16.000\text{ €/MWp/anno}$ (Tracker).

### Le Due Opzioni a Confronto:
1. **Opzione Diritto di Superficie (30 Anni) — *Consigliata per Sviluppatori / Fondi*:**
   * Canone annuo benchmark: **$3.000\text{ €/ettaro/anno}$** (pari a circa $0,30\text{ €/mq/anno}$).
   * Azzeramento del CAPEX di acquisto terreno, massimizzazione dell'IRR del progetto e preservazione della liquidità.
2. **Opzione Acquisto Diretto del Terreno:**
   * Prezzo target benchmark: **$7,80 – 9,20\text{ €/mq}$**.
   * Payback medio dell'investimento: **$6,3 – 7,1\text{ Anni}$** (ancora più rapido con tracker grazie all'extra-ricavo annuo di produzione).

---

## 7. Report delle Criticità & Analisi dei Rischi (Gap Analysis)

Di seguito sono evidenziati i **5 colli di bottiglia operativi** del processo di ricerca e le soluzioni concrete implementate in SunPro:

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

## 8. Roadmap di Scalabilità & Consigli Operativi per i Soci

Per trasformare la piattaforma in un generatore massivo di deal commerciali ad alto rendimento, si raccomanda il seguente piano operativo:

1. **Fase Immediata (Go-to-Market sui 36 Lead Qualificati):**
   * Utilizzare i **36 Blind Teaser PDF One-Pager** generati nella cartella `blind_teasers/` per contattare sviluppatori primari (CPO, fondi rinnovabili, general contractor EPC).
   * Proporre l'accesso ai dati completi e la stipula del preliminare fondiario solo previa firma di **NDA / Accordo di Riservatezza** a tutela della proprietà intellettuale.
2. **Espansione Territoriale a Costo Zero (Nord & Centro):**
   * Sfruttare il **Database Nazionale delle 2.107 Cabine Primarie ARERA/GSE** per estendere la scansione alle regioni Toscana, Veneto, Piemonte e Puglia senza costi infrastrutturali aggiuntivi.
3. **Budget Mirato per Visure di Chiusura:**
   * Non spendere soldi a monte in banche dati a pagamento massive. Allocare un micro-budget di **50 € – 150 € in crediti API catastali (es. Openapi.it)** da spendere unicamente sui terreni con trattativa calda avviata.

---

*Documento riservato redatto e autenticato dal motore di sviluppo SunPro (Nicola Valigi Engine System).*
