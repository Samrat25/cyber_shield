# cybershield/commands/attack.py
import click
import time
import multiprocessing
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


@click.group()
def attack():
    """Attack simulation for testing (use responsibly!)."""
    pass


def cpu_stress(duration):
    """CPU stress function."""
    end_time = time.time() + duration
    while time.time() < end_time:
        # Intensive computation
        _ = sum([i**2 for i in range(10000)])


def memory_stress(duration, size_mb=100):
    """Memory stress function."""
    data = []
    end_time = time.time() + duration
    while time.time() < end_time:
        # Allocate memory
        data.append(np.random.rand(1024, 1024))  # ~8MB per array
        if len(data) > size_mb // 8:
            data.pop(0)
        time.sleep(0.1)


def network_stress(duration):
    """Network stress function."""
    import socket
    end_time = time.time() + duration
    sockets = []
    
    try:
        while time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("8.8.8.8", 80))
                sockets.append(s)
                time.sleep(0.01)
            except Exception:
                pass
    finally:
        for s in sockets:
            try:
                s.close()
            except Exception:
                pass


@attack.command()
@click.option('--type', 'attack_type', 
              type=click.Choice(['cpu', 'memory', 'network', 'combined']),
              default='cpu',
              help='Type of attack to simulate')
@click.option('--duration', default=30, help='Duration in seconds')
@click.option('--intensity', default=8, help='Intensity level (1-16)')
def simulate(attack_type, duration, intensity):
    """
    Simulate various types of attacks for testing.
    
    WARNING: This will stress your system! Use for testing only.
    """
    console.print(Panel(
        f"[bold yellow]⚠ Attack Simulation[/bold yellow]\n\n"
        f"Type: [cyan]{attack_type}[/cyan]\n"
        f"Duration: [cyan]{duration}s[/cyan]\n"
        f"Intensity: [cyan]{intensity}[/cyan]\n\n"
        f"[red]This will stress your system![/red]",
        border_style="yellow",
        expand=False
    ))
    
    if not click.confirm("\nProceed with simulation?"):
        return
    
    console.print(f"\n[yellow]Starting {attack_type} attack simulation...[/yellow]\n")
    
    processes = []
    
    try:
        if attack_type == 'cpu' or attack_type == 'combined':
            console.print(f"  [red]→[/red] Launching CPU stress ({intensity} processes)")
            for _ in range(intensity):
                p = multiprocessing.Process(target=cpu_stress, args=(duration,))
                p.start()
                processes.append(p)
        
        if attack_type == 'memory' or attack_type == 'combined':
            console.print(f"  [red]→[/red] Launching memory stress")
            p = multiprocessing.Process(target=memory_stress, args=(duration, intensity * 50))
            p.start()
            processes.append(p)
        
        if attack_type == 'network' or attack_type == 'combined':
            console.print(f"  [red]→[/red] Launching network stress")
            for _ in range(min(intensity, 4)):
                p = multiprocessing.Process(target=network_stress, args=(duration,))
                p.start()
                processes.append(p)
        
        console.print(f"\n[yellow]Attack running for {duration} seconds...[/yellow]")
        console.print("[dim]Monitor your CyberShield node to see detection in action![/dim]\n")
        
        # Wait with progress bar
        with Progress() as progress:
            task = progress.add_task("[red]Simulating attack...", total=duration)
            for _ in range(duration):
                time.sleep(1)
                progress.update(task, advance=1)
        
        console.print("\n[green]✓ Simulation complete[/green]")
        console.print("[dim]Waiting for processes to terminate...[/dim]\n")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Simulation interrupted[/yellow]")
    
    finally:
        # Clean up processes
        for p in processes:
            p.terminate()
            p.join(timeout=2)
            if p.is_alive():
                p.kill()


@attack.command()
def patterns():
    """Show common attack patterns that CyberShield can detect."""
    console.print(Panel("[bold cyan]Detectable Attack Patterns[/bold cyan]", expand=False))
    
    patterns = [
        ("CPU Spike", "Sudden increase in CPU usage (>80%)", "Cryptomining, DoS"),
        ("Memory Exhaustion", "Rapid memory consumption", "Memory bombs, leaks"),
        ("Network Flood", "Unusual network traffic volume", "DDoS, data exfiltration"),
        ("Process Spawn", "Abnormal process creation rate", "Fork bombs, malware"),
        ("Disk I/O Spike", "Excessive disk read/write", "Ransomware, data theft"),
        ("Combined Attack", "Multiple metrics anomalous", "Advanced persistent threats"),
    ]
    
    console.print()
    for name, description, examples in patterns:
        console.print(f"  [cyan]●[/cyan] [bold]{name}[/bold]")
        console.print(f"    {description}")
        console.print(f"    [dim]Examples: {examples}[/dim]\n")
