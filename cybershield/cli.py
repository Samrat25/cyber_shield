#!/usr/bin/env python3
# cybershield/cli.py
"""
CyberShield CLI - Production-ready command-line interface
"""

import click
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗██╗  ██╗  ║
║  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║  ║
║  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████╗███████║  ║
║  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══██║  ║
║  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████║██║  ██║  ║
║   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ║
║                                                               ║
║  Blockchain-Based Distributed Intrusion Detection System     ║
║  Version 1.0.0                                                ║
╚═══════════════════════════════════════════════════════════════╝
"""


@click.group()
@click.version_option(version="1.0.0")
def main():
    """
    CyberShield - Blockchain-based Distributed Intrusion Detection System
    
    A production-ready security platform combining:
    • Advanced ML ensemble for threat detection
    • Real P2P network for distributed monitoring
    • Blockchain verification on Aptos
    • IPFS for immutable evidence storage
    """
    pass


# LAZY LOADING - Import commands only when main() is called
# This prevents loading sklearn at module import time
def _register_commands():
    """Register all command groups - called after main() starts."""
    from .commands.node import node
    from .commands.network import network
    from .commands.ml import ml
    from .commands.status import status
    from .commands.dashboard import dashboard
    from .commands.api import api
    
    main.add_command(node)
    main.add_command(network)
    main.add_command(ml)
    main.add_command(status)
    main.add_command(dashboard)
    main.add_command(api)


@main.command()
def version():
    """Show version information."""
    console.print(BANNER, style="cyan")
    console.print("\n[green]✓[/green] CyberShield v1.0.0")
    console.print("[dim]Production-ready distributed IDS[/dim]\n")


@main.command()
def quickstart():
    """Quick setup guide for new users."""
    console.print(Panel(
        "[bold cyan]CyberShield Quick Start Guide[/bold cyan]\n\n"
        "[yellow]Step 1:[/yellow] Initialize node\n"
        "  $ cybershield node init\n\n"
        "[yellow]Step 2:[/yellow] Register on blockchain\n"
        "  $ cybershield node register\n\n"
        "[yellow]Step 3:[/yellow] Start monitoring\n"
        "  $ cybershield node monitor\n\n"
        "[yellow]Step 4:[/yellow] View dashboard\n"
        "  $ cybershield dashboard\n\n"
        "[yellow]Step 5:[/yellow] (Optional) Start P2P listener\n"
        "  $ cybershield network listen\n\n"
        "[green]For attack testing:[/green]\n"
        "  Use Kali Linux VM with real attack tools (nmap, hping3, stress)\n",
        border_style="cyan",
        expand=False
    ))


def cli():
    """Entry point that registers commands lazily."""
    _register_commands()
    main()


if __name__ == "__main__":
    cli()
