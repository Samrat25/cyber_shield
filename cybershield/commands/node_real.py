# cybershield/commands/node_real.py
"""
REAL node management with actual blockchain transactions and IPFS
"""

import click
import asyncio
import json
import socket
import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ..config import LOGS_DIR, CONFIG_DIR
from ..core.monitor import SystemMonitor
from ..ml import get_detector
from ..blockchain.aptos import AptosClient
from ..blockchain.node_registry import NodeRegistry
from ..storage.ipfs import IPFSClient
from ..network.p2p_node import P2PNode

console = Console()


@click.group()
def node():
    """Node management commands."""
    pass


@node.command()
def init():
    """Initialize CyberShield node configuration."""
    console.print(Panel("[bold cyan]CyberShield Node Initialization[/bold cyan]", expand=False))
    
    config_file = CONFIG_DIR / "node_config.json"
    
    if config_file.exists():
        console.print("[yellow]⚠ Configuration already exists.[/yellow]")
        if not click.confirm("Overwrite existing configuration?"):
            return
    
    # Generate node ID
    node_id = socket.gethostname()
    
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"
    
    config = {
        "node_id": node_id,
        "local_ip": local_ip,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    config_file.write_text(json.dumps(config, indent=2))
    
    console.print(f"\n[green]✓[/green] Node initialized")
    console.print(f"  Node ID: [cyan]{node_id}[/cyan]")
    console.print(f"  Local IP: [cyan]{local_ip}[/cyan]")
    console.print(f"  Config: [dim]{config_file}[/dim]\n")


@node.command()
@click.option('--force', is_flag=True, help='Force re-registration')
def register(force):
    """
    Register node on blockchain and IPFS.
    This creates REAL transactions on Aptos testnet.
    """
    console.print(Panel("[bold cyan]Node Registration (REAL Blockchain)[/bold cyan]", expand=False))
    
    # Load config
    config_file = CONFIG_DIR / "node_config.json"
    if not config_file.exists():
        console.print("[red]✗ Node not initialized. Run 'cybershield node init' first.[/red]")
        return
    
    config = json.loads(config_file.read_text())
    state_file = LOGS_DIR / "node_state.json"
    
    if state_file.exists() and not force:
        console.print("[yellow]⚠ Node already registered.[/yellow]")
        if not click.confirm("Re-register?"):
            return
    
    node_id = config['node_id']
    local_ip = config['local_ip']
    
    console.print(f"\n  Node ID: [cyan]{node_id}[/cyan]")
    console.print(f"  IP: [cyan]{local_ip}[/cyan]\n")
    
    # 1. Pin to IPFS (REAL)
    with console.status("[yellow]Pinning to IPFS (Pinata)...[/yellow]"):
        ipfs_client = IPFSClient()
        reg_data = {
            "type": "node_registration",
            "node_id": node_id,
            "ip": local_ip,
            "registered_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "online",
            "version": "1.0.0"
        }
        cid = ipfs_client.pin_json(reg_data, f"cybershield-node-{node_id}")
    
    console.print(f"  [green]✓ IPFS CID:[/green] [cyan]{cid}[/cyan]")
    console.print(f"  [dim]  → {ipfs_client.gateway_url(cid)}[/dim]\n")
    
    # 2. Register on blockchain (REAL Aptos transaction)
    with console.status("[yellow]Submitting to Aptos blockchain...[/yellow]"):
        aptos_client = AptosClient()
        tx_hash = aptos_client.register_node(node_id, local_ip, cid)
    
    console.print(f"  [green]✓ TX Hash:[/green] [cyan]{tx_hash}[/cyan]")
    console.print(f"  [dim]  → {aptos_client.explorer_url(tx_hash)}[/dim]\n")
    
    # 3. Save state
    state = {
        "node_id": node_id,
        "ip": local_ip,
        "status": "online",
        "registered_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "reg_cid": cid,
        "reg_tx": tx_hash,
        "threat_count": 0
    }
    state_file.write_text(json.dumps(state, indent=2))
    
    console.print(Panel(
        f"[bold green]✓ Node '{node_id}' registered on blockchain![/bold green]\n"
        f"IPFS CID and Aptos TX are REAL and verifiable.",
        border_style="green",
        expand=False
    ))


@node.command()
def discover():
    """
    Discover other nodes from blockchain.
    Queries REAL on-chain node registry.
    """
    console.print(Panel("[bold cyan]Node Discovery (Reading Blockchain)[/bold cyan]", expand=False))
    
    with console.status("[yellow]Querying blockchain for registered nodes...[/yellow]"):
        registry = NodeRegistry()
        nodes = registry.get_all_nodes_sync()
    
    if not nodes:
        console.print("\n[yellow]No nodes found on blockchain yet.[/yellow]")
        console.print("[dim]Register your node first: cybershield node register[/dim]\n")
        return
    
    console.print(f"\n[green]✓ Found {len(nodes)} registered nodes on blockchain:[/green]\n")
    
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("Node ID", style="cyan")
    table.add_column("IP Address", style="white")
    table.add_column("IPFS CID", style="dim")
    table.add_column("Status", style="green")
    
    for node in nodes:
        table.add_row(
            node['node_id'],
            node['ip'],
            node['ipfs_cid'][:16] + "...",
            node['status']
        )
    
    console.print(table)
    console.print()


@node.command()
@click.option('--p2p/--no-p2p', default=False, help='Enable P2P networking')
@click.option('--port', default=8765, help='P2P port')
@click.option('--auto-discover', is_flag=True, help='Auto-discover and connect to peers from blockchain')
def monitor(p2p, port, auto_discover):
    """
    Start real-time monitoring with ML detection.
    All detections are logged to REAL blockchain and IPFS.
    """
    state_file = LOGS_DIR / "node_state.json"
    if not state_file.exists():
        console.print("[red]✗ Node not registered. Run 'cybershield node register' first.[/red]")
        return
    
    state = json.loads(state_file.read_text())
    node_id = state['node_id']
    
    # Run async monitoring
    asyncio.run(_monitor_async(node_id, state, p2p, port, auto_discover))


async def _monitor_async(node_id, state, enable_p2p, port, auto_discover):
    """Async monitoring loop with REAL blockchain and IPFS logging."""
    console.print(Panel(
        f"[bold cyan]CyberShield Monitoring - Node: {node_id}[/bold cyan]\n"
        f"ML ensemble active | Blockchain logging enabled\n"
        f"P2P: {'[green]Enabled[/green]' if enable_p2p else '[dim]Disabled[/dim]'}\n"
        f"Auto-discover: {'[green]Yes[/green]' if auto_discover else '[dim]No[/dim]'}\n"
        f"Press Ctrl+C to stop",
        expand=False
    ))
    
    # Initialize components
    monitor = SystemMonitor()
    detector = get_detector()
    ipfs_client = IPFSClient()
    aptos_client = AptosClient()
    
    # Start P2P node if enabled
    p2p_node = None
    if enable_p2p:
        p2p_node = P2PNode(node_id=node_id, port=port)
        await p2p_node.start()
        
        # Auto-discover peers from blockchain
        if auto_discover:
            console.print("\n[yellow]Discovering peers from blockchain...[/yellow]")
            registry = NodeRegistry()
            nodes = await registry.get_all_registered_nodes()
            
            for peer in nodes:
                if peer['node_id'] != node_id:
                    peer_addr = f"{peer['ip']}:{port}"
                    console.print(f"  Connecting to {peer['node_id']} at {peer_addr}...")
                    await p2p_node.connect_to_peer(peer_addr)
            
            console.print(f"[green]✓ Connected to {p2p_node.get_peer_count()} peers[/green]\n")
        
        # Register threat broadcast handler
        async def handle_threat_alert(peer_id, data):
            console.print(f"\n[red]⚠ Threat alert from {peer_id}:[/red]")
            console.print(f"  CID: {data.get('cid')}")
            console.print(f"  TX: {data.get('tx_hash')}\n")
        
        p2p_node.register_handler('threat_alert', handle_threat_alert)
    
    check_count = 0
    
    try:
        while True:
            metrics = monitor.get_metrics()
            check_count += 1
            
            # ML detection
            verdict, confidence, model_scores = detector.detect(metrics)
            
            ts = metrics["timestamp"][11:19]
            
            if verdict == "safe":
                # Show peer count if P2P enabled
                peer_info = f"  Peers: {p2p_node.get_peer_count()}" if p2p_node else ""
                
                console.print(
                    f"[dim]{ts}[/dim]  [green]● SAFE[/green]  "
                    f"CPU [green]{metrics['cpu_percent']:5.1f}%[/green]  "
                    f"MEM [green]{metrics['memory_percent']:5.1f}%[/green]  "
                    f"Confidence: [green]{confidence:.2f}[/green]"
                    f"{peer_info}"
                )
                
                # Heartbeat every 30s - REAL IPFS pin
                if check_count % 6 == 0:
                    cid = ipfs_client.pin_json(
                        {**metrics, "verdict": "safe", "model_scores": model_scores},
                        f"heartbeat-{node_id}"
                    )
                    console.print(f"  [dim]↑ Heartbeat pinned: {cid[:24]}...[/dim]")
            
            else:
                # ANOMALY DETECTED - REAL blockchain transaction
                console.print()
                console.print(Panel(
                    f"[bold red]⚠ INTRUSION DETECTED - {node_id}[/bold red]\n\n"
                    f"Confidence: [red]{confidence:.1%}[/red]\n"
                    f"CPU: [red]{metrics['cpu_percent']:.1f}%[/red]  "
                    f"MEM: [red]{metrics['memory_percent']:.1f}%[/red]\n\n"
                    f"Model Scores:\n" +
                    "\n".join([f"  {k}: {v:.3f}" for k, v in model_scores.items()]),
                    border_style="red",
                    expand=False
                ))
                
                # 1. Pin evidence to IPFS (REAL)
                with console.status("[yellow]Pinning evidence to IPFS...[/yellow]"):
                    threat_data = {
                        "type": "threat_detected",
                        "node_id": node_id,
                        "metrics": metrics,
                        "verdict": "anomaly",
                        "confidence": confidence,
                        "model_scores": model_scores
                    }
                    cid = ipfs_client.pin_json(threat_data, f"THREAT-{node_id}")
                
                console.print(f"\n  [green]✓[/green] Evidence CID: [cyan]{cid}[/cyan]")
                console.print(f"    [dim]{ipfs_client.gateway_url(cid)}[/dim]")
                
                # 2. Log on blockchain (REAL Aptos transaction)
                with console.status("[yellow]Writing to Aptos blockchain...[/yellow]"):
                    tx_hash = aptos_client.log_threat(node_id, cid, "anomaly")
                
                console.print(f"\n  [green]✓[/green] TX Hash: [cyan]{tx_hash}[/cyan]")
                console.print(f"    [dim]{aptos_client.explorer_url(tx_hash)}[/dim]")
                
                # 3. Broadcast to peers (REAL P2P)
                if p2p_node:
                    await p2p_node.broadcast({
                        "type": "threat_alert",
                        "node_id": node_id,
                        "cid": cid,
                        "tx_hash": tx_hash,
                        "confidence": confidence
                    })
                    console.print(f"\n  [green]✓[/green] Alert broadcast to {p2p_node.get_peer_count()} peers")
                
                # Update state
                state['status'] = 'COMPROMISED'
                state['last_threat_cid'] = cid
                state['last_threat_tx'] = tx_hash
                state['threat_count'] = state.get('threat_count', 0) + 1
                
                state_file = LOGS_DIR / "node_state.json"
                state_file.write_text(json.dumps(state, indent=2))
                
                console.print(Panel(
                    f"[bold red]NODE QUARANTINED[/bold red]\n\n"
                    f"Evidence permanently stored:\n"
                    f"• IPFS: {cid}\n"
                    f"• Blockchain: {tx_hash}\n\n"
                    f"[dim]All records are REAL and verifiable.[/dim]",
                    border_style="red",
                    expand=False
                ))
                
                break
            
            await asyncio.sleep(5)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped.[/yellow]")
    finally:
        if p2p_node:
            await p2p_node.stop()
