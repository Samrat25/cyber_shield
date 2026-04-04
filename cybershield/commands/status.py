# cybershield/commands/status.py
import click
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..config import LOGS_DIR, CONFIG_DIR
from ..blockchain.aptos import AptosClient

console = Console()


@click.command()
def status():
    """Show node status and statistics."""
    console.print(Panel("[bold cyan]CyberShield Node Status[/bold cyan]", expand=False))
    
    # Check if initialized
    config_file = CONFIG_DIR / "node_config.json"
    if not config_file.exists():
        console.print("\n[yellow]⚠ Node not initialized[/yellow]")
        console.print("[dim]Run 'cybershield node init' to get started[/dim]\n")
        return
    
    config = json.loads(config_file.read_text())
    
    # Check if registered
    state_file = LOGS_DIR / "node_state.json"
    if not state_file.exists():
        console.print(f"\n[yellow]⚠ Node initialized but not registered[/yellow]")
        console.print(f"  Node ID: [cyan]{config['node_id']}[/cyan]")
        console.print(f"  Local IP: [cyan]{config['local_ip']}[/cyan]")
        console.print("\n[dim]Run 'cybershield node register' to register on blockchain[/dim]\n")
        return
    
    state = json.loads(state_file.read_text())
    
    # Create status table
    t = Table(box=box.ROUNDED, show_header=False, min_width=60)
    t.add_column("Key", style="cyan", min_width=22)
    t.add_column("Value", style="white")
    
    # Status color
    status = state.get('status', 'unknown')
    color = "green" if status == "online" else "red"
    
    t.add_row("Node ID", state.get('node_id', 'N/A'))
    t.add_row("IP Address", state.get('ip', 'N/A'))
    t.add_row("Status", f"[{color}]{status}[/{color}]")
    t.add_row("Registered At", state.get('registered_at', 'N/A'))
    t.add_row("Registration CID", state.get('reg_cid', 'N/A'))
    t.add_row("Registration TX", state.get('reg_tx', 'N/A'))
    t.add_row("Local Threats", str(state.get('threat_count', 0)))
    
    # Get on-chain count
    try:
        aptos_client = AptosClient()
        onchain_count = aptos_client.get_log_count()
        t.add_row("On-Chain Threats", f"[red]{onchain_count}[/red]")
    except Exception:
        t.add_row("On-Chain Threats", "[dim]Unable to fetch[/dim]")
    
    console.print()
    console.print(t)
    console.print()
    
    # Show last threat if any
    if state.get('last_threat_cid'):
        console.print(Panel(
            f"[bold red]Last Threat Detected[/bold red]\n\n"
            f"CID: [cyan]{state['last_threat_cid']}[/cyan]\n"
            f"TX: [cyan]{state['last_threat_tx']}[/cyan]\n"
            f"Time: {state.get('compromised_at', 'N/A')}",
            border_style="red",
            expand=False
        ))
        console.print()
