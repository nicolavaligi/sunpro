"""
Google Antigravity SDK Agent per Solar Land Origination.
Agente autonomo equipaggiato con strumenti geospaziali, calcolo CAPEX/rendita e generazione dossier.
Autore: Nicola Valigi Engine System
"""

import os
import sys
import json
import asyncio
from typing import Optional, List, Dict, Any

from google.antigravity import Agent, LocalAgentConfig
from data.storage import get_all_leads, get_lead
from reports.generator import generate_pdf_dossier
from crawler.spatial_engine import calculate_energy_and_capex, query_overpass_features
from crawler.cadastral_resolver import estimate_belfiore
from scoring.scorer import calculate_site_score

# -------------------------------------------------------------
# DEFINIZIONE CUSTOM TOOLS PER L'AGENTE ANTIGRAVITY
# -------------------------------------------------------------

def list_solar_opportunities(regione: str = "Tutte", min_score: float = 60.0) -> str:
    """Restituisce le aree fotovoltaiche e siti idonei filtrati per regione e punteggio di idoneità.

    Args:
        regione: La regione italiana di interesse (es. 'Lombardia', 'Emilia-Romagna', 'Veneto', 'Tutte').
        min_score: Punteggio minimo da 0 a 100 (default 60).
    """
    leads = get_all_leads(regione=None if regione == "Tutte" else regione, min_score=min_score)
    if not leads:
        return f"Nessun sito fotovoltaico trovato per la regione '{regione}' con score >= {min_score}."

    summary = []
    for l in leads:
        summary.append(
            f"• [{l['id']}] {l['title']} | Comune: {l['comune']} ({l['provincia']}) | "
            f"Superficie: {l['superficie_ha']} ha (~{l['mwp_stimati']} MWp) | "
            f"Prezzo: {l['prezzo_mq_eur']} €/mq | Cabina: {l['cabina_piu_vicina']} ({l['distanza_cabina_m']} m) | "
            f"Score: {l['score_totale']}/100 ({l['rating_classe']})"
        )
    return f"Trovate {len(leads)} opportunità:\n" + "\n".join(summary)


def get_lead_full_details(lead_id: str) -> str:
    """Restituisce la scheda tecnica completa, i dati catastali e i contatti del proprietario di una particella.

    Args:
        lead_id: Identificativo del lead (es. 'LEAD-LOMB-001').
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
        f"Stato Commerciale: {lead['stato_commerciale']}\n"
        f"Score Totale: {lead['score_totale']}/100 ({lead['rating_classe']})\n"
    )
    return details


def generate_dossier_pdf_file(lead_id: str) -> str:
    """Genera fisicamente il file PDF del Dossier Commerciale (A4) per il team commerciale.

    Args:
        lead_id: L'identificativo del lead per cui generare il PDF.
    """
    lead = get_lead(lead_id)
    if not lead:
        return f"Errore: Lead '{lead_id}' non esistente."
    pdf_path = generate_pdf_dossier(lead)
    return f"Dossier PDF generato con successo: {pdf_path}"


def simulate_area_feasibility(
    superficie_ha: float,
    distanza_cabina_m: float,
    regione: str = "Lombardia",
    prezzo_mq: float = 8.5,
    tipologia: str = "EX_CAVA"
) -> str:
    """Simula in tempo reale l'idoneità tecnica, lo score e la fattibilità economica di una nuova area.

    Args:
        superficie_ha: Dimensione dell'area in ettari (es. 5.5).
        distanza_cabina_m: Distanza in metri dalla cabina primaria AT/MT (es. 750).
        regione: Regione italiana (es. 'Lombardia', 'Veneto', 'Toscana').
        prezzo_mq: Prezzo richiesto in euro al mq (es. 8.2).
        tipologia: Tipologia del sito ('EX_CAVA', 'DISCARICA_ESAURITA', 'BUFFER_INDUSTRIALE_350M', 'FASCIA_AUTOSTRADALE_300M').
    """
    superficie_mq = superficie_ha * 10_000
    mwp, mwh, capex = calculate_energy_and_capex(superficie_mq, distanza_cabina_m, regione)

    mock_lead = {
        "superficie_mq": superficie_mq,
        "prezzo_mq_eur": prezzo_mq,
        "distanza_cabina_m": distanza_cabina_m,
        "tipologia": tipologia,
        "regione": regione,
        "particella": "Simulazione"
    }
    score, dettagli, classe = calculate_site_score(mock_lead)

    res = (
        f"=== SIMULAZIONE FATTIBILITÀ SITO ===\n"
        f"Superficie: {superficie_ha:.2f} ha ({superficie_mq:,.0f} mq)\n"
        f"Potenza FV Installabile: ~{mwp:.2f} MWp\n"
        f"Produzione Stimata: ~{mwh:,.0f} MWh/anno\n"
        f"Stima CAPEX Allaccio Rete MT: ~{capex:,.0f} €\n"
        f"Valutazione Acquisto (@ {prezzo_mq} €/mq): {superficie_mq * prezzo_mq:,.0f} €\n"
        f"Canone Annuo Diritto Superficie: ~{superficie_ha * 3000:,.0f} €/anno\n"
        f"Punteggio di Idoneità: {score}/100 ({classe})\n"
        f"Dettagli Punteggio: {json.dumps(dettagli, ensure_ascii=False)}"
    )
    return res

# -------------------------------------------------------------
# SISTEMA AGENTE GOOGLE ANTIGRAVITY
# -------------------------------------------------------------

AGENT_SYSTEM_INSTRUCTIONS = """
Sei l'Assistente AI Senior di Origination Terreni Fotovoltaici di Nicola Valigi Engine System.
Operi come un esperto GIS, ingegnere energetico e analista M&A rinnovabili per il mercato italiano.

Le tue capacità:
1. Conosci la normativa sulle Aree Idonee (D.Lgs. 199/2021) in particolare i buffer da 350m da zone industriali, 300m da autostrade, e le priorità assolute per ex-cave e discariche bonificate.
2. Hai a disposizione strumenti (tools) per interrogare il database dei lead, simulare la fattibilità tecnica, calcolare i costi di allaccio alla cabina primaria (CAPEX) e generare dossier commerciali in PDF.
3. Rispondi in italiano con tono professionale, analitico e orientato al business.
"""

def create_agent_config(api_key: Optional[str] = None) -> LocalAgentConfig:
    """Configura l'agente Google Antigravity con i tool geospaziali e catastali."""
    tools = [
        list_solar_opportunities,
        get_lead_full_details,
        generate_dossier_pdf_file,
        simulate_area_feasibility
    ]
    kwargs = {
        "tools": tools,
        "system_instructions": AGENT_SYSTEM_INSTRUCTIONS
    }
    if api_key:
        kwargs["api_key"] = api_key
    return LocalAgentConfig(**kwargs)

async def run_agent_query(query: str, api_key: Optional[str] = None):
    """Esegue una query autonoma con l'agente Antigravity."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        print("\n[INFO] Chiave GEMINI_API_KEY non trovata nelle variabili d'ambiente.")
        print("Per abilitare le capacità generative e conversazionali avanzate di Gemini:")
        print("1. Ottieni una chiave gratuita su: https://aistudio.google.com/app/api-keys")
        print("2. Esegui: export GEMINI_API_KEY=\"tua_chiave\"\n")
        print("Esecuzione fallback deterministica locale dei tool:")
        # Fallback locale
        if "emilia" in query.lower() or "lombardia" in query.lower() or "aree" in query.lower():
            print(list_solar_opportunities(regione="Tutte", min_score=75.0))
        return

    config = create_agent_config(api_key=key)
    async with Agent(config=config) as agent:
        print(f"\nUser: {query}\nAntigravity Agent: ", end="", flush=True)
        response = await agent.chat(query)
        async for chunk in response:
            print(chunk, end="", flush=True)
        print("\n")

if __name__ == "__main__":
    prompt = "Quali sono le migliori opportunità fotovoltaiche censite con score >= 80 e vicine alle cabine AT/MT?"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    asyncio.run(run_agent_query(prompt))
