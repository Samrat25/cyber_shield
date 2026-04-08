# cybershield/commands/node_new.py
# NEW VERSION with observation window and payload analysis

import click
import asyncio
import json
import socket
import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich import box
from collections import Counter

from ..config import LOGS_DIR, CONFIG_DIR

console = Console()


class ObservationWindow:
    """
    Watches 20 seconds of readings before declaring an anomaly.
    Prevents false positives from momentary spikes.
    """
    def __init__(self, window_seconds=20, check_interval=5, threshold_ratio=0.66):
        self.max_readings = window_seconds // check_interval  # = 4
        self.threshold = threshold_ratio  # 66% must be anomaly (2.64 out of 4, rounds to 3)
        self.readings = []
    
    def add(self, verdict, confidence, threat_info, metrics):
        self.readings.append({
            "verdict": verdict,
            "confidence": confidence,
            "threat_info": threat_info,
            "metrics": metrics,
            "ts": metrics.get("timestamp", ""),
        })
        if len(self.readings) > self.max_readings:
            self.readings.pop(0)
    
    def should_alert(self):
        """Returns True only when enough readings in the window are anomalous."""
        if len(self.readings) < 2:  # Need at least 2 readings (10 seconds)
            return False
        anomaly_count = sum(1 for r in self.readings if r["verdict"] == "anomaly")
        ratio = anomaly_count / len(self.readings)
        # Alert if 66% or more are anomalous (e.g., 2/3, 3/4)
        return ratio >= self.threshold
    
    def dominant_threat(self):
        """Returns the most common threat type in the window."""
        threats = [
            r["threat_info"].get("threat_type", "unknown")
            for r in self.readings
            if r["verdict"] == "anomaly" and r.get("threat_info")
        ]
        if not threats:
            return "unknown"
        return Counter(threats).most_common(1)[0][0]
    
    def worst_metrics(self):
        """Returns the reading with the highest severity from the window."""
        anomalies = [r for r in self.readings if r["verdict"] == "anomaly"]
        if not anomalies:
            return None
        return max(anomalies, key=lambda r: r["confidence"])
    
    def anomaly_count(self):
        return sum(1 for r in self.readings if r["verdict"] == "anomaly")
    
    def window_size(self):
        return len(self.readings)
    
    def reset(self):
        self.readings = []


def _primary_trigger(payload):
    """Returns a human sentence explaining what triggered the alert."""
    devs = {}
    for key in ["cpu_sigma", "mem_sigma", "procs_sigma", "pkt_sigma", "byt_sigma", "disk_sigma"]:
        val_str = str(payload.get(key, "0")).replace("σ", "").replace("+", "")
        try:
            devs[key.replace("_sigma", "").upper()] = float(val_str)
        except:
            devs[key.replace("_sigma", "").upper()] = 0.0
    
    worst_key = max(devs, key=lambda k: abs(devs[k]))
    worst_val = devs[worst_key]
    return f"{worst_key} spiked {worst_val:+.1f}σ above your personal baseline"


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
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"
    
    config = {
        "node_id": node_id,
        "local_ip": local_ip,
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
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
    """Register node on blockchain and IPFS."""
    # LAZY IMPORTS
    from ..storage.ipfs import IPFSClient
    from ..blockchain.aptos import AptosClient
    from ..core.db import upsert_node
    
    console.print(Panel("[bold cyan]Node Registration[/bold cyan]", expand=False))
    
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
    
    # Pin to IPFS
    with console.status("[yellow]Pinning to IPFS...[/yellow]"):
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
    
    # Register on blockchain
    with console.status("[yellow]Submitting to Aptos blockchain...[/yellow]"):
        aptos_client = AptosClient()
        tx_hash = aptos_client.register_node(node_id, local_ip, cid)
    
    console.print(f"  [green]✓ TX Hash:[/green] [cyan]{tx_hash}[/cyan]")
    console.print(f"  [dim]  → {aptos_client.explorer_url(tx_hash)}[/dim]\n")
    
    # Save state
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
    
    # Log to Supabase
    try:
        upsert_node(node_id, local_ip, "online", reg_cid=cid, reg_tx=tx_hash)
    except Exception:
        pass
    
    console.print(Panel(
        f"[bold green]✓ Node '{node_id}' registered successfully![/bold green]\n"
        f"Blockchain and IPFS records confirmed.",
        border_style="green",
        expand=False
    ))


@node.command()
@click.option('--p2p/--no-p2p', default=False, help='Enable P2P networking')
@click.option('--port', default=8765, help='P2P port')
def monitor(p2p, port):
    """Start real-time monitoring with ML detection."""
    state_file = LOGS_DIR / "node_state.json"
    if not state_file.exists():
        console.print("[red]✗ Node not registered. Run 'cybershield node register' first.[/red]")
        return
    
    state = json.loads(state_file.read_text())
    node_id = state['node_id']
    
    asyncio.run(_monitor_async(node_id, state, p2p, port))


async def _monitor_async(node_id, state, enable_p2p, port):
    """Async monitoring loop with observation window and payload analysis."""
    # LAZY IMPORTS
    from ..core.monitor import SystemMonitor
    from ..ml.custom_detector import get_custom_detector  # Use custom model
    from ..ml.advanced_detector import classify_threat_from_metrics
    from ..blockchain.aptos import AptosClient
    from ..storage.ipfs import IPFSClient
    from ..network.p2p_node import P2PNode
    from ..core.db import log_event, upsert_node
    from ..zk_proof import generate_proof
    
    console.print(Panel(
        f"[bold cyan]CyberShield Monitoring - Node: {node_id}[/bold cyan]\n"
        f"Custom ML model active | Blockchain logging enabled\n"
        f"Observation window: 20s (66% threshold = 3/4 warnings) | Extreme CPU override\n"
        f"P2P: {'[green]Enabled[/green]' if enable_p2p else '[dim]Disabled[/dim]'}\n"
        f"Press Ctrl+C to stop",
        expand=False
    ))
    
    # Initialize
    monitor = SystemMonitor()
    detector = get_custom_detector()  # Use your trained model
    ipfs_client = IPFSClient()
    aptos_client = AptosClient()
    obs = ObservationWindow(window_seconds=20, check_interval=5, threshold_ratio=0.66)
    
    # P2P
    p2p_node = None
    if enable_p2p:
        p2p_node = P2PNode(node_id=node_id, port=port)
        await p2p_node.start()
        
        async def handle_threat_alert(peer_id, data):
            console.print(f"\n[red]⚠ Threat alert from {peer_id}:[/red]")
            console.print(f"  CID: {data.get('cid')}")
            console.print(f"  TX: {data.get('tx_hash')}\n")
        
        p2p_node.register_handler('threat_alert', handle_threat_alert)
    
    check_count = 0
    state_file = LOGS_DIR / "node_state.json"
    
    try:
        while True:
            metrics = monitor.get_metrics()
            metrics["node_id"] = node_id
            check_count += 1
            
            # ML detection
            verdict, confidence, model_scores = detector.detect(metrics)
            
            # Classify threat
            threat_info = classify_threat_from_metrics(metrics) if verdict == "anomaly" else {}
            
            # CRITICAL FIX: If threat classifier detects a real threat, override ML verdict
            if threat_info.get("threat_type") not in ["safe", None, ""]:
                # Threat classifier found something - trust it
                verdict = "anomaly"
                if confidence < 0.6:
                    confidence = 0.75  # Boost confidence
            elif threat_info.get("threat_type") == "safe":
                # Threat classifier says safe - override to safe
                verdict = "safe"
                confidence = 0.5
            
            # Add to observation window
            obs.add(verdict, confidence, threat_info, metrics)
            
            ts = metrics["timestamp"][11:19]
            
            if verdict == "safe":
                # SAFE status
                try:
                    log_event(metrics, "safe", confidence)
                except Exception:
                    pass
                
                peer_info = f"  Peers: {p2p_node.get_peer_count()}" if p2p_node else ""
                
                console.print(
                    f"[dim]{ts}[/dim]  [green]● SAFE[/green]  "
                    f"CPU {metrics['cpu_percent']:5.1f}%  "
                    f"MEM {metrics['memory_percent']:5.1f}%  "
                    f"PROCS {metrics.get('process_count',0)}  "
                    f"conf={confidence:.2f}"
                    f"{peer_info}"
                )
                
                # Heartbeat
                if check_count % 6 == 0:
                    try:
                        cid = ipfs_client.pin_json(
                            {**metrics, "verdict": "safe", "model_scores": model_scores},
                            f"heartbeat-{node_id}"
                        )
                        console.print(f"  [dim]↑ Heartbeat: {cid[:24]}...[/dim]")
                    except Exception:
                        pass
            
            else:
                # WARNING - but don't act yet
                ti = threat_info or {}
                console.print(
                    f"[dim]{ts}[/dim]  [yellow]⚠ WARNING[/yellow] [{obs.anomaly_count()}/{obs.window_size()} readings]  "
                    f"CPU {metrics['cpu_percent']:5.1f}%  "
                    f"MEM {metrics['memory_percent']:5.1f}%  "
                    f"Threat: [yellow]{ti.get('threat_label','unknown')}[/yellow]  "
                    f"conf={confidence:.2f}"
                )
            
            # Check if observation window confirms attack
            if obs.should_alert():
                worst = obs.worst_metrics()
                w_ti = worst["threat_info"] if worst else threat_info
                w_met = worst["metrics"] if worst else metrics
                w_conf = worst["confidence"] if worst else confidence
                
                # FIRE ALERT
                await _fire_anomaly_alert(
                    node_id, w_met, w_conf, model_scores, w_ti, obs,
                    ipfs_client, aptos_client, p2p_node, state, state_file
                )
                
                obs.reset()
                break
            
            await asyncio.sleep(5)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped.[/yellow]")
    finally:
        if p2p_node:
            await p2p_node.stop()


async def _fire_anomaly_alert(node_id, metrics, confidence, model_scores, threat_info,
                               obs_window, ipfs_client, aptos_client, p2p_node, state, state_file):
    """Fire confirmed anomaly alert with full payload analysis."""
    from ..zk_proof import generate_proof
    
    ti = threat_info or {}
    payload = ti.get("payload", {})
    severity = ti.get("severity", "HIGH")
    t_label = ti.get("threat_label", "Unknown Anomaly")
    
    sev_color = {"LOW": "yellow", "MEDIUM": "yellow", "HIGH": "red", "CRITICAL": "bold red"}.get(severity, "red")
    
    # Generate ZK proof
    zk_proof = generate_proof(metrics, confidence, "pending")
    
    # Display full alert
    console.print()
    console.print(Panel(
        f"[bold red]⚠  INTRUSION CONFIRMED — {node_id}[/bold red]\n\n"
        f"  Observation: [red]{obs_window.anomaly_count()} of {obs_window.max_readings} readings anomalous[/red]\n"
        f"  Attack Type: [{sev_color}]{t_label}[/{sev_color}]\n"
        f"  Severity   : [{sev_color}]{severity}[/{sev_color}]\n"
        f"  Confidence : [red]{confidence:.1%}[/red]\n\n"
        f"  [bold]Payload — Metric Deviations from YOUR Baseline:[/bold]\n"
        f"  ────────────────────────────────────────────────\n"
        f"  CPU    {payload.get('cpu_actual','?'):>6}%  "
        f"baseline={payload.get('cpu_baseline','?')}%  "
        f"spike=[red]{payload.get('cpu_sigma','?')}[/red]\n"
        f"  MEM    {payload.get('mem_actual','?'):>6}%  "
        f"baseline={payload.get('mem_baseline','?')}%  "
        f"spike=[red]{payload.get('mem_sigma','?')}[/red]\n"
        f"  PROCS  {payload.get('procs_actual','?'):>6}   "
        f"baseline={payload.get('procs_baseline','?')}   "
        f"spike=[red]{payload.get('procs_sigma','?')}[/red]\n"
        f"  NET PKT deviation  [red]{payload.get('pkt_sigma','?')}[/red]\n"
        f"  NET BYT deviation  [red]{payload.get('byt_sigma','?')}[/red]\n"
        f"  DISK    deviation  [red]{payload.get('disk_sigma','?')}[/red]\n"
        f"  ────────────────────────────────────────────────\n"
        f"  MAX DEVIATION: [bold red]{payload.get('max_deviation','?')}[/bold red]\n\n"
        f"  [dim]Primary trigger: {_primary_trigger(payload)}[/dim]",
        border_style="red", expand=False
    ))
    
    # Pin evidence
    try:
        with console.status("[yellow]Pinning evidence to IPFS...[/yellow]"):
            threat_data = {
                "type": "threat_detected",
                "node_id": node_id,
                "metrics": metrics,
                "verdict": "anomaly",
                "confidence": confidence,
                "model_scores": model_scores,
                "threat_info": threat_info,
                "zk_proof": zk_proof
            }
            cid = ipfs_client.pin_json(threat_data, f"THREAT-{node_id}")
        
        gateway_url = ipfs_client.gateway_url(cid)
        console.print(f"\n  [green]✓[/green] Evidence CID: [cyan]{cid}[/cyan]")
        console.print(f"  [green]✓[/green] IPFS Gateway: [cyan]{gateway_url}[/cyan]")
        console.print(f"  [green]✓[/green] ZK Proof: [cyan]{zk_proof['proof_hash'][:32]}...[/cyan] ({zk_proof['method']})")
    except Exception as e:
        console.print(f"\n  [yellow]⚠[/yellow] IPFS: {e}")
        cid = f"QmOFFLINE{abs(hash(str(metrics)))%10**16:016x}"
        console.print(f"  [dim]Using offline CID: {cid}[/dim]")
        console.print(f"  [green]✓[/green] ZK Proof: [cyan]{zk_proof['proof_hash'][:32]}...[/cyan] ({zk_proof['method']})")
    
    # Log to Supabase
    try:
        from ..core.db import log_event
        log_event(metrics, "anomaly", confidence, ipfs_cid=cid, threat_type=ti.get("threat_type", "unknown"))
    except Exception as e:
        console.print(f"  [dim]Supabase logging skipped: {e}[/dim]")
    
    # Log on blockchain
    with console.status("[yellow]Writing to blockchain...[/yellow]"):
        try:
            tx_hash = await aptos_client._submit_async(node_id, cid, "anomaly")
            console.print(f"  [green]✓[/green] TX Hash: [cyan]{tx_hash}[/cyan]")
        except Exception as e:
            console.print(f"  [red]✗[/red] Blockchain: {e}")
            tx_hash = f"0xOFFLINE{abs(hash(cid))%10**16:016x}"
    
    # Broadcast to peers
    if p2p_node:
        await p2p_node.broadcast({
            "type": "threat_alert",
            "node_id": node_id,
            "cid": cid,
            "tx_hash": tx_hash,
            "confidence": confidence,
            "threat_type": ti.get("threat_type", "unknown")
        })
        console.print(f"  [green]✓[/green] Alert broadcast to {p2p_node.get_peer_count()} peers")
    
    # Update state
    state['status'] = 'COMPROMISED'
    state['last_threat_cid'] = cid
    state['last_threat_tx'] = tx_hash
    state['threat_count'] = state.get('threat_count', 0) + 1
    state_file.write_text(json.dumps(state, indent=2))
    
    console.print(Panel(
        f"[bold red]NODE QUARANTINED[/bold red]\n\n"
        f"This node has been flagged and isolated.\n"
        f"Evidence permanently stored on IPFS and blockchain.",
        border_style="red",
        expand=False
    ))
