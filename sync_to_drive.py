"""
Script di sincronizzazione ed esportazione del prototipo sul Google Drive personale.
Crea la cartella 'Solar_Land_Origination_Prototipo' con mappe interattive, tutti i PDF dei lead,
dati tabellari (CSV e JSON) e scorciatoia per avvio locale con un doppio click.
Autore: Nicola Valigi Engine System
"""

import shutil
import json
from pathlib import Path
import pandas as pd

from data.storage import get_all_leads
from reports.generator import generate_pdf_dossier
from build_map import build_standalone_map

def sync_prototype_to_drive():
    # Percorso Google Drive personale
    drive_base = Path("/Users/houdinick/Google Drive/Il mio Drive")
    if not drive_base.exists():
        print(f"Attenzione: Percorso Google Drive non trovato: {drive_base}")
        return

    target_dir = drive_base / "Solar_Land_Origination_Prototipo"
    target_dir.mkdir(parents=True, exist_ok=True)

    pdf_dir = target_dir / "Dossier_PDF_Commerciali"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    data_dir = target_dir / "Dati_e_Tabelle"
    data_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Sincronizzazione prototipo in: {target_dir}")

    # 1. Generazione e copia della mappa standalone HD (Satellitare + OpenStreetMap)
    map_file = target_dir / "Mappa_Interattiva_Aree_Fotovoltaiche.html"
    build_standalone_map(map_file)
    print(f"  ✓ Mappa interattiva HD salvata: {map_file.name}")

    # 2. Generazione di tutti i Dossier PDF individuali per i commerciali
    leads = get_all_leads()
    print(f"  📄 Generazione di {len(leads)} dossier commerciali PDF...")
    for l in leads:
        generated_pdf = generate_pdf_dossier(l)
        target_pdf = pdf_dir / generated_pdf.name
        shutil.copy2(generated_pdf, target_pdf)
    print(f"  ✓ {len(leads)} file PDF salvati in Dossier_PDF_Commerciali/")

    # 3. Esportazione dati in CSV ed Excel-friendly JSON
    df = pd.DataFrame(leads)
    csv_file = data_dir / "aree_fotovoltaiche_qualificate.csv"
    json_file = data_dir / "aree_fotovoltaiche_qualificate.json"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Dati esportati: {csv_file.name} e {json_file.name}")

    # 3b. Copia File KML (Google Earth), GeoJSON e Modello Finanziario
    kml_src = Path(__file__).resolve().parent / "SunPro_Pipeline_Terreni_Fotovoltaico.kml"
    geojson_src = Path(__file__).resolve().parent / "SunPro_Pipeline_Terreni_Fotovoltaico.geojson"
    fin_src = Path(__file__).resolve().parent / "SunPro_Executive_Financial_Model.csv"

    if kml_src.exists():
        shutil.copy2(kml_src, target_dir / "Visualizza_Pipeline_in_Google_Earth_3D.kml")
        print("  ✓ File KML per Google Earth 3D copiato nella cartella principale di Drive.")
    if geojson_src.exists():
        shutil.copy2(geojson_src, data_dir / "SunPro_Pipeline_Terreni_Fotovoltaico.geojson")
    if fin_src.exists():
        shutil.copy2(fin_src, data_dir / "SunPro_Executive_Financial_Model.csv")
        print("  ✓ Modello Finanziario Esecutivo CSV copiato in Dati_e_Tabelle/.")

    # 4. Copia Manuale Commerciale & Script di Negoziazione
    manuale_src = Path(__file__).resolve().parent / "MANUALE_COMMERCIALE.md"
    if manuale_src.exists():
        shutil.copy2(manuale_src, target_dir / "MANUALE_COMMERCIALE_ORIGINATION.md")
        print(f"  ✓ Manuale commerciale copiato.")

    # 5. Creazione di un launcher macOS con doppio click (.command)
    launcher_script = target_dir / "Avvia_Prototipo_Locale.command"
    launcher_content = """#!/bin/bash
cd /Users/houdinick/solar-land-acquisition-crawler
./run_app.py
"""
    with open(launcher_script, "w") as f:
        f.write(launcher_content)
    launcher_script.chmod(0o755)
    print(f"  ✓ Launcher rapido per macOS creato: {launcher_script.name}")

    # 6. README esplicativo per consultazione su Drive da qualunque dispositivo
    readme_drive = target_dir / "LEGGIMI_ACCESSO_PROTOTIPO.md"
    with open(readme_drive, "w", encoding="utf-8") as f:
        f.write("""# ☀️ SunPro — Accesso Condiviso al Prototipo

> **Prototipo di Nicola Valigi Engine System**  
> Mappatura geospaziale e qualificazione terreni per impianti fotovoltaici utility-scale & agrivoltaici in Italia (Nord e Centro).

---

## 📁 Contenuto della Cartella su Drive

1. **`Mappa_Interattiva_Aree_Fotovoltaiche.html`**:
   - Apribile con qualsiasi browser (Safari, Chrome, tablet o smartphone) anche offline e senza Python.
   - Include layer vettoriale OpenStreetMap, visualizzazione neutra CartoDB e **ortofoto satellitare ad alta risoluzione Esri**.
   - Mostra le 11 aree pilota qualificate (72,3 ettari, ~59,7 MWp), cerchi buffer di allaccio alle cabine primarie e popup completi con link a satellite HD.

2. **`Dossier_PDF_Commerciali/`**:
   - Cartella contenente **11 Dossier Commerciali One-Page (A4)** pronti per la stampa o l'invio via email ai proprietari o ai partner.
   - Ogni scheda contiene: dati catastali (Comune, Foglio, Particella), coordinate GPS, MWp installabili, distanza cabina AT/MT, preventivo acquisto @ 8–9 €/mq vs Diritto di Superficie 30 anni, dati societari/PEC e script telefonico per il sales rep.

3. **`Dati_e_Tabelle/`**:
   - `aree_fotovoltaiche_qualificate.csv`: Tabella completa importabile direttamente su Excel o Google Fogli.
   - `aree_fotovoltaiche_qualificate.json`: Feed strutturato per integrazioni software.

4. **`MANUALE_COMMERCIALE_ORIGINATION.md`**:
   - Guida strategica completa: normativa D.Lgs. 199/2021 (Aree Idonee), buffer 350m Z.I., 300m autostrade, cave/discariche, protocollo di ricerca proprietari (Sister/Telemaco) e gestione obiezioni.

5. **`Avvia_Prototipo_Locale.command`**:
   - Clicca due volte su questo file da macOS per avviare istantaneamente l'applicazione desktop interattiva su `http://localhost:8503`.
""")
    print(f"  ✓ File LEGGIMI_ACCESSO_PROTOTIPO.md generato.")
    print(f"✅ Sincronizzazione completata con successo su Google Drive!")

if __name__ == "__main__":
    sync_prototype_to_drive()
