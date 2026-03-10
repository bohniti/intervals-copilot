from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from .api_client import JournalAPIClient

console = Console()


def run_chat_session(location_context: Optional[str] = None) -> Optional[dict]:
    """Run an interactive chat session with the LLM. Returns saved activity dict or None."""
    client = JournalAPIClient()
    messages = []

    console.print(Panel.fit(
        "[bold green]Climbers Journal[/bold green] — Chat Mode\n"
        "[dim]Describe your activity. Type 'quit' or press Ctrl+C to exit.[/dim]",
        border_style="green",
    ))

    if location_context:
        console.print(f"[dim]📍 Location: {location_context}[/dim]\n")

    initial_message = "I'll help you log an activity. What did you do today?"
    console.print(f"[bold cyan]Assistant:[/bold cyan] {initial_message}\n")

    while True:
        try:
            user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Chat cancelled.[/dim]")
            return None

        if user_input.strip().lower() in ("quit", "exit", "q"):
            console.print("[dim]Chat ended.[/dim]")
            return None

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat(messages=messages, location_context=location_context)
        except Exception as e:
            console.print(f"[red]Error communicating with backend: {e}[/red]")
            console.print("[dim]Make sure the backend is running: docker compose up -d[/dim]")
            return None

        reply = response.get("reply", "")
        pending_activity = response.get("pending_activity")
        needs_confirmation = response.get("needs_confirmation", False)

        messages.append({"role": "assistant", "content": reply})

        if reply:
            console.print(f"\n[bold cyan]Assistant:[/bold cyan] {reply}\n")

        if pending_activity and needs_confirmation:
            # Show the parsed details BEFORE saving anything
            console.print(Panel(
                _format_activity(pending_activity),
                title="[bold yellow]Proposed Activity — please review[/bold yellow]",
                border_style="yellow",
            ))
            confirm = Prompt.ask(
                "[bold]Save this activity?[/bold]",
                choices=["y", "n"],
                default="y",
            )
            if confirm == "y":
                # Only NOW do we actually save it
                try:
                    saved = client.create_activity(pending_activity)
                    console.print(
                        f"\n[bold green]✓ Saved![/bold green] "
                        f"Activity #{saved.get('id')}: {saved.get('title')}\n"
                    )
                    return saved
                except Exception as e:
                    console.print(f"[red]Failed to save: {e}[/red]")
                    return None
            else:
                console.print("[dim]Not saved. Tell me what to change and I'll update the proposal.[/dim]\n")
                # Continue the loop so the user can correct things

    return None


def _format_activity(activity: dict) -> str:
    lines = []
    if activity.get("title"):
        lines.append(f"**Title:** {activity['title']}")
    if activity.get("activity_type"):
        lines.append(f"**Type:** {activity['activity_type'].replace('_', ' ').title()}")
    if activity.get("date"):
        lines.append(f"**Date:** {activity['date'][:10]}")
    if activity.get("route_name"):
        lines.append(f"**Route:** {activity['route_name']}")
    if activity.get("grade"):
        sys_ = activity.get("grade_system", "")
        lines.append(f"**Grade:** {activity['grade']} ({sys_})" if sys_ else f"**Grade:** {activity['grade']}")
    if activity.get("climb_style"):
        lines.append(f"**Style:** {activity['climb_style'].title()}")
    if activity.get("pitches"):
        lines.append(f"**Pitches:** {activity['pitches']}")
    if activity.get("height_m"):
        lines.append(f"**Height:** {activity['height_m']} m")
    if activity.get("area"):
        lines.append(f"**Area:** {activity['area']}")
    if activity.get("location_name"):
        lines.append(f"**Location:** {activity['location_name']}")
    if activity.get("partner"):
        lines.append(f"**Partner:** {activity['partner']}")
    if activity.get("duration_minutes"):
        h, m = divmod(activity["duration_minutes"], 60)
        lines.append(f"**Duration:** {h}h {m}m" if h else f"**Duration:** {m}m")
    if activity.get("distance_km"):
        lines.append(f"**Distance:** {activity['distance_km']} km")
    if activity.get("elevation_gain_m"):
        lines.append(f"**Elevation gain:** {activity['elevation_gain_m']} m")
    if activity.get("notes"):
        lines.append(f"**Notes:** {activity['notes']}")
    return "\n".join(lines) if lines else "(no details)"
