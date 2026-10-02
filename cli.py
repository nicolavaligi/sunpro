"""
Interfaccia a riga di comando (CLI) per Solar Land Acquisition Crawler.
Autore: Nicola Valigi Engine System
"""

import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from data.storage import init_db, get_all_leads, get_lead
from pipeline import sync_all_curated_leads
from reports.generator import generate_pdf_dossier

console = Console()

def list_leads(regione=None, min_score=0.0):
    init_db()
    leads = get_all_leads(regione=regione, min_score=min_score)

    if not leads:
        console.print("[yellow]Nessun lead trovato con i filtri specificati.[/yellow]")
        return

    table = Table(title=f"Aree Fotovoltaiche Qualificate (D.Lgs 199/2021) - {len(leads)} trovate")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Titolo / Comune", style="white")
    table.add_column("Regione", style="magenta")
    table.add_column("Superficie", justify="right", style="green")
    table.add_column("MWp", justify="right", style="bold green")
    table.add_column("Prezzo €/mq", justify="right", style="yellow")
    table.add_column("Cabina AT/MT", style="blue")
    table.add_column("Score", justify="right", style="bold red")
    table.add_column("Stato", style="white")

    for l in leads:
        score = l["score_totale"]
        color = "green" if score >= 75 else ("yellow" if score >= 60 else "white")
        table.add_row(
            l["id"],
            f"{l['title']}\n[dim]{l['comune']} ({l['provincia']})[/dim]",
            l["regione"],
            f"{l['superficie_ha']:.1f} ha",
            f"{l['mwp_stimati']:.1f}",
            f"{l['prezzo_mq_eur']:.2f} €",
            f"{l['cabina_piu_vicina'][:20]}...\n[dim]({l['distanza_cabina_m']:,.0f} m)[/dim]",
            f"[{color}]{score}/100[/{color}]",
            l["stato_commerciale"]
        )

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
    parser = argparse.ArgumentParser(description="Solar Land Acquisition CLI (Nicola Valigi Engine System)")
    subparsers = parser.add_subparsers(dest="command")

    # Command: list
    list_p = subparsers.add_parser("list", help="Elenca le aree qualificate")
    list_p.add_argument("--regione", type=str, default=None, help="Filtra per regione")
    list_p.add_argument("--min-score", type=float, default=0.0, help="Score minimo (0-100)")

    # Command: sync
    subparsers.add_parser("sync", help="Risincronizza il database SQLite con le aree curate")

    # Command: report
    rep_p = subparsers.add_parser("report", help="Genera dossier PDF per una specifica area")
    rep_p.add_argument("lead_id", type=str, help="ID univoco del lead (es. LEAD-LOMB-001)")

    args = parser.parse_args()

    if args.command == "list":
        list_leads(regione=args.regione, min_score=args.min_score)
    elif args.command == "sync":
        sync_all_curated_leads()
        console.print("[green]Database sincronizzato con successo![/green]")
    elif args.command == "report":
        make_report(args.lead_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
