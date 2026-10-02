"""
Modulo per il Reperimento Dati Proprietari e Lead Enrichment Commerciale.
Supporta persone giuridiche, curatele fallimentari e persone fisiche.
Autore: Nicola Valigi Engine System
"""

from typing import Dict, Any

def enrich_owner_profile(lead: Dict[str, Any]) -> Dict[str, Any]:
    """Arricchisce i dati del proprietario con canali di contatto e modalità di visura."""
    prop_tipo = lead.get("proprietario_tipo", "PERSONA_GIURIDICA")
    nome = lead.get("proprietario_nome", "Proprietà da censire")
    pec = lead.get("proprietario_pec", "")
    piva = lead.get("proprietario_piva", "")

    canale_contatto = "Telefono / Visita in loco"
    canale_ufficiale = ""

    if prop_tipo == "PERSONA_GIURIDICA":
        canale_ufficiale = f"PEC Ufficiale Registro Imprese: {pec}" if pec else "Visura Camerale Telemaco su P.IVA"
        canale_contatto = f"PEC: {pec} | Tel: {lead.get('proprietario_telefono', 'N/D')}"
    elif prop_tipo == "CURATELA_FALLIMENTARE":
        canale_ufficiale = f"PEC Curatore Fallimentare: {pec}"
        canale_contatto = f"PEC Procedura: {pec}"
    else:
        canale_ufficiale = "Visura Catastale per Immobile su Agenzia delle Entrate (Sister)"
        canale_contatto = f"Contatto diretto: {lead.get('proprietario_telefono', 'Non disponibile')}"

    return {
        "proprietario_nome": nome,
        "proprietario_tipo": prop_tipo,
        "proprietario_piva": piva,
        "proprietario_pec": pec,
        "canale_ufficiale": canale_ufficiale,
        "canale_contatto": canale_contatto
    }

def generate_commercial_pitch(lead: Dict[str, Any]) -> Dict[str, str]:
    """Genera lo script e il pitch commerciale su misura per il commerciale/agente."""
    nome = lead.get("proprietario_nome", "Gentile Proprietà")
    comune = lead.get("comune", "del comune")
    ha = lead.get("superficie_ha", 5.0)
    mq = lead.get("superficie_mq", 50000)
    tipo = lead.get("tipologia", "area")
    prezzo_target = lead.get("prezzo_richiesto_eur", mq * 8.5)
    canone_annuo = round(ha * 3000, 0)
    trentennale = round(canone_annuo * 30, 0)

    # Adattamento tipologia per il dialogo
    tipo_desc = "la vostra ex cava dismessa" if "CAVA" in tipo else (
        "la vostra area in zona produttiva" if "INDUSTRIALE" in tipo else "il vostro compendio immobiliare"
    )

    pitch_telefonico = f"""
"Buongiorno, chiamo per conto dello Sviluppo Territoriale Rinnovabili. Abbiamo mappato {tipo_desc} situata a {comune} (Foglio {lead.get('foglio')}, P.lla {lead.get('particella')}) come area prioritaria per un investimento green fotovoltaico conforme alle direttive nazionali sulle Aree Idonee.

Desideriamo sottoporvi una duplice proposta finanziaria concreta:
1. ACQUISTO IMMEDIATO con rogito notarile: valorizzazione stimata di circa {prezzo_target:,.0f} € ({lead.get('prezzo_mq_eur', 8.5):.1f} €/mq interamente liquidati).
2. DIRITTO DI SUPERFICIE 30 ANNI: rendita garantita per la proprietà di circa {canone_annuo:,.0f} € all'anno indicizzati ISTAT (oltre {trentennale:,.0f} € complessivi), mantenendo la titolarità del bene e senza alcun costo o onere a vostro carico.

Possiamo inviarvi via PEC o concordare un breve incontro per illustrarvi il piano preliminare?"
    """.strip()

    obiezioni = """
• Se obiettano: "L'area ha vincoli o è da bonificare" -> Risposta: "La normativa D.Lgs. 199/2021 favorisce specificamente il recupero di cave e siti degradati, esentando da iter ordinari complessi. I costi di progettazione e le verifiche ambientali sono al 100% a nostro carico."
• Se obiettano: "Preferisco affittare che vendere" -> Risposta: "Possiamo procedere con Diritto di Superficie trentennale con fideiussione bancaria di primario istituto a garanzia del canone e dello smaltimento finale."
• Se chiedono: "Quanto tempo serve?" -> Risposta: "Sottoscriviamo una Lettera d'Intenti (LOI) non vincolante con indennizzo d'opzione entro 30 giorni."
    """.strip()

    return {
        "pitch_telefonico": pitch_telefonico,
        "obiezioni_e_risposte": obiezioni
    }
