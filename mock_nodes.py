# mock_nodes.py — ONLY this file is mocked
# Simulates Node-2 and Node-3 being part of the network
# Run: python3 mock_nodes.py   in a separate terminal during demo

import time, random
from rich.console import Console
from rich.table   import Table
from rich.live    import Live
from rich         import box

console = Console()

NODES = [
    {"id": "node-2", "ip": "192.168.1.102"},
    {"id": "node-3", "ip": "192.168.1.103"},
]

def row(n):
    return {
        "cpu"   : round(random.uniform(9,  28),  1),
        "mem"   : round(random.uniform(42, 61),  1),
        "procs" : random.randint(115, 162),
        "net"   : f"{random.randint(180, 750)} KB/s",
    }

def table(tick):
    t = Table(
        title=f"[cyan]CyberShield — Mock Network Peers  [tick {tick}][/cyan]",
        box=box.ROUNDED, show_header=True, header_style="bold"
    )
    t.add_column("Node",    style="cyan",  min_width=10)
    t.add_column("IP",      style="white", min_width=15)
    t.add_column("CPU %",   justify="right", min_width=7)
    t.add_column("MEM %",   justify="right", min_width=7)
    t.add_column("Procs",   justify="right", min_width=7)
    t.add_column("Net",     min_width=10)
    t.add_column("Status",  min_width=12)
    for n in NODES:
        m = row(n)
        t.add_row(
            n["id"], n["ip"],
            f"[green]{m['cpu']}[/green]",
            f"[green]{m['mem']}[/green]",
            f"[green]{m['procs']}[/green]",
            f"[green]{m['net']}[/green]",
            "[green]● SAFE[/green]"
        )
    return t

if __name__ == "__main__":
    console.print("[bold]Mock peer nodes active. Keep this visible during demo.[/bold]\n")
    tick = 0
    with Live(table(tick), refresh_per_second=0.4, console=console) as live:
        while True:
            time.sleep(2.5)
            tick += 1
            live.update(table(tick))
