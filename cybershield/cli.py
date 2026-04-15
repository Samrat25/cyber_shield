#!/usr/bin/env python3
# cybershield/cli.py
"""
CyberShield CLI - Production-ready command-line interface with enhanced UI
"""

import click
import sys
from rich.console import Console

console = Console()


class CustomHelpFormatter(click.Context):
    """Custom context that shows beautiful help."""
    def get_help(self):
        from .ui.banner import show_banner
        from rich.panel import Panel
        from rich import box
        
        show_banner()
        
        console.print(Panel(
            "[bold cyan]🛡️  CyberShield Commands[/bold cyan]\n\n"
            "[yellow]📦 Node Management:[/yellow]\n"
            "  [green]node init[/green]      - Initialize your security node\n"
            "  [green]node register[/green]  - Register on blockchain & IPFS\n"
            "  [green]node monitor[/green]   - Start real-time threat monitoring\n\n"
            "[yellow]🌐 Network:[/yellow]\n"
            "  [green]network listen[/green]  - Start P2P server for peers\n"
            "  [green]network connect[/green] - Connect to remote peer\n\n"
            "[yellow]🔒 Security Features:[/yellow]\n"
            "  [green]phishing check[/green]  - Detect phishing URLs\n"
            "  [green]awareness quiz[/green]  - Security training quiz\n"
            "  [green]ml train[/green]        - Train ML detection model\n"
            "  [green]ml detect[/green]       - Run threat detection\n\n"
            "[yellow]📊 Dashboard & Status:[/yellow]\n"
            "  [green]dashboard[/green]       - Launch web interface\n"
            "  [green]status[/green]          - Show system status\n"
            "  [green]api[/green]             - Start REST API server\n\n"
            "[yellow]ℹ️  Information:[/yellow]\n"
            "  [green]version[/green]         - Show version information\n"
            "  [green]quickstart[/green]      - Quick setup guide\n\n"
            "[bold white]Usage Examples:[/bold white]\n"
            "  [dim]$[/dim] cybershield node init\n"
            "  [dim]$[/dim] cybershield node monitor\n"
            "  [dim]$[/dim] cybershield dashboard\n"
            "  [dim]$[/dim] cybershield phishing check --url <URL>\n\n"
            "[dim]For detailed help on any command:[/dim]\n"
            "  [dim]$[/dim] cybershield [cyan]<command>[/cyan] --help",
            border_style="red",
            box=box.DOUBLE
        ))
        console.print()
        return ""


@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
@click.version_option(version="1.0.0")
@click.option('--help', '-h', is_flag=True, help='Show this message and exit')
def main(ctx, help):
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
    # Show custom help if --help flag is used
    if help:
        from .ui.banner import show_banner
        from rich.panel import Panel
        from rich import box
        
        show_banner()
        
        console.print(Panel(
            "[bold cyan]🛡️  CyberShield Commands[/bold cyan]\n\n"
            "[yellow]📦 Node Management:[/yellow]\n"
            "  [green]node init[/green]      - Initialize your security node\n"
            "  [green]node register[/green]  - Register on blockchain & IPFS\n"
            "  [green]node monitor[/green]   - Start real-time threat monitoring\n\n"
            "[yellow]🌐 Network:[/yellow]\n"
            "  [green]network listen[/green]  - Start P2P server for peers\n"
            "  [green]network connect[/green] - Connect to remote peer\n\n"
            "[yellow]🔒 Security Features:[/yellow]\n"
            "  [green]phishing check[/green]  - Detect phishing URLs\n"
            "  [green]awareness quiz[/green]  - Security training quiz\n"
            "  [green]ml train[/green]        - Train ML detection model\n"
            "  [green]ml detect[/green]       - Run threat detection\n\n"
            "[yellow]📊 Dashboard & Status:[/yellow]\n"
            "  [green]dashboard[/green]       - Launch web interface\n"
            "  [green]status[/green]          - Show system status\n"
            "  [green]api[/green]             - Start REST API server\n\n"
            "[yellow]ℹ️  Information:[/yellow]\n"
            "  [green]version[/green]         - Show version information\n"
            "  [green]quickstart[/green]      - Quick setup guide\n\n"
            "[bold white]Usage Examples:[/bold white]\n"
            "  [dim]$[/dim] cybershield node init\n"
            "  [dim]$[/dim] cybershield node monitor\n"
            "  [dim]$[/dim] cybershield dashboard\n"
            "  [dim]$[/dim] cybershield phishing check --url <URL>\n\n"
            "[dim]For detailed help on any command:[/dim]\n"
            "  [dim]$[/dim] cybershield [cyan]<command>[/cyan] --help",
            border_style="red",
            box=box.DOUBLE
        ))
        console.print()
        ctx.exit()
    
    # Show banner if no command is provided
    if ctx.invoked_subcommand is None:
        from .ui.banner import show_banner, show_loading
        from rich.panel import Panel
        from rich import box
        
        show_banner()
        show_loading("Initializing CyberShield", duration=1.5, steps=[
            "Loading security modules",
            "Initializing components",
            "Ready"
        ])
        
        console.print(Panel(
            "[bold cyan]🛡️  Available Commands[/bold cyan]\n\n"
            "[yellow]Node Management:[/yellow]\n"
            "  [green]init[/green]      - Initialize your security node\n"
            "  [green]register[/green]  - Register on blockchain\n"
            "  [green]monitor[/green]   - Start real-time monitoring\n\n"
            "[yellow]Network:[/yellow]\n"
            "  [green]listen[/green]    - Start P2P server\n"
            "  [green]connect[/green]   - Connect to peer\n\n"
            "[yellow]Security:[/yellow]\n"
            "  [green]phishing[/green]  - URL phishing detection\n"
            "  [green]awareness[/green] - Security training quiz\n"
            "  [green]ml[/green]        - Machine learning detection\n\n"
            "[yellow]Dashboard:[/yellow]\n"
            "  [green]dashboard[/green] - Launch web interface\n\n"
            "[dim]Type 'cybershield <command> --help' for more information[/dim]",
            border_style="red",
            box=box.DOUBLE
        ))
        console.print()


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
    from .ui.banner import show_banner
    from rich.panel import Panel
    from rich import box
    
    show_banner()
    
    console.print(Panel(
        "[bold cyan]CyberShield Version Information[/bold cyan]\n\n"
        "[white]Version:[/white] [bold green]1.0.0[/bold green]\n"
        "[white]Release:[/white] [bold yellow]Production[/bold yellow]\n"
        "[white]Build Date:[/white] [dim]April 2026[/dim]\n\n"
        "[bold red]Features:[/bold red]\n"
        "  ✓ ML-based threat detection\n"
        "  ✓ P2P distributed monitoring\n"
        "  ✓ Blockchain verification (Aptos)\n"
        "  ✓ IPFS evidence storage\n"
        "  ✓ Phishing detection\n"
        "  ✓ Security awareness training\n"
        "  ✓ Real-time dashboard\n\n"
        "[dim]For more info: https://github.com/yourusername/cybershield[/dim]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()


@main.command()
def quickstart():
    """Quick setup guide for new users."""
    from .ui.banner import show_banner, show_command_header, show_loading
    from rich.panel import Panel
    from rich import box
    
    show_banner(clear_screen=True)
    show_command_header("Quick Start Guide", "Get started with CyberShield in 5 easy steps")
    show_loading("Preparing guide", duration=1.0, steps=[
        "Loading documentation",
        "Preparing examples"
    ])
    
    console.print(Panel(
        "[bold cyan]🚀 CyberShield Quick Start Guide[/bold cyan]\n\n"
        "[bold yellow]Step 1: Initialize Node[/bold yellow]\n"
        "  [dim]$[/dim] [green]cybershield node init[/green]\n"
        "  [dim]Creates your security node configuration[/dim]\n\n"
        "[bold yellow]Step 2: Register on Blockchain[/bold yellow]\n"
        "  [dim]$[/dim] [green]cybershield node register[/green]\n"
        "  [dim]Registers node on Aptos blockchain and IPFS[/dim]\n\n"
        "[bold yellow]Step 3: Start Monitoring[/bold yellow]\n"
        "  [dim]$[/dim] [green]cybershield node monitor[/green]\n"
        "  [dim]Begins real-time threat detection[/dim]\n\n"
        "[bold yellow]Step 4: Launch Dashboard[/bold yellow]\n"
        "  [dim]$[/dim] [green]cybershield dashboard[/green]\n"
        "  [dim]Opens web interface at http://localhost:7000[/dim]\n\n"
        "[bold yellow]Step 5: Start P2P Server (Optional)[/bold yellow]\n"
        "  [dim]$[/dim] [green]cybershield network listen --port 8765[/green]\n"
        "  [dim]Enables peer-to-peer network monitoring[/dim]\n\n"
        "[bold red]🔒 Security Features:[/bold red]\n"
        "  • [cyan]Phishing Detection:[/cyan] cybershield phishing check --url <URL>\n"
        "  • [cyan]ML Detection:[/cyan] cybershield ml detect --data <file>\n"
        "  • [cyan]Awareness Quiz:[/cyan] cybershield awareness quiz\n\n"
        "[bold red]⚔️  Attack Testing:[/bold red]\n"
        "  Use Kali Linux VM with real attack tools:\n"
        "  • nmap (port scanning)\n"
        "  • hping3 (network attacks)\n"
        "  • stress-ng (CPU exhaustion)\n\n"
        "[dim]For detailed guides, see QUICK_START_SECURITY.md[/dim]",
        border_style="red",
        box=box.DOUBLE,
        expand=False
    ))
    console.print()


def cli():
    """Entry point that registers commands lazily."""
    _register_commands()
    main()


if __name__ == "__main__":
    cli()
