"""
Modulo di persistenza SQLite per la gestione dei Lead e Aree Fotovoltaiche.
Autore: Nicola Valigi Engine System
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from config import DB_PATH, LEAD_STATUSES

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inizializza la tabella dei lead se non esiste."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                regione TEXT NOT NULL,
                provincia TEXT NOT NULL,
                comune TEXT NOT NULL,
                codice_belfiore TEXT,
                foglio TEXT,
                particella TEXT,
                lat REAL NOT NULL,
                lng REAL NOT NULL,
                superficie_mq REAL NOT NULL,
                superficie_ha REAL NOT NULL,
                prezzo_richiesto_eur REAL,
                prezzo_mq_eur REAL,
                tipologia TEXT NOT NULL,
                distanza_zona_industriale_m REAL,
                distanza_autostrada_m REAL,
                nome_autostrada TEXT,
                cabina_piu_vicina TEXT,
                distanza_cabina_m REAL,
                livello_tensione TEXT,
                mwp_stimati REAL,
                produzione_mwh_anno REAL,
                capex_allaccio_eur REAL,
                score_totale REAL NOT NULL,
                score_dettagli TEXT,
                rating_classe TEXT NOT NULL,
                proprietario_tipo TEXT,
                proprietario_nome TEXT,
                proprietario_piva TEXT,
                proprietario_pec TEXT,
                proprietario_telefono TEXT,
                fonte_origine TEXT,
                stato_commerciale TEXT NOT NULL DEFAULT 'DA_CONTATTARE',
                note_commerciali TEXT,
                destinazione_urbanistica TEXT,
                valore_agricolo_base_eur_mq REAL,
                valore_mercato_ordinario_eur_mq REAL,
                premio_trasformazione_pct REAL,
                status_acquistabilita TEXT DEFAULT 'ACQUISTABILE_BANCABILE',
                sintesi_perizia TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        # Migrazione dinamica per colonne di valutazione fondiaria e zoning
        for col, col_type in [
            ("destinazione_urbanistica", "TEXT"),
            ("valore_agricolo_base_eur_mq", "REAL"),
            ("valore_mercato_ordinario_eur_mq", "REAL"),
            ("premio_trasformazione_pct", "REAL"),
            ("status_acquistabilita", "TEXT"),
            ("sintesi_perizia", "TEXT"),
        ]:
            try:
                cursor.execute(f"ALTER TABLE leads ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass
        conn.commit()

def upsert_lead(lead: Dict[str, Any]):
    """Inserisce o aggiorna un lead nel database."""
    now = datetime.now().isoformat()
    score_dettagli_json = (
        json.dumps(lead.get("score_dettagli", {}))
        if isinstance(lead.get("score_dettagli"), dict)
        else lead.get("score_dettagli", "{}")
    )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leads (
                id, title, regione, provincia, comune, codice_belfiore, foglio, particella,
                lat, lng, superficie_mq, superficie_ha, prezzo_richiesto_eur, prezzo_mq_eur,
                tipologia, distanza_zona_industriale_m, distanza_autostrada_m, nome_autostrada,
                cabina_piu_vicina, distanza_cabina_m, livello_tensione, mwp_stimati,
                produzione_mwh_anno, capex_allaccio_eur, score_totale, score_dettagli,
                rating_classe, proprietario_tipo, proprietario_nome, proprietario_piva,
                proprietario_pec, proprietario_telefono, fonte_origine, stato_commerciale,
                note_commerciali, destinazione_urbanistica, valore_agricolo_base_eur_mq,
                valore_mercato_ordinario_eur_mq, premio_trasformazione_pct, status_acquistabilita,
                sintesi_perizia, created_at, updated_at
            ) VALUES (
                :id, :title, :regione, :provincia, :comune, :codice_belfiore, :foglio, :particella,
                :lat, :lng, :superficie_mq, :superficie_ha, :prezzo_richiesto_eur, :prezzo_mq_eur,
                :tipologia, :distanza_zona_industriale_m, :distanza_autostrada_m, :nome_autostrada,
                :cabina_piu_vicina, :distanza_cabina_m, :livello_tensione, :mwp_stimati,
                :produzione_mwh_anno, :capex_allaccio_eur, :score_totale, :score_dettagli,
                :rating_classe, :proprietario_tipo, :proprietario_nome, :proprietario_piva,
                :proprietario_pec, :proprietario_telefono, :fonte_origine, :stato_commerciale,
                :note_commerciali, :destinazione_urbanistica, :valore_agricolo_base_eur_mq,
                :valore_mercato_ordinario_eur_mq, :premio_trasformazione_pct, :status_acquistabilita,
                :sintesi_perizia, :created_at, :updated_at
            ) ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                regione = excluded.regione,
                provincia = excluded.provincia,
                comune = excluded.comune,
                codice_belfiore = excluded.codice_belfiore,
                foglio = excluded.foglio,
                particella = excluded.particella,
                lat = excluded.lat,
                lng = excluded.lng,
                superficie_mq = excluded.superficie_mq,
                superficie_ha = excluded.superficie_ha,
                prezzo_richiesto_eur = excluded.prezzo_richiesto_eur,
                prezzo_mq_eur = excluded.prezzo_mq_eur,
                tipologia = excluded.tipologia,
                distanza_zona_industriale_m = excluded.distanza_zona_industriale_m,
                distanza_autostrada_m = excluded.distanza_autostrada_m,
                nome_autostrada = excluded.nome_autostrada,
                cabina_piu_vicina = excluded.cabina_piu_vicina,
                distanza_cabina_m = excluded.distanza_cabina_m,
                livello_tensione = excluded.livello_tensione,
                mwp_stimati = excluded.mwp_stimati,
                produzione_mwh_anno = excluded.produzione_mwh_anno,
                capex_allaccio_eur = excluded.capex_allaccio_eur,
                score_totale = excluded.score_totale,
                score_dettagli = excluded.score_dettagli,
                rating_classe = excluded.rating_classe,
                proprietario_tipo = excluded.proprietario_tipo,
                proprietario_nome = excluded.proprietario_nome,
                proprietario_piva = excluded.proprietario_piva,
                proprietario_pec = excluded.proprietario_pec,
                proprietario_telefono = excluded.proprietario_telefono,
                fonte_origine = excluded.fonte_origine,
                stato_commerciale = excluded.stato_commerciale,
                note_commerciali = excluded.note_commerciali,
                destinazione_urbanistica = excluded.destinazione_urbanistica,
                valore_agricolo_base_eur_mq = excluded.valore_agricolo_base_eur_mq,
                valore_mercato_ordinario_eur_mq = excluded.valore_mercato_ordinario_eur_mq,
                premio_trasformazione_pct = excluded.premio_trasformazione_pct,
                status_acquistabilita = excluded.status_acquistabilita,
                sintesi_perizia = excluded.sintesi_perizia,
                updated_at = excluded.updated_at
        """, {
            "id": lead["id"],
            "title": lead["title"],
            "regione": lead["regione"],
            "provincia": lead["provincia"],
            "comune": lead["comune"],
            "codice_belfiore": lead.get("codice_belfiore", ""),
            "foglio": str(lead.get("foglio", "")),
            "particella": str(lead.get("particella", "")),
            "lat": float(lead["lat"]),
            "lng": float(lead["lng"]),
            "superficie_mq": float(lead["superficie_mq"]),
            "superficie_ha": round(float(lead["superficie_mq"]) / 10_000, 2),
            "prezzo_richiesto_eur": float(lead.get("prezzo_richiesto_eur") or 0),
            "prezzo_mq_eur": round(float(lead.get("prezzo_mq_eur") or 0), 2),
            "tipologia": lead["tipologia"],
            "distanza_zona_industriale_m": lead.get("distanza_zona_industriale_m"),
            "distanza_autostrada_m": lead.get("distanza_autostrada_m"),
            "nome_autostrada": lead.get("nome_autostrada", ""),
            "cabina_piu_vicina": lead.get("cabina_piu_vicina", ""),
            "distanza_cabina_m": float(lead.get("distanza_cabina_m") or 0),
            "livello_tensione": lead.get("livello_tensione", "MT 15kV / 20kV"),
            "mwp_stimati": round(float(lead.get("mwp_stimati") or 0), 2),
            "produzione_mwh_anno": round(float(lead.get("produzione_mwh_anno") or 0), 1),
            "capex_allaccio_eur": round(float(lead.get("capex_allaccio_eur") or 0), 0),
            "score_totale": round(float(lead["score_totale"]), 1),
            "score_dettagli": score_dettagli_json,
            "rating_classe": lead.get("rating_classe", "QUALIFICATO"),
            "proprietario_tipo": lead.get("proprietario_tipo", "PERSONA_GIURIDICA"),
            "proprietario_nome": lead.get("proprietario_nome", ""),
            "proprietario_piva": lead.get("proprietario_piva", ""),
            "proprietario_pec": lead.get("proprietario_pec", ""),
            "proprietario_telefono": lead.get("proprietario_telefono", ""),
            "fonte_origine": lead.get("fonte_origine", "OSM_OVERPASS"),
            "stato_commerciale": lead.get("stato_commerciale", "DA_CONTATTARE"),
            "note_commerciali": lead.get("note_commerciali", ""),
            "destinazione_urbanistica": lead.get("destinazione_urbanistica", "Zona E — Agricola"),
            "valore_agricolo_base_eur_mq": float(lead.get("valore_agricolo_base_eur_mq") or 0),
            "valore_mercato_ordinario_eur_mq": float(lead.get("valore_mercato_ordinario_eur_mq") or 0),
            "premio_trasformazione_pct": float(lead.get("premio_trasformazione_pct") or 0),
            "status_acquistabilita": lead.get("status_acquistabilita", "ACQUISTABILE_BANCABILE"),
            "sintesi_perizia": lead.get("sintesi_perizia", ""),
            "created_at": lead.get("created_at", now),
            "updated_at": now
        })
        conn.commit()

def get_lead(lead_id: str) -> Optional[Dict[str, Any]]:
    """Restituisce un singolo lead dato l'ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        if res.get("score_dettagli"):
            try:
                res["score_dettagli"] = json.loads(res["score_dettagli"])
            except Exception:
                pass
        return res

def get_all_leads(
    regione: Optional[str] = None,
    min_score: float = 0.0,
    stato_commerciale: Optional[str] = None,
    max_prezzo_mq: Optional[float] = None
) -> List[Dict[str, Any]]:
    """Restituisce la lista dei lead con filtri facoltativi."""
    query = "SELECT * FROM leads WHERE score_totale >= ?"
    params: List[Any] = [min_score]

    if regione and regione != "Tutte":
        query += " AND regione = ?"
        params.append(regione)

    if stato_commerciale and stato_commerciale != "Tutti":
        query += " AND stato_commerciale = ?"
        params.append(stato_commerciale)

    if max_prezzo_mq:
        query += " AND (prezzo_mq_eur <= ? OR prezzo_mq_eur IS NULL OR prezzo_mq_eur = 0)"
        params.append(max_prezzo_mq)

    query += " ORDER BY score_totale DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            if item.get("score_dettagli"):
                try:
                    item["score_dettagli"] = json.loads(item["score_dettagli"])
                except Exception:
                    pass
            result.append(item)
        return result

def update_status(lead_id: str, new_status: str, notes: Optional[str] = None):
    """Aggiorna lo stato commerciale e le note di un lead."""
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        if notes is not None:
            cursor.execute("""
                UPDATE leads
                SET stato_commerciale = ?, note_commerciali = ?, updated_at = ?
                WHERE id = ?
            """, (new_status, notes, now, lead_id))
        else:
            cursor.execute("""
                UPDATE leads
                SET stato_commerciale = ?, updated_at = ?
                WHERE id = ?
            """, (new_status, now, lead_id))
        conn.commit()

def get_leads_df(
    regione: Optional[str] = None,
    min_score: float = 0.0,
    stato_commerciale: Optional[str] = None
) -> pd.DataFrame:
    """Restituisce un pandas DataFrame pronto per l'analisi o visualizzazione."""
    leads = get_all_leads(regione=regione, min_score=min_score, stato_commerciale=stato_commerciale)
    if not leads:
        return pd.DataFrame()
    df = pd.DataFrame(leads)
    return df
