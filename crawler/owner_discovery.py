"""
Modulo per la Validazione Rigorosa Anagrafica/P.IVA (Algoritmo Ufficiale Agenzia Entrate)
e Lead Enrichment Commerciale per l'acquisizione di terreni fotovoltaici.
Autore: Nicola Valigi (Houdinick) — SunPro Engine System
"""

import re
from typing import Any, Dict


def validate_italian_piva(piva: str) -> bool:
    """
    Valida rigorosamente una Partita IVA italiana a 11 cifre secondo l'algoritmo ufficiale
    pari/dispari (Luhn Modulo 10 — D.P.R. 633/1972 / Agenzia delle Entrate).
    Blocca qualsiasi P.IVA segnaposto, con cifre ripetute o con cifra di controllo errata.
    """
    if not piva:
        return False
    clean = re.sub(r"\s+", "", str(piva))
    if clean.upper().startswith("IT"):
        clean = clean[2:]
    if len(clean) != 11 or not clean.isdigit():
        return False
    if clean == "00000000000" or len(set(clean)) == 1:
        return False

    # Le prime 7 cifre sono il numero di matricola, le cifre 8-10 sono il codice ufficio provinciale (001-100, 120, 121, 888, 999)
    ufficio = int(clean[7:10])
    if ufficio == 0:
        return False

    somma_dispari = sum(int(clean[i]) for i in range(0, 10, 2))
    somma_pari = 0
    for i in range(1, 10, 2):
        doppio = int(clean[i]) * 2
        if doppio > 9:
            doppio -= 9
        somma_pari += doppio

    totale = somma_dispari + somma_pari
    check_atteso = (10 - (totale % 10)) % 10
    return int(clean[10]) == check_atteso


def sanitize_owner_fields(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Garantisce che nessuna P.IVA non conforme al codice di controllo o anagrafica
    segnaposto non verificata in visura venga mantenuta nel record.
    """
    piva = str(lead.get("proprietario_piva") or "").strip()
    if piva and not validate_italian_piva(piva):
        lead["proprietario_piva"] = ""
        lead["contatto_verificato"] = False

    if not lead.get("contatto_verificato"):
        lead["proprietario_piva"] = ""
        lead["proprietario_pec"] = ""
        lead["proprietario_telefono"] = ""
    return lead


def enrich_owner_profile(lead: Dict[str, Any]) -> Dict[str, Any]:
    """Arricchisce i dati del proprietario indicando la procedura di visura su mappale WMS verificato."""
    sanitize_owner_fields(lead)
    prop_tipo = lead.get("proprietario_tipo") or "AZIENDA_AGRICOLA / PROPRIETÀ FONDIARIA"
    belf = lead.get("codice_belfiore") or "N/D"
    fg = lead.get("foglio") or "N/D"
    part = lead.get("particella") or "N/D"

    if lead.get("contatto_verificato") and lead.get("proprietario_nome"):
        nome = lead["proprietario_nome"]
        piva = lead.get("proprietario_piva", "")
        pec = lead.get("proprietario_pec", "")
        canale_ufficiale = f"PEC Verificata Registro Imprese: {pec}" if pec else "Visura Catastale Ufficiale"
        canale_contatto = f"PEC: {pec} | Tel: {lead.get('proprietario_telefono', 'N/D')}"
    else:
        nome = "Acquisibile tramite Visura Catastale Sister (Mappale WMS Verificato)"
        piva = "Richiede Visura Catastale su Sister (~0,90 €)"
        pec = "Estrarre da INI-PEC / Telemaco post-visura catastale"
        canale_ufficiale = f"Visura Catastale per Immobile su Sister -> Comune Cod. {belf}, Fg. {fg}, Part. {part}"
        canale_contatto = f"1) Visura Sister su Fg. {fg} Part. {part} ({belf}) -> 2) Ricerca C.F./P.IVA su Registro Imprese"

    return {
        "proprietario_nome": nome,
        "proprietario_tipo": prop_tipo,
        "proprietario_piva": piva,
        "proprietario_pec": pec,
        "canale_ufficiale": canale_ufficiale,
        "canale_contatto": canale_contatto
    }


def generate_commercial_pitch(lead: Dict[str, Any]) -> Dict[str, str]:
    """Genera lo script e il pitch commerciale post-visura su mappale catastale WMS."""
    comune = lead.get("comune", "del comune")
    belf = lead.get("codice_belfiore") or "N/D"
    fg = lead.get("foglio") or "N/D"
    part = lead.get("particella") or "N/D"
    ha = float(lead.get("superficie_ha", 5.0))
    mq = float(lead.get("superficie_mq", 50000))
    tipo = lead.get("tipologia", "area")
    prezzo_mq = float(lead.get("prezzo_mq_eur", 7.80))
    prezzo_target = float(lead.get("prezzo_richiesto_eur", mq * prezzo_mq))
    vam_mq = float(lead.get("valore_agricolo_base_eur_mq", 5.20))
    canone_annuo = round(ha * 3000, 0)
    trentennale = round(canone_annuo * 30, 0)

    tipo_desc = "la vostra ex cava dismessa" if "CAVA" in tipo else (
        "il vostro terreno in fascia infrastrutturale" if "AUTOSTRAD" in tipo else "il vostro compendio agricolo a campo aperto"
    )

    rif_cat = f"Comune di {comune} (Cod. Belfiore {belf}), Foglio {fg}, Particella/e {part}" if fg != "N/D" and fg != "" else f"Comune di {comune} (Cod. Belfiore {belf})"

    pitch_telefonico = f"""
"Buongiorno, chiamo per conto dello Sviluppo Territoriale Rinnovabili (SunPro). Abbiamo individuato sulla cartografia catastale WMS dell'Agenzia delle Entrate {tipo_desc} sito in {rif_cat} (Coordinate GPS: {lead.get('lat', 0):.5f}, {lead.get('lng', 0):.5f}), di circa {ha:.1f} ettari, idoneo ex lege ai sensi del D.Lgs. 199/2021.

Desideriamo sottoporvi una duplice proposta finanziaria concreta:
1. ACQUISTO IMMEDIATO con rogito notarile: offerta target fino a {prezzo_target:,.0f} € ({prezzo_mq:.2f} €/mq, a fronte di un valore agricolo medio VAM di zona di {vam_mq:.2f} €/mq, entro il tetto di sostenibilità ≤ 8,00 €/mq).
2. DIRITTO DI SUPERFICIE 30 ANNI: rendita garantita di circa {canone_annuo:,.0f} €/anno indicizzati ISTAT ({trentennale:,.0f} € complessivi), mantenendo la nuda proprietà del fondo.

Possiamo concordare un breve incontro o inviarvi la Lettera d'Intenti (LOI) non vincolante?"
    """.strip()

    obiezioni = """
• Verifica preventiva effettuata: Mappale (Comune, Codice Belfiore, Foglio e Particella) già riscontrato gratuitamente tramite Servizio Cartografico WMS Agenzia delle Entrate e sovrapposto a ortofoto e vincoli OSM (elettrodotti, ferrovia AV, idrografia).
• Procedura pre-contatto: Eseguire Visura Catastale per Immobile su Sister usando Codice Belfiore + Foglio + Particella per estrarre l'intestatario reale e verificare la quota di proprietà.
• Se il proprietario chiede garanzie: Diritto di Superficie trentennale assistito da fideiussione bancaria a prima richiesta per canone e decommissioning finale.
    """.strip()

    return {
        "pitch_telefonico": pitch_telefonico,
        "obiezioni_e_risposte": obiezioni
    }
