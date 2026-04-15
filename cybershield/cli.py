#!/usr/bin/env python3
# cybershield/cli.py
"""
CyberShield CLI - Production-ready command-line interface with enhanced UI
"""

import click
import sys
from rich.console import Console

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="1.0.0")
def main(ctx):
    """
    CyberShield - Blockchain-based Distributed Intrusion Detection System
    
    A production-ready security platform combining:
    • Advanced ML ensemble for threat detection
    • Real P2P network for distributed monitoring
    • Blockchain verification on Aptos
    • IPFS for immutable evidence storage
    • Phishing detection and URL analysis
    • Interactive security awareness training
    """
    # Show banner if no command is provided
    if ctx.invoked_subcommand is None:
        from .ui.banner import show_banner, show_loading
        show_banner()
        show_loading("Initializing CyberShield", duration=1.5, steps=[
            "Loading security modules",
            "Initializing components",
            "Ready"
        ])
        console.print("[dim]Type 'cybershield --help' for available commands[/dim]\n")


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
    from .commands.phishing import phishing
    from .commands.awareness import awareness
    
    main.add_command(node)
    main.add_command(network)
    main.add_command(ml)
    main.add_command(status)
    main.add_command(dashboard)
    main.add_command(api)
    main.add_command(phishing)
    main.add_command(awareness)


@main.command()
def version():
    """Show version information with animated banner."""
    from .ui.banner import show_banner, show_info
    
    show_banner()
    show_info("CyberShield v1.0.0 - Production-ready distributed IDS")


@main.command()
def quickstart():
    """Quick setup guide for new users."""
    from .ui.banner import show_banner, show_command_header
    from rich.panel import Panel
    
    show_banner(clear_screen=True)
    show_command_header("Quick Start Guide", "Get started with CyberShield in 5 steps")
    
    console.print(Panel(
        "[bold cyan]CyberShield Quick Start Guide[/bold cyan]\n\n"
        "[yellow]Step 1:[/yellow] Initialize node\n"
        "  [dim]$[/dim] [green]cybershield node init[/green]\n\n"
        "[yellow]Step 2:[/yellow] Register on blockchain\n"
        "  [dim]$[/dim] [green]cybershield node register[/green]\n\n"
        "[yellow]Step 3:[/yellow] Start monitoring\n"
        "  [dim]$[/dim] [green]cybershield node monitor[/green]\n\n"
        "[yellow]Step 4:[/yellow] View dashboard\n"
        "  [dim]$[/dim] [green]cybershield dashboard[/green]\n\n"
        "[yellow]Step 5:[/yellow] (Optional) Start P2P listener\n"
        "  [dim]$[/dim] [green]cybershield network listen[/green]\n\n"
        "[bold red]Security Features:[/bold red]\n"
        "  • [cyan]Phishing detection:[/cyan] cybershield phishing check --url <URL>\n"
        "  • [cyan]ML detection:[/cyan] cybershield ml detect --data <file>\n"
        "  • [cyan]Awareness quiz:[/cyan] cybershield awareness quiz\n\n"
        "[bold red]For attack testing:[/bold red]\n"
        "  Use Kali Linux VM with real attack tools (nmap, hping3, stress)\n",
        border_style="red",
        expand=False
    ))


def cli():
    """Entry point that registers commands lazily."""
    _register_commands()
    main()


if __name__ == "__main__":
    cli()
