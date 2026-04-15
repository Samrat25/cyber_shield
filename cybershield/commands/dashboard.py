# cybershield/commands/dashboard.py
import click
import sys
import secrets
import webbrowser
from pathlib import Path
from rich.console import Console
from cybershield.ui.banner import show_banner, show_command_header, show_loading, show_success

console = Console()


@click.command()
@click.option('--no-browser', is_flag=True, help='Do not auto-open browser')
@click.option('--port', default=8080, help='Dashboard port (default: 8080)')
def dashboard(no_browser, port):
    """
    Start the real-time dashboard with React UI.
    
    Opens a web UI at http://localhost:8080/dashboard with live metrics,
    threat log, and network visualization.
    """
    show_banner(subtitle="Dashboard Server", clear_screen=True)
    show_command_header("DASHBOARD", "Starting real-time monitoring dashboard")
    
    show_loading("Initializing dashboard", duration=1.0, steps=[
        "Loading configuration",
        "Starting server",
        "Generating session key"
    ])
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Generate unique session key
        session_key = secrets.token_urlsafe(32)
        
        from dashboard.server import start_dashboard_server
        
        # Start server in background
        dashboard_url = f"http://localhost:{port}/dashboard?key={session_key}"
        
        console.print(f"\n[bold green]✓ Dashboard server starting...[/bold green]\n")
        console.print(f"[cyan]Dashboard URL:[/cyan] {dashboard_url}")
        console.print(f"[cyan]Session Key:[/cyan] {session_key}")
        console.print(f"[cyan]Port:[/cyan] {port}\n")
        
        console.print(f"[bold yellow]📋 Share this link:[/bold yellow]")
        console.print(f"[green]{dashboard_url}[/green]\n")
        
        console.print(f"[dim]The session key persists across restarts.[/dim]")
        console.print(f"[dim]Press Ctrl+C to stop the server[/dim]\n")
        
        # Open browser
        if not no_browser:
            console.print("[yellow]Opening browser...[/yellow]\n")
            webbrowser.open(dashboard_url)
        
        # Start the server (blocking)
        start_dashboard_server(port=port, session_key=session_key)
        
    except ImportError as e:
        console.print(f"[red]✗ Dashboard dependencies missing: {e}[/red]")
        console.print("[yellow]Install with: pip install flask flask-cors supabase[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard server stopped.[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Failed to start dashboard: {e}[/red]")
