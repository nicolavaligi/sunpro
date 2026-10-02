# SunPro — Geo-Intelligence 3D & Solar Land Acquisition

[![Author: Nicola Valigi Engine System](https://img.shields.io/badge/Author-Nicola%20Valigi%20Engine%20System-blue.svg)](https://github.com/nicolavaligi)
[![GitHub Pages: Live](https://img.shields.io/badge/Live-GitHub%20Pages-brightgreen.svg)](https://nicolavaligi.github.io/sunpro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![Web UI: Port 8503](https://img.shields.io/badge/Web%20UI-Port%208503-red.svg)](http://localhost:8503)

Piattaforma di **Geo-Intelligence 3D** per l'origination e acquisizione autonoma di terreni fotovoltaici Utility-Scale & Agrivoltaico conforme al **D.Lgs. 199/2021 (Aree Idonee)**. Include viewer satellitare 3D con volo orbitale, agente decisionale AI, estrazione catastale e generazione automatica di **Dossier Commerciali PDF**.

🌐 **Demo Live Web (GitHub Pages):** [https://nicolavaligi.github.io/sunpro/](https://nicolavaligi.github.io/sunpro/)


---

## 🎯 Criteri di Qualificazione & Target Operativo

- **Superficie Minima:** >= **2 ettari (20.000 mq)** continua o accorpabile.
- **Target Prezzo:** **8,00 – 9,00 €/mq** (o canone diritto di superficie 30 anni @ 2.800–3.500 €/ha/anno).
- **Buffer Zone Industriali:** Entro **350 metri** da insediamenti industriali, artigianali o commerciali (PIP/D.I.).
- **Fascia Autostradale:** Entro **300 metri** dall'asse di autostrade e raccordi viari principali.
- **Tipologie Prioritarie:** Ex cave esaurite/dismesse, miniere, discariche bonificate, siti industriali brownfield.
- **Connessione Rete:** Prossimità metrica a Cabine Primarie AT/MT (Terna / Enel Distribuzione DSO) entro 1,5–3 km con stima CAPEX di elettrodotto.
- **Regioni Prioritarie:** Lombardia, Veneto, Emilia-Romagna, Piemonte, Toscana, Umbria, Marche.

---

## 📦 Struttura del Progetto

```
solar-land-acquisition-crawler/
├── .venv/                      # Ambiente isolato gestito con uv
├── config.py                   # Parametri tecnici, normativi e pesi di scoring
├── app.py                      # Applicazione Desktop Streamlit su porta 8503
├── cli.py                      # Interfaccia CLI con tabelle Rich da terminale
├── run_app.py                  # Script launcher rapido per desktop
├── pipeline.py                 # Pipeline di calcolo energetico, catastale e scoring
├── crawler/
│   ├── spatial_engine.py       # Buffer 350m/300m, Overpass API, calcolo CAPEX rete
│   ├── cadastral_resolver.py   # WMS Catasto, codici Belfiore e coordinate
│   └── owner_discovery.py      # Estrazione dati proprietario, PEC, P.IVA e pitch script
├── scoring/
│   └── scorer.py               # Algoritmo multicriterio 0-100 pesato
├── reports/
│   └── generator.py            # Generatore ReportLab PDF (A4) ed HTML per commerciali
├── data/
│   ├── storage.py              # Database SQLite persistente (solar_land_leads.db)
├── MANUALE_COMMERCIALE.md      # Guida strategica e script di trattativa
└── README.md
```

---

## 🚀 Avvio Rapido

### 1. Attivazione Ambiente ed Esecuzione CLI
```bash
# Entra nella cartella del progetto
cd ~/solar-land-acquisition-crawler

# Elenca tutte le aree qualificate censite
.venv/bin/python3 cli.py list

# Filtra per regione (es. Emilia-Romagna o Lombardia) e score minimo
.venv/bin/python3 cli.py list --regione Lombardia --min-score 75

# Genera direttamente il Dossier Commerciale PDF di un lead
.venv/bin/python3 cli.py report LEAD-LOMB-001
```

### 2. Avvio Applicazione Desktop
```bash
# Esegui il launcher desktop
./run_app.py

# Oppure tramite streamlit:
.venv/bin/python3 -m streamlit run app.py --server.port=8503
```
L'interfaccia si aprirà automaticamente nel browser all'indirizzo **`http://localhost:8503`**.

---

## 📊 Caratteristiche dell'Applicazione Desktop

1. **Mappa Geospaziale Interattiva:**
   - Visualizzazione su mappa OpenStreetMap / Satellite con cerchi buffer per cabine primarie e marker colorati per classe di rating (🟢 Top Lead >= 75, 🟠 Qualificato 60–74, 🔵 Secondario < 60).
2. **Pipeline Commerciale & Tracking:**
   - Monitoraggio dello stato dei contatti (`DA_CONTATTARE`, `IN_CONTATTO`, `IN_TRATTATIVA`, `OPZIONATO`, `SCARTATO`) con aggiornamento note e persistenza automatica su SQLite.
3. **One-Click Dossier PDF:**
   - Generazione istantanea con 1 click di un report A4 esecutivo completo con dati catastali (Comune, Foglio, Particella), stima MWp e MWh producibili, distanza e nome cabina AT/MT, preventivo acquisto vs diritto di superficie trentennale, contatti proprietario e script di chiamata pronto per l'agente.
4. **Inserimento & Scansione Nuove Aree:**
   - Form rapido per inserire coordinate e parametri di un nuovo terreno, con scoring e calcolo energetico istantaneo.

---

## ⚖️ Licenza & Proprietà

Sviluppato da **Nicola Valigi Engine System**. Tutti i diritti riservati.
Email di contatto: `305862309+nicolavaligi@users.noreply.github.com`
