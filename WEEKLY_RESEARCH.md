# Ricerca settimanale SunPro

Il workflow `.github/workflows/weekly-research.yml` esegue la ricerca ogni lunedì alle 07:23 UTC (08:23 in Italia in inverno, 09:23 in estate), alla prima pubblicazione del workflow e su avvio manuale da Actions. GitHub può ritardare le esecuzioni e disattivare gli schedule nei repository pubblici inattivi per 60 giorni: controllare la data del report e lo stato in Actions.

La ricerca copre Lombardia, Veneto, Emilia-Romagna, Piemonte, Toscana, Umbria e Marche. Usa Overpass/OpenStreetMap senza credenziali: way agricole chiuse di almeno 2 ha entro circa 300 m dalle autostrade mappate. Non è una ricerca di annunci di vendita e non prova disponibilità o idoneità. La superficie è calcolata sul poligono OSM con ellissoide WGS84; il punto di navigazione cade al suo interno. I poligoni sono uso del suolo, non confini catastali. Le relazioni multipoligono non sono incluse.

In mappa i candidati hanno poligoni ambra e una sezione dedicata; restano separati dai siti originali e dalle loro stime. Non vengono inventati particelle, prezzi, cabine o qualifiche. Prima di una trattativa servono verifica ortofoto, confini catastali, vincoli e disponibilità del proprietario.

Ogni esecuzione scrive `weekly/latest.md`, `weekly/latest.json`, `weekly/report.html`, `weekly/candidates.geojson` e un archivio per settimana ISO in `weekly/history/`. Confronta gli ID OSM e le geometrie: nuovi, modificati, non più corrispondenti. "Nuovo" significa nuovo per questo monitoraggio. Un errore di fonte è riportato esplicitamente, conservando i candidati precedenti della regione e la data dell'ultimo riscontro. Un nuovo tentativo nella stessa settimana aggiorna il relativo archivio.

Il workflow salva i risultati nel repository, crea/aggiorna una issue settimanale e richiede la pubblicazione Pages. Le notifiche dipendono dalle impostazioni GitHub dell'utente; non sono previste email dirette o messaggi in questa chat. `GITHUB_TOKEN` deve avere contents, issues e pages in scrittura; nessun token personale o chiave feed è incorporato. Restrizioni organizzative o Pages possono impedire la pubblicazione: verificare Actions.

Esecuzione locale:

```sh
python -m pip install shapely==2.1.2 pyproj==3.7.2
python -m unittest discover -s tests -p test_weekly_research.py
python scripts/weekly_research.py
node tests/test_web.cjs
```

Il workflow non usa il precedente harvester: quel percorso applica distanze e dati di default non adatti a una validazione catastale e rigenera dossier. Le verifiche e l'anomalia Suzzara restano protette.
