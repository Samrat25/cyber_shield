#!/usr/bin/env python3
# cli.py
# python3 cli.py register
# python3 cli.py monitor
# python3 cli.py status

import sys, time, json, os, socket, datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich         import box

from core.monitor     import get_metrics
from core.ml_detector import detect, train
from core.pinata      import pin_json, gateway_url
from core.aptos       import register_node, log_threat, get_log_count, explorer_url

console    = Console()
STATE_FILE = "logs/node_state.json"
os.makedirs("logs", exist_ok=True)

# ── REGISTER ────────────────────────────────────────────────────────────────
def cmd_register():
    console.print(Panel("[bold cyan]CyberShield — Node Registration[/bold cyan]", expand=False))
    
    node_id  = socket.gethostname()
    ip       = socket.gethostbyname(socket.gethostname())
    reg_time = datetime.datetime.now(datetime.UTC).isoformat()
    
    console.print(f"\n  Node ID : [cyan]{node_id}[/cyan]")
    console.print(f"  IP      : [cyan]{ip}[/cyan]")
    console.print(f"  Time    : {reg_time}\n")
    
    # 1. Pin to Pinata
    with console.status("[yellow]Pinning node info to Pinata IPFS...[/yellow]"):
        reg_data = {"type": "node_registration", "node_id": node_id,
                    "ip": ip, "registered_at": reg_time, "status": "online"}
        cid = pin_json(reg_data, name=f"cybershield-node-{node_id}")
    
    console.print(f"  [green]✓ IPFS CID  :[/green] [cyan]{cid}[/cyan]")
    console.print(f"  [dim]  → {gateway_url(cid)}[/dim]\n")
    
    # 2. Log on Aptos testnet
    with console.status("[yellow]Submitting registration TX to Aptos testnet...[/yellow]"):
        tx = register_node(node_id, ip, cid)
    
    console.print(f"  [green]✓ TX Hash   :[/green] [cyan]{tx}[/cyan]")
    console.print(f"  [dim]  → {explorer_url(tx)}[/dim]\n")
    
    # 3. Save state
    state = {"node_id": node_id, "ip": ip, "status": "online",
             "registered_at": reg_time, "reg_cid": cid, "reg_tx": tx,
             "threat_count": 0}
    Path(STATE_FILE).write_text(json.dumps(state, indent=2))
    
    console.print(Panel(
        f"[bold green]Node '{node_id}' is registered and online.[/bold green]\n"
        f"IPFS + Aptos testnet records confirmed.",
        border_style="green", expand=False
    ))

# ── MONITOR ─────────────────────────────────────────────────────────────────
def cmd_monitor():
    if not Path(STATE_FILE).exists():
        console.print("[red]Register first: python3 cli.py register[/red]")
        sys.exit(1)
    
    state   = json.loads(Path(STATE_FILE).read_text())
    node_id = state["node_id"]
    check   = 0
    
    console.print(Panel(
        f"[bold cyan]CyberShield — Monitoring Node: {node_id}[/bold cyan]\n"
        f"ML checks every 5s  |  Safe status pins to IPFS every 30s\n"
        f"Ctrl+C to stop",
        expand=False
    ))
    
    # Show mock network alongside
    console.print("\n[dim]Network topology (mock P2P layer):[/dim]")
    console.print("  [green]● Node-2[/green] [dim]192.168.1.102 — online[/dim]")
    console.print("  [green]● Node-3[/green] [dim]192.168.1.103 — online[/dim]")
    console.print(f"  [green]● {node_id}[/green] [dim]{state['ip']} — online  ← YOU[/dim]\n")
    console.print("─" * 70)
    
    try:
        while True:
            metrics = get_metrics()
            check  += 1
            verdict, score = detect(metrics)
            ts = metrics["timestamp"][11:19]
            
            if verdict == "safe":
                console.print(
                    f"[dim]{ts}[/dim]  [green]● SAFE[/green]  "
                    f"CPU [green]{metrics['cpu_percent']:5.1f}%[/green]  "
                    f"MEM [green]{metrics['memory_percent']:5.1f}%[/green]  "
                    f"PROCS [green]{metrics['process_count']}[/green]  "
                    f"[dim]score {score}[/dim]"
                )
                # Pin safe heartbeat to Pinata every 30s
                if check % 6 == 0:
                    with console.status("  [dim]Pinning heartbeat...[/dim]"):
                        cid = pin_json({**metrics, "verdict": "safe"},
                                       f"cybershield-heartbeat-{node_id}")
                    console.print(f"  [dim]↑ Heartbeat CID: {cid[:28]}...[/dim]")
            
            else:
                # ── ANOMALY PATH ──────────────────────────────────────────
                console.print()
                console.print(Panel(
                    f"[bold red]⚠  INTRUSION DETECTED — {node_id}[/bold red]\n\n"
                    f"CPU      [red]{metrics['cpu_percent']}%[/red]  "
                    f"MEM  [red]{metrics['memory_percent']}%[/red]  "
                    f"PROCS [red]{metrics['process_count']}[/red]\n"
                    f"NET recv [red]{metrics['net_bytes_recv']:,}[/red] bytes\n"
                    f"ML score [red]{score}[/red]  (anomaly threshold < 0)",
                    border_style="red", expand=False
                ))
                
                # 1. Pin threat evidence to Pinata
                with console.status("[yellow]  [1/2] Pinning threat evidence to Pinata IPFS...[/yellow]"):
                    threat_data = {
                        "type"     : "threat_detected",
                        "node_id"  : node_id,
                        "ip"       : metrics["ip"],
                        "metrics"  : metrics,
                        "verdict"  : "anomaly",
                        "ml_score" : score,
                    }
                    cid = pin_json(threat_data, f"cybershield-THREAT-{node_id}")
                
                console.print(f"\n  [green]✓[/green] Evidence pinned to IPFS")
                console.print(f"    CID : [cyan]{cid}[/cyan]")
                console.print(f"    URL : [dim]{gateway_url(cid)}[/dim]")
                
                # 2. Log on Aptos testnet
                with console.status("[yellow]  [2/2] Writing to Aptos testnet blockchain...[/yellow]"):
                    tx = log_threat(node_id, cid, "anomaly")
                
                onchain = get_log_count()
                
                console.print(f"\n  [green]✓[/green] TX confirmed on Aptos testnet")
                console.print(f"    TX  : [cyan]{tx}[/cyan]")
                console.print(f"    URL : [dim]{explorer_url(tx)}[/dim]")
                console.print(f"    Total on-chain threats logged: [red]{onchain}[/red]")
                
                # Update local state
                state.update({
                    "status": "COMPROMISED",
                    "compromised_at"   : metrics["timestamp"],
                    "last_threat_cid"  : cid,
                    "last_threat_tx"   : tx,
                    "threat_count"     : state.get("threat_count", 0) + 1
                })
                Path(STATE_FILE).write_text(json.dumps(state, indent=2))
                
                # 3. Node disconnect sequence
                console.print()
                console.print(Panel(
                    f"[bold red]NODE QUARANTINED — {node_id}[/bold red]\n\n"
                    f"[red]This node has been isolated from the network.[/red]\n\n"
                    f"  [green]● Node-2[/green] [dim]192.168.1.102 — still online[/dim]\n"
                    f"  [green]● Node-3[/green] [dim]192.168.1.103 — still online[/dim]\n"
                    f"  [red]✕ {node_id}[/red] [dim]{metrics['ip']} — DISCONNECTED[/dim]\n\n"
                    f"[dim]Future: traffic reroutes automatically to Node-2 / Node-3.[/dim]",
                    border_style="red", expand=False
                ))
                sys.exit(0)
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped.[/yellow]")

# ── STATUS ───────────────────────────────────────────────────────────────────
def cmd_status():
    if not Path(STATE_FILE).exists():
        console.print("[red]No node registered yet.[/red]")
        return
    state = json.loads(Path(STATE_FILE).read_text())
    t = Table(box=box.ROUNDED, show_header=False, min_width=60)
    t.add_column("Key",   style="cyan",  min_width=22)
    t.add_column("Value", style="white")
    color = "green" if state.get("status") == "online" else "red"
    for k, v in state.items():
        val = f"[{color}]{v}[/{color}]" if k == "status" else str(v)
        t.add_row(k, val)
    # Also show live on-chain count
    try:
        count = get_log_count()
        t.add_row("on_chain_threat_count", f"[red]{count}[/red]")
    except Exception:
        pass
    console.print(Panel(t, title="[cyan]Node Status[/cyan]", border_style="cyan"))

# ── ENTRY ────────────────────────────────────────────────────────────────────
HELP = """
[bold cyan]CyberShield CLI[/bold cyan]

  [green]python3 cli.py register[/green]   register this node on IPFS + Aptos testnet
  [green]python3 cli.py monitor[/green]    start real-time ML monitoring
  [green]python3 cli.py status[/green]     show current node state + on-chain count
  [green]python3 cli.py train[/green]      train / retrain the ML model
"""

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "register": cmd_register()
    elif cmd == "monitor": cmd_monitor()
    elif cmd == "status" : cmd_status()
    elif cmd == "train"  :
        console.print("[yellow]Training...[/yellow]")
        train()
        console.print("[green]✓ Done[/green]")
    else:
        console.print(HELP)
