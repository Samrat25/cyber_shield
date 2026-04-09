# cybershield/commands/network.py
import click
import asyncio
import json
import threading
from pathlib import Path
from datetime import datetime, UTC
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..config import LOGS_DIR, P2P_PORT
from ..network.p2p_node import P2PNode

console = Console()


class PeerRegistry:
    """
    Stores real connected peers with their live metrics.
    Dashboard reads this file to show real node data.
    """
    def __init__(self):
        self._peers = {}   # node_id → peer dict
        self._lock  = threading.Lock()
        self._peers_file = LOGS_DIR / "peers.json"
        self._load()
    
    def _load(self):
        if self._peers_file.exists():
            try:
                with open(self._peers_file) as f:
                    self._peers = json.load(f)
            except Exception:
                self._peers = {}
    
    def _save(self):
        self._peers_file.parent.mkdir(exist_ok=True)
        with open(self._peers_file, "w") as f:
            json.dump(self._peers, f, indent=2, default=str)
    
    def register(self, node_id: str, ip: str, extra: dict = None):
        with self._lock:
            self._peers[node_id] = {
                "node_id"     : node_id,
                "ip"          : ip,
                "status"      : "online",
                "type"        : "real",
                "connected_at": datetime.now(UTC).isoformat(),
                "last_seen"   : datetime.now(UTC).isoformat(),
                "os"          : extra.get("os", "") if extra else "",
            }
            self._save()
            print(f"[DEBUG] Peer registered and saved to {self._peers_file}")
    
    def update_metrics(self, node_id: str, metrics: dict):
        with self._lock:
            if node_id in self._peers:
                self._peers[node_id].update({
                    "last_seen"     : datetime.now(UTC).isoformat(),
                    "cpu_percent"   : metrics.get("cpu_percent"),
                    "memory_percent": metrics.get("memory_percent"),
                    "process_count" : metrics.get("process_count"),
                    "verdict"       : metrics.get("verdict", "safe"),
                    "status"        : "online",
                })
                self._save()
            else:
                # Auto-register if not found
                self.register(node_id, metrics.get("ip", "unknown"), {"os": metrics.get("os", "")})
    
    def disconnect(self, node_id: str):
        with self._lock:
            if node_id in self._peers:
                self._peers[node_id]["status"] = "offline"
                self._save()
    
    def all(self) -> list:
        with self._lock:
            return list(self._peers.values())
    
    def count(self) -> int:
        return len([p for p in self._peers.values() if p.get("status") == "online"])


# Global registry
peer_registry = PeerRegistry()


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
    """Async P2P server with real WebSocket peer handling."""
    try:
        import websockets
    except ImportError:
        console.print("[red]✗ websockets not installed. Run: pip install websockets[/red]")
        return
    
    from ..config import CONFIG_DIR
    config_file = CONFIG_DIR / "node_config.json"
    
    if not config_file.exists():
        console.print("[red]✗ Node not initialized. Run 'cybershield node init' first.[/red]")
        return
    
    config = json.loads(config_file.read_text())
    node_id = config['node_id']
    
    console.print(Panel(f"[bold cyan]P2P Network Server — Real WebSocket Listener[/bold cyan]", expand=False))
    console.print(f"\n[green]✓ Server starting on port {port}[/green]")
    console.print(f"[dim]Waiting for peer connections...[/dim]\n")
    
    async def handle_peer(websocket):
        """Handles one WebSocket connection from a peer node."""
        peer_node_id = None
        check_count = 0
        try:
            async for raw_msg in websocket:
                check_count += 1
                try:
                    msg = json.loads(raw_msg)
                except json.JSONDecodeError:
                    continue
                
                msg_type = msg.get("type")
                
                if msg_type == "register":
                    peer_node_id = msg.get("node_id", f"peer-{id(websocket)}")
                    ip      = msg.get("ip", websocket.remote_address[0])
                    peer_registry.register(peer_node_id, ip, {"os": msg.get("os","")})
                    console.print(f"  [green]✓[/green] Peer registered: [cyan]{peer_node_id}[/cyan] ({ip})")
                    # Send back acknowledgment
                    await websocket.send(json.dumps({
                        "type"   : "ack",
                        "message": f"Connected to CyberShield node {node_id}",
                        "peers"  : peer_registry.count()
                    }))
                
                elif msg_type == "heartbeat":
                    data = msg.get("data", {})
                    if not peer_node_id:
                        peer_node_id = data.get("node_id", f"peer-{id(websocket)}")
                        peer_registry.register(peer_node_id, data.get("ip","?"))
                    peer_registry.update_metrics(peer_node_id, data)
                    console.print(
                        f"  [dim]← {peer_node_id}: "
                        f"CPU={data.get('cpu_percent',0):.1f}%  "
                        f"MEM={data.get('memory_percent',0):.1f}%[/dim]"
                    )
                    # Debug: verify file is updated
                    if check_count % 6 == 0:  # Every 30 seconds
                        console.print(f"  [dim]✓ Peer data saved to logs/peers.json[/dim]")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if peer_node_id:
                peer_registry.disconnect(peer_node_id)
                console.print(f"  [yellow]✗[/yellow] Peer disconnected: [cyan]{peer_node_id}[/cyan]")
    
    try:
        async with websockets.serve(handle_peer, "0.0.0.0", port):
            console.print(f"[green]✓ WebSocket server listening on 0.0.0.0:{port}[/green]\n")
            await asyncio.Future()  # run forever
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]✗ Server error: {e}[/red]")


@network.command()
def peers():
    """Show connected peers (requires active monitoring)."""
    console.print("[yellow]This command requires an active monitoring session.[/yellow]")
    console.print("[dim]Run 'cybershield node monitor --p2p' to enable P2P networking.[/dim]\n")
