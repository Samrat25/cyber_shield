# cybershield/commands/api.py
import click
from rich.console import Console

console = Console()


@click.group()
def api():
    """REST API server management."""
    pass


@api.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, type=int, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def start(host, port, debug):
    """Start the REST API server."""
    try:
        import sys
        import os
        from pathlib import Path
        
        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from api.server import start as start_server
        start_server(host=host, port=port, debug=debug)
    except ImportError as e:
        console.print(f"[red]✗ API server dependencies missing: {e}[/red]")
        console.print("[yellow]Install with: pip install flask flask-cors[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Failed to start API server: {e}[/red]")
