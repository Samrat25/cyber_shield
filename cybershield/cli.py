#!/usr/bin/env python3
# cybershield/cli.py
"""
CyberShield CLI - Production-ready command-line interface
"""

import click
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .commands import node, network, ml, attack, status

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


# Register command groups
main.add_command(node.node)
main.add_command(network.network)
main.add_command(ml.ml)
main.add_command(attack.attack)
main.add_command(status.status)


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
        "[yellow]Step 1:[/yellow] Configure your environment\n"
        "  $ cybershield node init\n\n"
        "[yellow]Step 2:[/yellow] Train ML models\n"
        "  $ cybershield ml train --advanced\n\n"
        "[yellow]Step 3:[/yellow] Register on blockchain\n"
        "  $ cybershield node register\n\n"
        "[yellow]Step 4:[/yellow] Start monitoring\n"
        "  $ cybershield node monitor\n\n"
        "[yellow]Step 5:[/yellow] (Optional) Connect to network\n"
        "  $ cybershield network connect <peer-address>\n\n"
        "[green]For testing:[/green]\n"
        "  $ cybershield attack simulate --type cpu\n",
        border_style="cyan",
        expand=False
    ))


if __name__ == "__main__":
    main()
