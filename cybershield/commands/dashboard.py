# cybershield/commands/dashboard.py
import click
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


@click.command()
@click.option('--no-browser', is_flag=True, help='Do not auto-open browser')
def dashboard(no_browser):
    """
    Start the real-time dashboard server.
    
    Opens a web UI at http://localhost:7000 with live metrics,
    threat log, and network visualization.
    """
    from ..ui.banner import show_command_header, show_loading
    
    show_command_header("Dashboard Server", "Launching real-time web interface")
    show_loading("Starting dashboard", duration=1.5, steps=[
        "Loading Flask server",
        "Initializing routes",
        "Preparing to launch"
    ])
    
    try:
        # Add project root to path so we can import dashboard module
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        console.print(Panel(
            "[bold green]✓ Dashboard Starting![/bold green]\n\n"
            "[cyan]Access URL:[/cyan] [bold white]http://localhost:7000[/bold white]\n"
            "[cyan]Features:[/cyan]\n"
            "  • Real-time metrics monitoring\n"
            "  • P2P network topology\n"
            "  • Threat detection log\n"
            "  • Blockchain evidence viewer\n\n"
            "[yellow]Press Ctrl+C to stop the server[/yellow]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print()
        
        from dashboard.server import start
        start(open_browser=not no_browser)
    except ImportError as e:
        console.print(f"[red]✗ Dashboard dependencies missing: {e}[/red]")
        console.print("[yellow]Install with: pip install flask flask-cors supabase[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Failed to start dashboard: {e}[/red]")

