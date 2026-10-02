"""
Interfaccia a riga di comando (CLI) per SunPro — Geo-Intelligence & Solar Land Acquisition.
Supporta:
- list: elenco filtrato delle aree qualificate
- harvest: acquisizione live di nuovi lead reali dal feed di produzione B2B
- analyze: audit geospaziale, normativo (199/2021) ed energetico (PVGIS) su coordinate
- cabina: ricerca cabine primarie AT/MT e stazioni elettriche nel raggio
- pvgis: irraggiamento solare scientifico JRC European Commission
- report: generazione immediata Dossier Commerciale A4 in PDF
Autore: Nicola Valigi Engine System
"""

import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

from data.storage import init_db, get_all_leads, get_lead
from reports.generator import generate_pdf_dossier
from crawler.pvgis import get_pvgis_irradiance
from crawler.substation_finder import find_substations_around_coords
from crawler.geo_analyzer import analyze_site_location, geocode_city_name
from crawler.live_feed_harvester import harvest_and_qualify_solar_land, populate_database_with_live_leads
from build_full_platform import build_platform

console = Console()

def list_leads(regione=None, min_score=0.0):
    init_db()
    leads = get_all_leads(regione=regione if regione != "Tutte" else None, min_score=min_score)

    if not leads:
        console.print(f"[yellow]Nessun lead trovato con min_score >= {min_score} e regione={regione}.[/yellow]")
        return

    table = Table(title=f"☀️ SunPro — Aree Fotovoltaiche Qualificate (D.Lgs 199/2021) · {len(leads)} trovate")
    table.add_column("ID", style="cyan bold", no_wrap=True)
    table.add_column("Titolo / Comune", style="white")
    table.add_column("Regione", style="magenta")
    table.add_column("Superficie", justify="right", style="green")
    table.add_column("MWp", justify="right", style="bold green")
    table.add_column("Prezzo €/mq", justify="right", style="yellow")
    table.add_column("Cabina AT/MT", style="blue")
    table.add_column("Score", justify="right", style="bold")
    table.add_column("Rating", style="bold")

    for l in leads:
        score = float(l.get("score_totale", 0.0))
        color = "green" if score >= 90 else ("yellow" if score >= 75 else "white")
        table.add_row(
            l["id"],
            f"{l['title']}\n[dim]{l.get('comune','')} ({l.get('provincia','')})[/dim]",
            l.get("regione", ""),
            f"{l.get('superficie_ha', 0):.1f} ha",
            f"{l.get('mwp_stimati', 0):.1f}",
            f"{l.get('prezzo_mq_eur', 0):.2f} €",
            f"{str(l.get('cabina_piu_vicina', 'N/D'))[:22]}...\n[dim]({l.get('distanza_cabina_m', 0):,.0f} m)[/dim]",
            f"[{color}]{score:.1f}/100[/{color}]",
            f"[{color}]{l.get('rating_classe', 'QUALIFICATO')}[/{color}]"
        )

    console.print(table)

def run_harvest(max_leads: int = 15):
    console.print(f"[bold cyan]📡 Avvio Harvester Live: estrazione fino a {max_leads} nuovi siti reali...[/bold cyan]")
    candidates = harvest_and_qualify_solar_land(max_candidates=max_leads)
    populate_database_with_live_leads(candidates)
    console.print(f"[bold green]✓ Inseriti {len(candidates)} lead reali in SQLite.[/bold green]")
    console.print("[dim]Rigenerazione piattaforma web e Google Drive...[/dim]")
    build_platform()
    console.print("[bold green]✅ Database, PDF, Interfaccia 3D e Google Drive aggiornati al 100%![/bold green]")

def run_analyze(lat: float, lon: float, ha: float = 5.0, prezzo_mq: float = 8.5):
    console.print(f"[bold cyan]🔍 Analisi Geo-Intelligence per Coordinate: {lat:.5f}, {lon:.5f} ({ha:.2f} ha)[/bold cyan]")
    res = analyze_site_location(lat, lon, superficie_ha=ha, prezzo_mq=prezzo_mq)

    loc = res["localizzazione"]
    conf = res["conformita_d_lgs_199_2021"]
    rete = res["connessione_rete"]
    sol = res["resa_solare_pvgis"]
    dim = res["dimensionamento_impianto"]
    eco = res["modello_economico"]
    sc = res["scoring_sunpro"]

    p_color = "green" if sc["score_totale"] >= 80 else ("yellow" if sc["score_totale"] >= 65 else "red")

    summary_text = (
        f"[bold white]Localizzazione:[/bold white] {loc['comune']} ({loc['regione']}) — Cod. Belfiore: {loc['codice_belfiore']}\n"
        f"[bold white]Superficie Terreno:[/bold white] {res['superficie']['ha']} ha ({res['superficie']['mq']:,} mq)\n"
        f"[bold white]Conformità D.Lgs. 199/2021:[/bold white] [{'green' if conf['idoneo_ex_lege'] else 'red'}]{conf['motivo']}[/]\n"
        f"  • Distanza asse autostradale: {conf['distanza_autostrada_m']} m ({conf['nome_autostrada']})\n"
        f"  • Distanza zona industriale: {conf['distanza_industriale_m']} m\n\n"
        f"[bold white]Infrastruttura Rete Elettrica:[/bold white]\n"
        f"  • Cabina Primaria più vicina: [bold cyan]{rete['cabina_piu_vicina']}[/bold cyan] ({rete['tensione']})\n"
        f"  • Distanza di allaccio: [bold]{rete['distanza_m']} metri[/bold]\n"
        f"  • Stima CAPEX allaccio MT: [bold yellow]€ {rete['capex_allaccio_stimato_eur']:,.0f}[/bold yellow]\n\n"
        f"[bold white]Resa Solare Scientifica PVGIS (JRC):[/bold white]\n"
        f"  • Produzione specifica: [bold green]{sol['produzione_specifica_kwh_kwp']} kWh/kWp/anno[/bold green]\n"
        f"  • Irraggiamento globale: {sol['irraggiamento_globale_kwh_m2']} kWh/m² · Tilt ottimale: {sol['tilt_ottimale_gradi']}°\n\n"
        f"[bold white]Dimensionamento & Valutazione Finanziaria:[/bold white]\n"
        f"  • Potenza installabile stimata: [bold green]~{dim['potenza_stimata_mwp']} MWp[/bold green] (~{dim['produzione_annua_attesa_mwh']:,.0f} MWh/anno)\n"
        f"  • Valore d'acquisto target (@ {eco['prezzo_mq_eur']} €/mq): [bold yellow]€ {eco['valore_acquisto_stimato_eur']:,.0f}[/bold yellow]\n"
        f"  • Canone Diritto di Superficie: [bold green]€ {eco['canone_annuo_diritto_superficie_eur']:,.0f}/anno[/bold green] (30y: € {eco['totale_rendita_30_anni_eur']:,.0f})\n\n"
        f"[bold white]Punteggio Globale SunPro:[/bold white] [{p_color} bold]{sc['score_totale']:.1f}/100 — {sc['rating_classe']}[/{p_color} bold]"
    )

    console.print(Panel(summary_text, title="☀️ SunPro Geo-Intelligence Site Audit", border_style="cyan"))

def run_cabina(lat: float, lon: float, radius: int = 3000):
    console.print(f"[bold cyan]⚡ Ricerca Cabine Primarie AT/MT nel raggio di {radius} m da ({lat:.4f}, {lon:.4f})...[/bold cyan]")
    subs = find_substations_around_coords(lat, lon, radius_m=radius)
    if not subs:
        console.print(f"[yellow]Nessuna cabina trovata entro {radius} m.[/yellow]")
        return

    table = Table(title=f"Cabine Primarie & Stazioni Elettriche ({len(subs)} rilevate)")
    table.add_column("Nome Cabina / Stazione", style="cyan bold")
    table.add_column("Distanza", justify="right", style="bold green")
    table.add_column("Tensione", style="magenta")
    table.add_column("Operatore", style="white")
    table.add_column("Stima CAPEX Allaccio", justify="right", style="yellow")
    table.add_column("Fonte", style="dim")

    for s in subs:
        table.add_row(
            s["name"],
            f"{s['distanza_m']} m",
            s.get("livello_tensione", "MT"),
            s.get("operatore", "DSO"),
            f"€ {s.get('capex_allaccio_stimato_eur', 0):,.0f}",
            s.get("fonte", "")
        )
    console.print(table)

def run_pvgis(lat: float, lon: float):
    console.print(f"[bold cyan]☀️ Interrogazione PVGIS JRC (Commissione Europea) per ({lat:.4f}, {lon:.4f})...[/bold cyan]")
    data = get_pvgis_irradiance(lat, lon)
    table = Table(title="Dati Scientifici PVGIS (JRC EU v5.2)")
    table.add_column("Parametro", style="white bold")
    table.add_column("Valore", style="green bold")
    table.add_column("Note Tecniche", style="dim")

    table.add_row("Produzione Specifica (E_y)", f"{data['kwh_kwp_anno']} kWh/kWp/anno", "Energia netta per kWp considerando 14% perdite BOS")
    table.add_row("Irraggiamento Globale (H(i)_y)", f"{data['kwh_m2_anno']} kWh/m²/anno", "Radiazione incidente sul piano inclinato ottimale")
    table.add_row("Inclinazione Ottimale (Tilt)", f"{data['inclinazione_ottimale']}°", "Angolo zenitale per massima resa annuale")
    table.add_row("Fonte Dati", data["fonte"], "Modello SARAH2 / ERA5 JRC European Commission")
    console.print(table)

def make_report(lead_id: str):
    lead = get_lead(lead_id)
    if not lead:
        console.print(f"[red]Errore: Lead '{lead_id}' non trovato.[/red]")
        sys.exit(1)

    pdf_path = generate_pdf_dossier(lead)
    console.print(Panel(
        f"[green]Dossier Commerciale PDF generato con successo![/green]\n"
        f"File: [bold]{pdf_path}[/bold]\n"
        f"Lead: {lead['title']} ({lead['comune']})\n"
        f"Score: {lead['score_totale']}/100 ({lead.get('rating_classe')})",
        title="Dossier Origination Terreni"
    ))

def main():
    parser = argparse.ArgumentParser(description="SunPro Geo-Intelligence CLI (Nicola Valigi Engine System)")
    subparsers = parser.add_subparsers(dest="command")

    # list
    list_p = subparsers.add_parser("list", help="Elenca le aree qualificate")
    list_p.add_argument("--regione", type=str, default=None, help="Filtra per regione")
    list_p.add_argument("--min-score", type=float, default=0.0, help="Score minimo (0-100)")

    # harvest
    harv_p = subparsers.add_parser("harvest", help="Estrae nuovi lead reali dal feed di produzione B2B")
    harv_p.add_argument("--max", type=int, default=15, help="Numero massimo di lead da acquisire")

    # analyze
    ana_p = subparsers.add_parser("analyze", help="Analisi Geo-Intelligence completa di coordinate GPS")
    ana_p.add_argument("lat", type=float, help="Latitudine GPS (es. 45.4182)")
    ana_p.add_argument("lon", type=float, help="Longitudine GPS (es. 10.3845)")
    ana_p.add_argument("--ha", type=float, default=5.0, help="Superficie in ettari (default: 5.0)")
    ana_p.add_argument("--prezzo-mq", type=float, default=8.5, help="Prezzo target al mq (default: 8.5)")

    # cabina
    cab_p = subparsers.add_parser("cabina", help="Cerca cabine primarie AT/MT nel raggio di coordinate")
    cab_p.add_argument("lat", type=float, help="Latitudine GPS")
    cab_p.add_argument("lon", type=float, help="Longitudine GPS")
    cab_p.add_argument("--radius", type=int, default=3000, help="Raggio di ricerca in metri (default: 3000)")

    # pvgis
    pvg_p = subparsers.add_parser("pvgis", help="Interroga la resa solare PVGIS JRC")
    pvg_p.add_argument("lat", type=float, help="Latitudine GPS")
    pvg_p.add_argument("lon", type=float, help="Longitudine GPS")

    # report
    rep_p = subparsers.add_parser("report", help="Genera dossier PDF per una specifica area")
    rep_p.add_argument("lead_id", type=str, help="ID univoco del lead (es. LEAD-LOMB-001)")

    args = parser.parse_args()

    if args.command == "list":
        list_leads(regione=args.regione, min_score=args.min_score)
    elif args.command == "harvest":
        run_harvest(max_leads=args.max)
    elif args.command == "analyze":
        run_analyze(args.lat, args.lon, ha=args.ha, prezzo_mq=args.prezzo_mq)
    elif args.command == "cabina":
        run_cabina(args.lat, args.lon, radius=args.radius)
    elif args.command == "pvgis":
        run_pvgis(args.lat, args.lon)
    elif args.command == "report":
        make_report(args.lead_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
