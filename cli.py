#!/usr/bin/env python3
"""
CyberShield CLI
Commands: register | monitor | test | status | train | calibrate | dashboard
"""
import sys, time, json, os, socket, datetime, threading
from pathlib import Path

# ── Lazy dotenv — only load what's needed ──────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich.columns import Columns
from rich         import box

console    = Console()
STATE_FILE = "logs/node_state.json"
os.makedirs("logs", exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────────────────────────
def _load_state() -> dict:
    if Path(STATE_FILE).exists():
        return json.loads(Path(STATE_FILE).read_text())
    return {}

def _save_state(s: dict):
    Path(STATE_FILE).write_text(json.dumps(s, indent=2))

def _require_state() -> dict:
    s = _load_state()
    if not s:
        console.print("[red]Register first: python cli.py register[/red]")
        sys.exit(1)
    return s

# ── CALIBRATE ────────────────────────────────────────────────────────────────────
def cmd_calibrate():
    """Sample YOUR machine for 30s to build a personal ML baseline."""
    from core.ml_detector import calibrate, train as ml_train

    console.print(Panel(
        "[bold cyan]CyberShield — Machine Calibration[/bold cyan]\n\n"
        "Sampling your system (30 seconds). Keep machine IDLE.\n"
        "[dim]Close heavy apps, browser tabs, etc.[/dim]",
        expand=False
    ))
    baseline = calibrate(samples=20, interval=1.5)
    console.print("\n[yellow]Retraining ML model on your baseline...[/yellow]")
    ml_train()
    console.print(Panel(
        f"[bold green]Calibration done![/bold green]\n\n"
        f"  CPU  : {baseline['cpu_mean']:.1f}% \u00b1 {baseline['cpu_std']:.1f}\n"
        f"  MEM  : {baseline['mem_mean']:.1f}% \u00b1 {baseline['mem_std']:.1f}\n"
        f"  PROCS: {baseline['prc_mean']:.0f} \u00b1 {baseline['prc_std']:.0f}\n\n"
        f"Now run: [green]python cli.py register[/green]",
        border_style="green", expand=False
    ))

# ── TRAIN ────────────────────────────────────────────────────────────────────────
def cmd_train():
    from core.ml_detector import train as ml_train
    console.print("[yellow]Training ML model...[/yellow]")
    ml_train()
    console.print("[green]\u2713 Model saved to ml/[/green]")

# ── REGISTER ─────────────────────────────────────────────────────────────────────
def cmd_register():
    console.print(Panel("[bold cyan]CyberShield — Node Registration[/bold cyan]", expand=False))

    node_id  = socket.gethostname()
    try:
        ip = "127.0.0.1"
        import socket as sock
        sock.setdefaulttimeout(2.0)
        ip = sock.gethostbyname(sock.gethostname())
    except:
        ip = "127.0.0.1"
    reg_time = datetime.datetime.now(datetime.UTC).isoformat()

    console.print(f"\n  Node ID : [cyan]{node_id}[/cyan]")
    console.print(f"  IP      : [cyan]{ip}[/cyan]\n")

    # Step 1 — IPFS
    try:
        from core.pinata import pin_json, gateway_url
        with console.status("[yellow]Pinning to Pinata IPFS (timeout 20s)...[/yellow]"):
            cid = pin_json(
                {"type": "node_reg", "node_id": node_id,
                 "ip": ip, "registered_at": reg_time},
                name=f"cs-node-{node_id}"
            )
        console.print(f"  [green]\u2713 IPFS CID  :[/green] [cyan]{cid}[/cyan]")
        console.print(f"  [dim]  {gateway_url(cid)}[/dim]\n")
    except Exception as e:
        console.print(f"  [red]\u2717 IPFS failed: {e}[/red]")
        cid = f"OFFLINE-{abs(hash(node_id+reg_time))%10**10}"
        console.print(f"  [yellow]  Using offline CID: {cid}[/yellow]\n")

    # Step 2 — Aptos
    tx = None
    try:
        from core.aptos_direct import register_node, explorer_url
        with console.status("[yellow]Submitting Aptos testnet TX...[/yellow]"):
            tx = register_node(node_id, ip, cid)
        console.print(f"  [green]\u2713 Aptos TX  :[/green] [cyan]{tx}[/cyan]")
        console.print(f"  [dim]  {explorer_url(tx)}[/dim]")
    except Exception as e:
        console.print(f"  [red]\u2717 Aptos failed: {e}[/red]")
        tx = f"0xOFFLINE{abs(hash(cid))%10**10:010x}"
        console.print(f"  [yellow]  Using offline TX: {tx}[/yellow]")

    console.print()

    # Step 3 — Supabase (optional)
    try:
        from core.db import upsert_node
        upsert_node(node_id, ip, "online", reg_cid=cid, reg_tx=tx)
    except Exception:
        pass

    state = {
        "node_id": node_id, "ip": ip, "status": "online",
        "registered_at": reg_time, "reg_cid": cid, "reg_tx": tx,
        "threat_count": 0, "warning_count": 0
    }
    _save_state(state)
    console.print(Panel(
        f"[bold green]'{node_id}' registered successfully.[/bold green]\n"
        f"Run: [green]python cli.py monitor[/green]",
        border_style="green", expand=False
    ))

# ── MONITOR ──────────────────────────────────────────────────────────────────────
def cmd_monitor():
    from core.monitor     import get_metrics
    from core.ml_detector import detect

    state   = _require_state()
    node_id = state["node_id"]
    check   = 0
    warning = 0
    QUARANTINE_AT = 3

    console.print(Panel(
        f"[bold cyan]CyberShield Monitor — {node_id}[/bold cyan]\n"
        f"Checks every 5s  |  Quarantine after {QUARANTINE_AT} anomalies  |  Ctrl+C to stop",
        expand=False
    ))
    console.print("\n[dim]P2P Network (mock topology):[/dim]")
    console.print(f"  [green]\u25cf[/green] {node_id}  {state.get('ip')}  \u2190 YOU")
    console.print(f"  [dim]\u25cf[/dim] node-2  192.168.1.102  (mock)")
    console.print(f"  [dim]\u25cf[/dim] node-3  192.168.1.103  (mock)")
    console.print("\u2500" * 70 + "\n")

    def _async_pin(data, name):
        try:
            from core.pinata import pin_json
            return pin_json(data, name)
        except Exception:
            return None

    try:
        while True:
            metrics = get_metrics()
            check  += 1
            ts      = metrics["timestamp"][11:19]

            verdict, score, threat_info = detect(metrics)

            if verdict == "safe":
                warning = 0
                console.print(
                    f"[dim]{ts}[/dim]  [green]\u25cf SAFE[/green]  "
                    f"CPU [green]{metrics['cpu_percent']:5.1f}%[/green]  "
                    f"MEM [green]{metrics['memory_percent']:5.1f}%[/green]  "
                    f"PROCS [green]{metrics['process_count']}[/green]  "
                    f"DISK [green]{metrics.get('disk_percent',0):.0f}%[/green]  "
                    f"[dim]score={score:.4f}[/dim]"
                )
                if check % 6 == 0:
                    t = threading.Thread(
                        target=_async_pin,
                        args=({**metrics, "verdict": "safe"}, f"hb-{node_id}"),
                        daemon=True
                    )
                    t.start()
                    console.print(f"  [dim]\u2191 heartbeat pinning in background...[/dim]")

                try:
                    from core.db import log_event, upsert_node
                    log_event(metrics, "safe", score)
                    upsert_node(node_id, metrics["ip"], "online")
                except Exception:
                    pass

            else:
                # ── ANOMALY ────────────────────────────────────────────────────
                warning += 1
                t_type   = threat_info.get("threat_type",  "unknown")
                t_label  = threat_info.get("threat_label", "Unknown")
                severity = threat_info.get("severity",    "HIGH")
                payload  = threat_info.get("payload",     {})
                sev_col  = {"LOW":"yellow","MEDIUM":"yellow","HIGH":"red","CRITICAL":"bold red"}.get(severity,"red")

                console.print()
                console.print(Panel(
                    f"[bold red]\u26a0  INTRUSION DETECTED \u2014 {node_id}[/bold red]\n\n"
                    f"  Threat     : [{sev_col}]{t_label}[/{sev_col}]\n"
                    f"  Severity   : [{sev_col}]{severity}[/{sev_col}]\n"
                    f"  ML Score   : [red]{score:.4f}[/red]\n\n"
                    f"  Payload:\n"
                    f"    CPU    {payload.get('cpu_actual','?'):>6}%  baseline {payload.get('cpu_baseline','?')}%  [{sev_col}]{payload.get('cpu_sigma','?')}[/{sev_col}]\n"
                    f"    MEM    {payload.get('mem_actual','?'):>6}%  baseline {payload.get('mem_baseline','?')}%  [{sev_col}]{payload.get('mem_sigma','?')}[/{sev_col}]\n"
                    f"    PROCS  {payload.get('procs_actual','?'):>6}   baseline {payload.get('procs_baseline','?')}    [{sev_col}]{payload.get('procs_sigma','?')}[/{sev_col}]\n"
                    f"    NET PKT deviation  [{sev_col}]{payload.get('pkt_sigma','?')}[/{sev_col}]\n"
                    f"    NET BYT deviation  [{sev_col}]{payload.get('byt_sigma','?')}[/{sev_col}]\n"
                    f"    DISK    deviation  [{sev_col}]{payload.get('disk_sigma','?')}[/{sev_col}]\n\n"
                    f"  [dim]Warning {warning}/{QUARANTINE_AT}[/dim]",
                    border_style="red", expand=False
                ))

                # Evidence chain
                cid = None
                tx  = None

                with console.status("[yellow]  Pinning evidence to IPFS...[/yellow]"):
                    try:
                        from core.pinata import pin_json, gateway_url
                        evidence = {**metrics, "verdict":"anomaly",
                                    "ml_score":score, "threat_type":t_type,
                                    "threat_label":t_label, "severity":severity,
                                    "payload":payload}
                        cid = pin_json(evidence, f"THREAT-{node_id}-{t_type}")
                        console.print(f"  [green]\u2713[/green] IPFS: [cyan]{cid}[/cyan]")
                        console.print(f"       [dim]{gateway_url(cid)}[/dim]")
                    except Exception as e:
                        console.print(f"  [red]\u2717 IPFS: {e}[/red]")
                        cid = f"QmOFFLINE{abs(hash(str(metrics)))%10**10}"

                with console.status("[yellow]  Logging on Aptos testnet...[/yellow]"):
                    try:
                        from core.aptos_direct import log_threat, explorer_url
                        tx = log_threat(node_id, cid, t_type)
                        console.print(f"  [green]\u2713[/green] TX:   [cyan]{tx}[/cyan]")
                        console.print(f"       [dim]{explorer_url(tx)}[/dim]")
                    except Exception as e:
                        console.print(f"  [red]\u2717 Aptos: {e}[/red]")
                        tx = f"0xOFFLINE{abs(hash(cid))%10**10:010x}"

                # ZK proof
                try:
                    from core.zk import generate_proof
                    zk = generate_proof(metrics, score, cid)
                    console.print(f"  [green]\u2713[/green] ZK:   [cyan]{zk['proof_hash'][:40]}[/cyan]  method={zk['method']}")
                except Exception as e:
                    console.print(f"  [yellow]  ZK skipped: {e}[/yellow]")
                    zk = {"proof_hash": "unavailable", "method": "none"}

                # Supabase
                try:
                    from core.db import log_event, upsert_node
                    log_event(metrics, "anomaly", score, ipfs_cid=cid, aptos_tx=tx,
                              threat_type=t_type, threat_label=t_label,
                              severity=severity, zk_proof=zk.get("proof_hash"))
                    upsert_node(node_id, metrics["ip"],
                                "warning" if warning < QUARANTINE_AT else "compromised")
                except Exception:
                    pass

                state["last_threat"] = {"type":t_type,"cid":cid,"tx":tx,"at":metrics["timestamp"]}
                state["threat_count"] = state.get("threat_count",0) + 1

                if warning >= QUARANTINE_AT:
                    state["status"] = "COMPROMISED"
                    _save_state(state)
                    console.print()
                    console.print(Panel(
                        f"[bold red]NODE QUARANTINED \u2014 {node_id}[/bold red]\n\n"
                        f"[red]{QUARANTINE_AT} consecutive anomalies. Threat confirmed.[/red]\n\n"
                        f"  Evidence:\n"
                        f"    IPFS : [cyan]{cid}[/cyan]\n"
                        f"    Aptos: [cyan]{tx}[/cyan]\n"
                        f"    ZK   : [cyan]{zk.get('proof_hash','?')[:40]}[/cyan]\n\n"
                        f"  Network after quarantine:\n"
                        f"    [green]\u25cf node-2[/green]  online \u2014 taking over\n"
                        f"    [green]\u25cf node-3[/green]  online \u2014 taking over\n"
                        f"    [red]\u2715 {node_id}[/red]  DISCONNECTED\n\n"
                        f"[dim]Dashboard P2P diagram now shows severed edges.[/dim]",
                        border_style="red", expand=False
                    ))
                    sys.exit(0)

                _save_state(state)

            time.sleep(5)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped.[/yellow]")

# ── ML TEST ──────────────────────────────────────────────────────────────────────
def cmd_test():
    """Full ML test — scenarios + live reading + payload detail."""
    from core.ml_detector import detect, load_baseline, THREAT_CATALOGUE, _rf_enabled
    from core.monitor     import get_metrics

    baseline = load_baseline()

    console.print(Panel(
        "[bold cyan]CyberShield \u2014 ML Test[/bold cyan]\n"
        "[dim]No network calls. Pure local ML test.[/dim]",
        expand=False
    ))

    # Show which model is active
    if _rf_enabled:
        console.print("[green]\u2713 Random Forest (CICIDS2017) \u2014 active[/green]")
    else:
        console.print("[yellow]\u25cf Rate-based spike detector \u2014 active (RF unavailable)[/yellow]")
        console.print("[dim]  To enable RF: pip install scikit-learn==1.6.1[/dim]")

    # Show baseline
    console.print(f"\n[bold]Your machine baseline:[/bold]")
    bl_tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    bl_tbl.add_column("Metric");  bl_tbl.add_column("Normal Mean"); bl_tbl.add_column("\u00b1 Std Dev")
    bl_tbl.add_row("CPU %",    f"{baseline['cpu_mean']:.1f}%",  f"\u00b1{baseline['cpu_std']:.1f}")
    bl_tbl.add_row("Memory %", f"{baseline['mem_mean']:.1f}%",  f"\u00b1{baseline['mem_std']:.1f}")
    bl_tbl.add_row("Processes",f"{baseline['prc_mean']:.0f}",   f"\u00b1{baseline['prc_std']:.0f}")
    bl_tbl.add_row("Net Pkts", f"{baseline['pkt_mean']:.0f}",   f"\u00b1{baseline['pkt_std']:.0f}")
    bl_tbl.add_row("Net Bytes",f"{baseline['byt_mean']:.0f}",   f"\u00b1{baseline['byt_std']:.0f}")
    console.print(bl_tbl)

    # Build test scenarios scaled to YOUR baseline
    cpu_n  = baseline["cpu_mean"];  cpu_s  = baseline["cpu_std"]
    mem_n  = baseline["mem_mean"];  mem_s  = baseline["mem_std"]
    prc_n  = baseline["prc_mean"];  prc_s  = baseline["prc_std"]
    pkt_n  = baseline["pkt_mean"];  pkt_s  = baseline["pkt_std"]
    byt_n  = baseline["byt_mean"];  byt_s  = baseline["byt_std"]

    BASE_ROW = {
        "node_id": "test", "ip": "127.0.0.1",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "disk_percent": baseline.get("disk_mean", 70),
        "net_connections": 50, "swap_percent": 10,
        "cpu_freq_mhz": 2400, "cpu_temp": 45,
        "net_bytes_sent": byt_n, "net_packets_sent": pkt_n,
    }

    SCENARIOS = [
        {
            "name": "Idle system",
            "desc": "Your normal baseline \u2014 should be SAFE",
            "data": {**BASE_ROW,
                "cpu_percent": cpu_n, "memory_percent": mem_n,
                "process_count": int(prc_n), "net_packets_recv": pkt_n,
                "net_bytes_recv": byt_n},
        },
        {
            "name": "CPU stress (DoS)",
            "desc": "stress --cpu 8 \u2192 CPU spikes 6\u03c3 above your normal",
            "data": {**BASE_ROW,
                "cpu_percent": min(cpu_n + cpu_s*6, 99),
                "memory_percent": mem_n, "process_count": int(prc_n)+20,
                "net_packets_recv": pkt_n, "net_bytes_recv": byt_n},
        },
        {
            "name": "nmap port scan",
            "desc": "nmap -sV \u2192 huge packet count, low bytes",
            "data": {**BASE_ROW,
                "cpu_percent": cpu_n+8, "memory_percent": mem_n,
                "process_count": int(prc_n)+15,
                "net_packets_recv": pkt_n + pkt_s*8,
                "net_bytes_recv":   byt_n + byt_s*0.3,
                "net_connections": 900},
        },
        {
            "name": "hping3 flood",
            "desc": "hping3 --flood \u2192 high bytes AND packets",
            "data": {**BASE_ROW,
                "cpu_percent": cpu_n+20, "memory_percent": mem_n,
                "process_count": int(prc_n)+5,
                "net_packets_recv": pkt_n + pkt_s*7,
                "net_bytes_recv":   byt_n + byt_s*7},
        },
        {
            "name": "Memory exhaustion",
            "desc": "memory bomb \u2192 MEM spikes (already high at 94%, watches delta)",
            "data": {**BASE_ROW,
                "cpu_percent": cpu_n+5,
                "memory_percent": min(mem_n + mem_s*4, 99.5),
                "process_count": int(prc_n)+30,
                "net_packets_recv": pkt_n, "net_bytes_recv": byt_n,
                "swap_percent": 80},
        },
        {
            "name": "Combined APT",
            "desc": "All vectors simultaneously \u2014 worst case",
            "data": {**BASE_ROW,
                "cpu_percent": min(cpu_n + cpu_s*6, 99),
                "memory_percent": min(mem_n + mem_s*3, 99),
                "process_count": int(prc_n + prc_s*6),
                "net_packets_recv": pkt_n + pkt_s*6,
                "net_bytes_recv":   byt_n + byt_s*5,
                "disk_percent": 95, "net_connections": 800},
        },
    ]

    # ── Run scenarios ─────────────────────────────────────────────────────────
    console.print("\n[bold]Scenario Tests:[/bold]")
    results = []
    for sc in SCENARIOS:
        r = detect(sc["data"])
        verdict, score = r[0], r[1]
        ti = r[2] if len(r) > 2 else {}
        results.append((sc, verdict, score, ti))

    # Summary table
    tbl = Table(box=box.ROUNDED, header_style="bold", show_lines=True)
    tbl.add_column("Scenario",      min_width=20)
    tbl.add_column("Verdict",       min_width=9,  justify="center")
    tbl.add_column("Score",         min_width=8,  justify="right")
    tbl.add_column("Threat",        min_width=30)
    tbl.add_column("Severity",      min_width=10, justify="center")
    tbl.add_column("Max \u03c3",         min_width=7,  justify="right")

    for sc, verdict, score, ti in results:
        v_col = "green" if verdict == "safe" else "red"
        s_col = {"LOW":"yellow","MEDIUM":"yellow","HIGH":"red","CRITICAL":"bold red"}.get(
            ti.get("severity",""), "dim")
        tbl.add_row(
            sc["name"],
            f"[{v_col}]{verdict.upper()}[/{v_col}]",
            f"[{v_col}]{score:.4f}[/{v_col}]",
            ti.get("threat_label", "[dim]\u2014[/dim]"),
            f"[{s_col}]{ti.get('severity','\u2014')}[/{s_col}]" if ti else "\u2014",
            ti.get("payload",{}).get("max_deviation","\u2014") if ti else "\u2014",
        )
    console.print(tbl)

    # Detailed payload for each anomaly
    console.print("\n[bold]Full Payload Analysis (anomalies):[/bold]")
    any_anomaly = False
    for sc, verdict, score, ti in results:
        if verdict != "anomaly":
            continue
        any_anomaly = True
        p = ti.get("payload", {})
        console.print(Panel(
            f"[bold red]{sc['name']}[/bold red]\n"
            f"[dim]{sc['desc']}[/dim]\n\n"
            f"  Threat   : [red]{ti.get('threat_label','?')}[/red]\n"
            f"  Severity : [red]{ti.get('severity','?')}[/red]\n"
            f"  Score    : {score:.4f}\n\n"
            f"  [bold]Metric Deviations from YOUR baseline:[/bold]\n"
            f"  CPU    {p.get('cpu_actual','?'):>6}%   your_normal={p.get('cpu_baseline','?')}%   [red]{p.get('cpu_sigma','?')}[/red]\n"
            f"  MEM    {p.get('mem_actual','?'):>6}%   your_normal={p.get('mem_baseline','?')}%   [red]{p.get('mem_sigma','?')}[/red]\n"
            f"  PROCS  {p.get('procs_actual','?'):>6}    your_normal={p.get('procs_baseline','?')}    [red]{p.get('procs_sigma','?')}[/red]\n"
            f"  NET PKT deviation  [red]{p.get('pkt_sigma','?')}[/red]\n"
            f"  NET BYT deviation  [red]{p.get('byt_sigma','?')}[/red]\n"
            f"  DISK    deviation  [red]{p.get('disk_sigma','?')}[/red]\n"
            f"  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n"
            f"  MAX DEVIATION: [bold red]{p.get('max_deviation','?')}[/bold red]",
            border_style="red", expand=False
        ))
    if not any_anomaly:
        console.print("[yellow]  All scenarios showed SAFE \u2014 check baseline calibration[/yellow]")
        console.print("[yellow]  Run: python cli.py calibrate[/yellow]")

    # ── Live reading ──────────────────────────────────────────────────────────
    console.print("\n[bold]Live Machine Reading NOW:[/bold]")
    live = get_metrics()
    lr   = detect(live)
    lv, ls = lr[0], lr[1]
    lt     = lr[2] if len(lr) > 2 else {}
    lv_col = "green" if lv == "safe" else "red"

    lt_tbl = Table(box=box.SIMPLE, show_header=False)
    lt_tbl.add_column("Metric",  style="cyan", min_width=18)
    lt_tbl.add_column("Value")
    lt_tbl.add_row("CPU",         f"[{lv_col}]{live['cpu_percent']:.1f}%[/{lv_col}]")
    lt_tbl.add_row("Memory",      f"[{lv_col}]{live['memory_percent']:.1f}%[/{lv_col}]")
    lt_tbl.add_row("Processes",   f"[{lv_col}]{live['process_count']}[/{lv_col}]")
    lt_tbl.add_row("Swap",        f"{live.get('swap_percent',0):.1f}%")
    lt_tbl.add_row("Disk %",      f"{live.get('disk_percent',0):.0f}%")
    lt_tbl.add_row("Net recv",    f"{live.get('net_bytes_recv',0):,} bytes")
    lt_tbl.add_row("Net packets", f"{live.get('net_packets_recv',0):,}")
    lt_tbl.add_row("Net conns",   f"{live.get('net_connections',0)}")
    lt_tbl.add_row("CPU freq",    f"{live.get('cpu_freq_mhz',0):.0f} MHz")
    lt_tbl.add_row("ML score",    f"[{lv_col}]{ls:.4f}[/{lv_col}]")
    lt_tbl.add_row("Verdict",     f"[{lv_col}]{lv.upper()}[/{lv_col}]")
    if lt:
        lt_tbl.add_row("Threat",  f"[red]{lt.get('threat_label','?')}[/red]")
        lt_tbl.add_row("Severity",f"[red]{lt.get('severity','?')}[/red]")
    console.print(lt_tbl)

# ── DASHBOARD ────────────────────────────────────────────────────────────────────
def cmd_dashboard():
    from dashboard.server import start
    start()

# ── STATUS ───────────────────────────────────────────────────────────────────────
def cmd_status():
    state = _load_state()
    if not state:
        console.print("[red]No node registered.[/red]")
        return

    t = Table(box=box.ROUNDED, show_header=False)
    t.add_column("Key", style="cyan")
    t.add_column("Value")

    for k, v in state.items():
        t.add_row(k, str(v))

    console.print(Panel(t, title="[cyan]Node Status[/cyan]", border_style="cyan"))

# ── ENTRY ────────────────────────────────────────────────────────────────────────
HELP = """
[bold cyan]CyberShield CLI[/bold cyan]

  [green]python cli.py calibrate[/green]   sample machine, build ML baseline  \u2190 run FIRST
  [green]python cli.py train[/green]       train model on baseline
  [green]python cli.py register[/green]    register node on IPFS + Aptos
  [green]python cli.py monitor[/green]     start real-time monitoring
  [green]python cli.py test[/green]        test ML detection (full detail)
  [green]python cli.py dashboard[/green]   start web dashboard
  [green]python cli.py status[/green]      show node state
"""

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    {
        "calibrate": cmd_calibrate,
        "train"    : cmd_train,
        "register" : cmd_register,
        "monitor"  : cmd_monitor,
        "test"     : cmd_test,
        "dashboard": cmd_dashboard,
        "status"   : cmd_status,
    }.get(cmd, lambda: console.print(HELP))()
