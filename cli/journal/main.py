import typer
from typing import Optional, Annotated
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime

from .api_client import JournalAPIClient
from .location import get_current_location
from .chat import run_chat_session

app = typer.Typer(
    name="journal",
    help="Climbers Journal CLI — log your climbs, hikes, and adventures",
    no_args_is_help=True,
)
console = Console()


@app.command()
def add(
    quick: Annotated[bool, typer.Option("--quick", "-q", help="Quick single-line entry")] = False,
):
    """Add a new activity via an interactive chat session."""
    console.print("[dim]Detecting your location...[/dim]")
    location = get_current_location()
    location_context = location.as_context_string() if location else None

    if location_context:
        console.print(f"[dim]📍 {location_context}[/dim]")
    else:
        console.print("[dim]Could not detect location[/dim]")

    activity = run_chat_session(location_context=location_context)

    if activity:
        console.print(f"\n[bold green]✓ Activity saved[/bold green] (ID: {activity.get('id', '?')})")
    else:
        console.print("\n[dim]No activity saved.[/dim]")


@app.command(name="list")
def list_activities(
    activity_type: Annotated[Optional[str], typer.Option("--type", "-t", help="Filter by type")] = None,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Number of records")] = 20,
):
    """List recent activities."""
    client = JournalAPIClient()
    try:
        activities = client.list_activities(activity_type=activity_type, limit=limit)
    except Exception as e:
        console.print(f"[red]Could not fetch activities: {e}[/red]")
        raise typer.Exit(1)

    if not activities:
        console.print("[dim]No activities found.[/dim]")
        return

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="dim", width=5)
    table.add_column("Date", width=12)
    table.add_column("Type", width=14)
    table.add_column("Title")
    table.add_column("Grade", width=8)
    table.add_column("Area", width=18)

    for a in activities:
        date_str = a.get("date", "")[:10] if a.get("date") else ""
        atype = a.get("activity_type", "").replace("_", " ").title()
        table.add_row(
            str(a.get("id", "")),
            date_str,
            atype,
            a.get("title", ""),
            a.get("grade") or "",
            a.get("area") or a.get("location_name") or "",
        )

    console.print(table)


@app.command()
def show(activity_id: Annotated[int, typer.Argument(help="Activity ID")]):
    """Show details of an activity."""
    client = JournalAPIClient()
    try:
        activity = client.get_activity(activity_id)
    except Exception as e:
        console.print(f"[red]Activity not found: {e}[/red]")
        raise typer.Exit(1)

    from .chat import _format_activity
    from rich.panel import Panel
    from rich.markdown import Markdown
    console.print(Panel(
        Markdown(_format_activity(activity)),
        title=f"[bold]Activity #{activity_id}[/bold]",
    ))


if __name__ == "__main__":
    app()
