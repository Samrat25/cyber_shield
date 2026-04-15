# cybershield/commands/dashboard.py
import click
import sys
import os
from pathlib import Path
from rich.console import Console

console = Console()


@click.command()
@click.option('--no-browser', is_flag=True, help='Do not auto-open browser')
def dashboard(no_browser):
    """
    Start the real-time dashboard server.
    
    Opens a web UI at http://localhost:7000 with live metrics,
    threat log, and network visualization.
    """
    try:
        # Add project root to path so we can import dashboard module
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        from dashboard.server import start
        start(open_browser=not no_browser)
    except ImportError as e:
        console.print(f"[red]✗ Dashboard dependencies missing: {e}[/red]")
        console.print("[yellow]Install with: pip install flask flask-cors supabase[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Failed to start dashboard: {e}[/red]")
