"""
Google Antigravity SDK Agent per SunPro (Nicola Valigi Engine System).
Agente autonomo di Geo-Intelligence & Origination Terreni Fotovoltaici.
Funziona:
1. Con GEMINI_API_KEY: Esecuzione tramite Agent() del Google Antigravity SDK con Function Calling.
2. Senza GEMINI_API_KEY: Esecuzione autonoma tramite il Nicola Valigi Geo-Intelligence Engine (NLP deterministico locale ad alta precisione).
Autore: Nicola Valigi Engine System
"""

import os
import sys
import json
import re
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from data.storage import get_all_leads, get_lead
from reports.generator import generate_pdf_dossier
from crawler.spatial_engine import calculate_energy_and_capex
from crawler.cadastral_resolver import estimate_belfiore
from crawler.substation_finder import find_substations_around_coords
from crawler.pvgis import get_pvgis_irradiance
from crawler.geo_analyzer import analyze_site_location, geocode_city_name
from crawler.live_feed_harvester import harvest_and_qualify_solar_land, populate_database_with_live_leads
from build_full_platform import build_platform

console = Console()

# -------------------------------------------------------------
# 1. TOOLSET GEOSPAZIALE & ORIGINATION PER ANTIGRAVITY AGENT
# -------------------------------------------------------------

def list_solar_opportunities(regione: str = "Tutte", min_score: float = 60.0, max_cabina_dist_m: float = 99999.0) -> str:
    """Restituisce le aree fotovoltaiche e siti idonei filtrati per regione, score e distanza dalla cabina.

    Args:
        regione: La regione italiana di interesse (es. 'Lombardia', 'Emilia-Romagna', 'Veneto', 'Tutte').
        min_score: Punteggio minimo da 0 a 100 (default 60).
        max_cabina_dist_m: Distanza massima dalla cabina primaria AT/MT in metri (default nessun limite).
    """
    leads = get_all_leads(regione=None if regione == "Tutte" else regione, min_score=min_score)
    if max_cabina_dist_m < 99999.0:
        leads = [l for l in leads if float(l.get("distanza_cabina_m", 99999)) <= max_cabina_dist_m]

    if not leads:
        return f"Nessun sito fotovoltaico trovato per regione='{regione}', score >= {min_score}, cabina <= {max_cabina_dist_m}m."

    leads.sort(key=lambda x: (x["score_totale"], -float(x.get("distanza_cabina_m", 9999))), reverse=True)
    summary = []
    for l in leads:
        summary.append(
            f"• [{l['id']}] {l['title']} | Comune: {l['comune']} ({l['provincia']}) | "
            f"Superficie: {l['superficie_ha']} ha (~{l['mwp_stimati']} MWp) | "
            f"Prezzo: {l['prezzo_mq_eur']} €/mq | Cabina: {l['cabina_piu_vicina']} ({l['distanza_cabina_m']:,.0f} m) | "
            f"Score: {l['score_totale']}/100 ({l['rating_classe']})"
        )
    return f"Trovate {len(leads)} opportunità qualificate:\n" + "\n".join(summary)


def get_lead_full_details(lead_id: str) -> str:
    """Restituisce la scheda tecnica completa, i dati catastali e i contatti del proprietario di una particella.

    Args:
        lead_id: Identificativo del lead (es. 'LEAD-LOMB-001' o 'FV-LOM-W1306185882').
    """
    lead = get_lead(lead_id)
    if not lead:
        return f"Errore: Nessun lead trovato con ID '{lead_id}'."

    details = (
        f"=== SCHEDA SITO: {lead['title']} (ID: {lead['id']}) ===\n"
        f"Localizzazione: {lead['comune']} ({lead['provincia']}, {lead['regione']}) | Belfiore: {lead.get('codice_belfiore')}\n"
        f"Catasto: Foglio {lead.get('foglio')} - Particelle {lead.get('particella')}\n"
        f"Coordinate GPS: {lead['lat']}, {lead['lng']}\n"
        f"Tipologia D.Lgs 199/21: {lead['tipologia']}\n"
        f"Superficie: {lead['superficie_ha']} ha ({lead['superficie_mq']:,.0f} mq)\n"
        f"Potenza Attesa: ~{lead.get('mwp_stimati')} MWp | Produzione: {lead.get('produzione_mwh_anno'):,.0f} MWh/anno\n"
        f"Cabina Primaria AT/MT: {lead['cabina_piu_vicina']} a {lead['distanza_cabina_m']} metri (CAPEX allaccio ~{lead.get('capex_allaccio_eur'):,.0f} €)\n"
        f"Valutazione Economica: {lead['prezzo_mq_eur']} €/mq (Totale acquisto: {lead['prezzo_richiesto_eur']:,.0f} €)\n"
        f"Diritto di Superficie 30y: ~{lead['superficie_ha']*3000:,.0f} €/anno\n"
        f"Proprietario: {lead['proprietario_nome']} ({lead['proprietario_tipo']})\n"
        f"PEC / Contatto: {lead.get('proprietario_pec') or lead.get('proprietario_telefono') or 'Sister'}\n"
        f"Score Totale: {lead['score_totale']}/100 ({lead['rating_classe']})\n"
    )
    return details


def generate_dossier_pdf_file(lead_id: str) -> str:
    """Genera fisicamente il file PDF del Dossier Commerciale (A4) per il sales rep.

    Args:
        lead_id: L'identificativo del lead per cui generare il PDF.
    """
    lead = get_lead(lead_id)
    if not lead:
        return f"Errore: Lead '{lead_id}' non esistente."
    pdf_path = generate_pdf_dossier(lead)
    return f"Dossier Commerciale PDF generato con successo: {pdf_path}"


def analyze_site_location_tool(lat: float, lon: float, ha: float = 5.0, prezzo_mq: float = 8.5) -> str:
    """Esegue un audit completo di Geo-Intelligence su coordinate GPS (PVGIS, Cabina AT/MT, D.Lgs 199/2021).

    Args:
        lat: Latitudine del terreno.
        lon: Longitudine del terreno.
        ha: Superficie in ettari (default 5.0).
        prezzo_mq: Prezzo target in euro/mq (default 8.5).
    """
    res = analyze_site_location(lat, lon, superficie_ha=ha, prezzo_mq=prezzo_mq)
    return json.dumps(res, indent=2, ensure_ascii=False)


def pvgis_lookup_tool(location_or_coords: str) -> str:
    """Interroga i dati scientifici di irraggiamento solare PVGIS (Commissione Europea JRC) per una città o coordinate.

    Args:
        location_or_coords: Nome comune (es. 'Faenza') o coppia 'lat, lon' (es. '44.28, 11.88').
    """
    lat, lon, label = None, None, location_or_coords
    # Verifica se sono coordinate
    m = re.search(r'([0-9]+\.[0-9]+)[\s,]+([0-9]+\.[0-9]+)', location_or_coords)
    if m:
        lat, lon = float(m.group(1)), float(m.group(2))
        label = f"{lat:.4f}, {lon:.4f}"
    else:
        geo = geocode_city_name(location_or_coords)
        if geo:
            lat, lon, label = geo[0], geo[1], geo[2]

    if lat is None or lon is None:
        return f"Impossibile geocodificare '{location_or_coords}'. Specificare coordinate lat/lng o un comune italiano valido."

    data = get_pvgis_irradiance(lat, lon)
    return (
        f"=== DATI SCIENTIFICI PVGIS (JRC COMMISSIONE EUROPEA) PER {label.upper()} ===\n"
        f"Coordinate: {lat:.4f}, {lon:.4f}\n"
        f"Produzione Specifica (E_y): {data['kwh_kwp_anno']} kWh/kWp/anno\n"
        f"Irraggiamento Globale (H(i)_y): {data['kwh_m2_anno']} kWh/m²\n"
        f"Inclinazione Ottimale Moduli (Tilt): {data['inclinazione_ottimale']}°\n"
        f"Fonte Ufficiale: {data['fonte']}"
    )


def find_substations_tool(lat: float, lon: float, radius_m: int = 3000) -> str:
    """Cerca le cabine primarie AT/MT e stazioni elettriche Terna/Enel entro un raggio specificato.

    Args:
        lat: Latitudine.
        lon: Longitudine.
        radius_m: Raggio di ricerca in metri (default 3000).
    """
    subs = find_substations_around_coords(lat, lon, radius_m=radius_m)
    if not subs:
        return f"Nessuna cabina primaria trovata entro {radius_m} metri da ({lat}, {lon})."
    lines = []
    for s in subs:
        lines.append(f"• {s['name']} | Distanza: {s['distanza_m']} m | Tensione: {s.get('livello_tensione')} | CAPEX: € {s.get('capex_allaccio_stimato_eur', 0):,.0f} | Operatore: {s.get('operatore')}")
    return f"Trovate {len(subs)} cabine/stazioni nel raggio di {radius_m}m:\n" + "\n".join(lines)


def harvest_live_feed_tool(max_leads: int = 15) -> str:
    """Interroga il feed di produzione B2B su Railway, acquisisce nuovi siti reali e aggiorna SQLite e la piattaforma.

    Args:
        max_leads: Numero massimo di nuovi lead qualificati da importare.
    """
    candidates = harvest_and_qualify_solar_land(max_candidates=max_leads)
    populate_database_with_live_leads(candidates)
    build_platform()
    return f"Acquisizione completata con successo! Inseriti {len(candidates)} lead reali qualificati. Piattaforma e Google Drive sincronizzati."


# -------------------------------------------------------------
# 2. MOTORE DETERMINISTICO AD ALTA PRECISIONE (Senza Gemini API Key)
# -------------------------------------------------------------

def run_deterministic_engine(prompt: str):
    """Esegue la richiesta interpretando l'intento dell'utente tramite il Nicola Valigi Geo-Intelligence Engine."""
    console.print(Panel(
        f"[bold white]{prompt}[/bold white]\n[dim]Modalità: Nicola Valigi Engine System (Local Geo-Intelligence)[/dim]",
        title="🤖 SunPro AI Assistant",
        border_style="green"
    ))

    p_lower = prompt.lower()

    # 1. Lead / Top Lead con filtri regione o cabina
    if any(k in p_lower for k in ["top lead", "lead", "opportunit", "migliori", "trova"]):
        reg = "Tutte"
        for r in ["lombardia", "veneto", "emilia-romagna", "piemonte", "toscana", "umbria", "marche"]:
            if r in p_lower:
                reg = r.title()
                break

        min_s = 75.0
        m_dist = 99999.0
        m_cab = re.search(r'(?:cabina|distanza|sotto|entro|meno di)\s*([0-9]+)\s*m', p_lower)
        if m_cab:
            m_dist = float(m_cab.group(1))

        res = list_solar_opportunities(regione=reg, min_score=min_s, max_cabina_dist_m=m_dist)
        console.print(Panel(res, title=f"📋 Risultati Filtro: Regione={reg} | Cabina <={m_dist if m_dist < 99999 else 'Tutte'}m", border_style="cyan"))
        return

    # 2. Analisi sito su coordinate
    if "analizza" in p_lower or "coordinate" in p_lower or "sito a" in p_lower:
        m_coords = re.search(r'([0-9]+\.[0-9]+)[\s,]+([0-9]+\.[0-9]+)', prompt)
        if m_coords:
            lat = float(m_coords.group(1))
            lon = float(m_coords.group(2))
            ha = 5.0
            m_ha = re.search(r'([0-9]+\.?[0-9]*)\s*ha', p_lower)
            if m_ha:
                ha = float(m_ha.group(1))

            console.print(f"[bold cyan]🔍 Analisi Geo-Intelligence in corso per ({lat}, {lon}) con superficie {ha} ha...[/bold cyan]")
            audit = analyze_site_location(lat, lon, superficie_ha=ha)
            
            loc = audit["localizzazione"]
            conf = audit["conformita_d_lgs_199_2021"]
            rete = audit["connessione_rete"]
            sol = audit["resa_solare_pvgis"]
            dim = audit["dimensionamento_impianto"]
            eco = audit["modello_economico"]
            sc = audit["scoring_sunpro"]

            rep = (
                f"[bold white]Comune & Catasto:[/bold white] {loc['comune']} ({loc['regione']}) — Belfiore: {loc['codice_belfiore']}\n"
                f"[bold white]Superficie:[/bold white] {audit['superficie']['ha']} ha ({audit['superficie']['mq']:,} mq)\n"
                f"[bold white]Conformità D.Lgs. 199/2021:[/bold white] [{'green' if conf['idoneo_ex_lege'] else 'yellow'}]{conf['motivo']}[/]\n"
                f"  • Distanza asse autostradale: {conf['distanza_autostrada_m']} m ({conf['nome_autostrada']})\n"
                f"[bold white]Connessione Rete:[/bold white] {rete['cabina_piu_vicina']} ({rete['tensione']}) a [bold cyan]{rete['distanza_m']} m[/bold cyan] (CAPEX allaccio: € {rete['capex_allaccio_stimato_eur']:,.0f})\n"
                f"[bold white]Resa Scientifica PVGIS:[/bold white] [bold green]{sol['produzione_specifica_kwh_kwp']} kWh/kWp/anno[/bold green] ({sol['irraggiamento_globale_kwh_m2']} kWh/m² · Tilt {sol['tilt_ottimale_gradi']}°)\n"
                f"[bold white]Dimensionamento Atteso:[/bold white] [bold green]~{dim['potenza_stimata_mwp']} MWp[/bold green] (~{dim['produzione_annua_attesa_mwh']:,.0f} MWh/anno)\n"
                f"[bold white]Modello Finanziario:[/bold white] Acquisto target: € {eco['valore_acquisto_stimato_eur']:,.0f} | Canone Diritto Superficie: € {eco['canone_annuo_diritto_superficie_eur']:,.0f}/anno\n"
                f"[bold white]Score Finale SunPro:[/bold white] [bold green]{sc['score_totale']:.1f}/100 — {sc['rating_classe']}[/bold green]"
            )
            console.print(Panel(rep, title="☀️ Report Audit Geo-Intelligence SunPro", border_style="cyan"))
            return

    # 3. Harvest live
    if "harvest" in p_lower or "aggiorna" in p_lower:
        console.print("[bold cyan]📡 Esecuzione Harvest Live dal Feed B2B su Railway...[/bold cyan]")
        res = harvest_live_feed_tool(max_leads=15)
        console.print(Panel(res, title="✅ Harvest Live Completato", border_style="green"))
        return

    # 4. PVGIS Irraggiamento
    if "pvgis" in p_lower or "irraggiamento" in p_lower or "radiazione" in p_lower or "resa solare" in p_lower:
        loc = prompt.replace("Irraggiamento PVGIS a", "").replace("Irraggiamento PVGIS", "").replace("irraggiamento a", "").strip(" :?\"'")
        if not loc:
            loc = "Faenza"
        res = pvgis_lookup_tool(loc)
        console.print(Panel(res, title="☀️ Dati PVGIS Joint Research Centre", border_style="yellow"))
        return

    # 5. Cabine AT/MT
    if "cabina" in p_lower or "sottostazione" in p_lower:
        m_coords = re.search(r'([0-9]+\.[0-9]+)[\s,]+([0-9]+\.[0-9]+)', prompt)
        if m_coords:
            lat = float(m_coords.group(1))
            lon = float(m_coords.group(2))
            res = find_substations_tool(lat, lon, radius_m=3500)
            console.print(Panel(res, title="⚡ Ricerca Cabine Primarie AT/MT", border_style="cyan"))
            return

    # Fallback generale: elenca le top opportunità
    console.print(Panel(list_solar_opportunities(regione="Tutte", min_score=80.0), title="☀️ Top Opportunità SunPro Censite", border_style="green"))


# -------------------------------------------------------------
# 3. ESECUZIONE AGENTE GOOGLE ANTIGRAVITY (Con Gemini API Key)
# -------------------------------------------------------------

AGENT_SYSTEM_INSTRUCTIONS = """
Sei l'Assistente AI Senior di Origination Terreni Fotovoltaici di Nicola Valigi Engine System.
Operi come un esperto GIS, ingegnere energetico e analista M&A rinnovabili per il mercato italiano.

Le tue capacità e strumenti:
1. list_solar_opportunities: interroga le aree fotovoltaiche e siti idonei filtrati per regione, score e vicinanza alla cabina.
2. analyze_site_location_tool: esegue l'audit completo di Geo-Intelligence su coordinate GPS (PVGIS, Cabina AT/MT, D.Lgs 199/2021, MWp, CAPEX).
3. pvgis_lookup_tool: interroga l'irraggiamento scientifico ufficiale PVGIS della Commissione Europea JRC.
4. find_substations_tool: cerca le cabine primarie AT/MT e stazioni elettriche Terna/Enel nel raggio.
5. harvest_live_feed_tool: acquisisce in tempo reale nuovi siti reali dal feed B2B su Railway.
6. generate_dossier_pdf_file: compila ed esporta il dossier commerciale A4 in PDF.

Rispondi sempre in italiano, con taglio esecutivo, dati numerici precisi e tono professionale orientato al risultato.
"""

def create_antigravity_agent(api_key: str):
    from google.antigravity import Agent, LocalAgentConfig
    tools = [
        list_solar_opportunities,
        get_lead_full_details,
        generate_dossier_pdf_file,
        analyze_site_location_tool,
        pvgis_lookup_tool,
        find_substations_tool,
        harvest_live_feed_tool
    ]
    config = LocalAgentConfig(
        tools=tools,
        system_instructions=AGENT_SYSTEM_INSTRUCTIONS,
        api_key=api_key
    )
    return Agent(config=config)

async def run_agent_query(query: str):
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key:
        # Esecuzione Engine deterministico avanzato di Nicola Valigi
        run_deterministic_engine(query)
        return

    # Esecuzione Google Antigravity Agent
    console.print(Panel(
        f"[bold white]{query}[/bold white]\n[dim]Modalità: Google Antigravity SDK Agent (Active GEMINI_API_KEY)[/dim]",
        title="🤖 SunPro Antigravity Agent",
        border_style="cyan"
    ))
    try:
        agent = create_antigravity_agent(gemini_key)
        async with agent:
            response = await agent.chat(query)
            console.print("[bold green]Antigravity Agent:[/bold green] ", end="")
            async for chunk in response:
                print(chunk, end="", flush=True)
            print("\n")
    except Exception as e:
        console.print(f"[yellow]Nota: Antigravity SDK ha riscontrato '{e}'. Esecuzione fallback su Engine Locale:[/yellow]")
        run_deterministic_engine(query)

if __name__ == "__main__":
    prompt = "Top lead Lombardia con cabina sotto 800 m"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    asyncio.run(run_agent_query(prompt))
