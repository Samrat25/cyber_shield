# cybershield/commands/network.py
import click
import asyncio
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..config import LOGS_DIR, P2P_PORT
from ..network.p2p_node import P2PNode

console = Console()


@click.group()
def network():
    """P2P network management."""
    pass


@network.command()
@click.argument('peer_address')
@click.option('--port', default=P2P_PORT, help='Local P2P port')
def connect(peer_address, port):
    """Connect to a peer node."""
    asyncio.run(_connect_async(peer_address, port))


async def _connect_async(peer_address, port):
    """Async peer connection."""
    # Load node config
    from ..config import CONFIG_DIR
    config_file = CONFIG_DIR / "node_config.json"
    
    if not config_file.exists():
        console.print("[red]✗ Node not initialized. Run 'cybershield node init' first.[/red]")
        return
    
    config = json.loads(config_file.read_text())
    node_id = config['node_id']
    
    console.print(Panel(f"[bold cyan]Connecting to Peer Network[/bold cyan]", expand=False))
    console.print(f"\n  Your Node: [cyan]{node_id}[/cyan]")
    console.print(f"  Peer: [cyan]{peer_address}[/cyan]\n")
    
    # Start P2P node
    p2p_node = P2PNode(node_id=node_id, port=port)
    await p2p_node.start()
    
    # Connect to peer
    success = await p2p_node.connect_to_peer(peer_address)
    
    if success:
        console.print(f"\n[green]✓ Connected successfully![/green]")
        console.print(f"  Total peers: {p2p_node.get_peer_count()}\n")
        
        # Keep connection alive
        console.print("[dim]Press Ctrl+C to disconnect[/dim]\n")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Disconnecting...[/yellow]")
    else:
        console.print(f"\n[red]✗ Connection failed[/red]\n")
    
    await p2p_node.stop()


@network.command()
@click.option('--port', default=P2P_PORT, help='P2P port to listen on')
def listen(port):
    """Start P2P server and wait for connections."""
    asyncio.run(_listen_async(port))


async def _listen_async(port):
    """Async P2P server."""
    from ..config import CONFIG_DIR
    config_file = CONFIG_DIR / "node_config.json"
    
    if not config_file.exists():
        console.print("[red]✗ Node not initialized. Run 'cybershield node init' first.[/red]")
        return
    
    config = json.loads(config_file.read_text())
    node_id = config['node_id']
    
    console.print(Panel(f"[bold cyan]P2P Network Server[/bold cyan]", expand=False))
    
    p2p_node = P2PNode(node_id=node_id, port=port)
    await p2p_node.start()
    
    console.print(f"\n[green]✓ Server started[/green]")
    console.print(f"  Address: [cyan]{p2p_node.local_ip}:{port}[/cyan]")
    console.print(f"\n[dim]Waiting for peer connections...[/dim]")
    console.print(f"[dim]Other nodes can connect with:[/dim]")
    console.print(f"[dim]  cybershield network connect {p2p_node.local_ip}:{port}[/dim]\n")
    
    try:
        while True:
            await asyncio.sleep(5)
            if p2p_node.get_peer_count() > 0:
                console.print(f"[dim]Connected peers: {p2p_node.get_peer_count()}[/dim]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
    
    await p2p_node.stop()


@network.command()
def peers():
    """Show connected peers (requires active monitoring)."""
    console.print("[yellow]This command requires an active monitoring session.[/yellow]")
    console.print("[dim]Run 'cybershield node monitor --p2p' to enable P2P networking.[/dim]\n")
