"""Banner and loading animations for CLI."""

import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

BANNER = """
   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗██╗  ██╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████╗███████║
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══██║
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████║██║  ██║
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""

SUBTITLE = "Blockchain-Based Distributed Intrusion Detection System"
VERSION = "Version 1.0.0"


def show_banner(subtitle: str = None, clear_screen: bool = True):
    """
    Display the CyberShield banner with animations.
    
    Args:
        subtitle: Optional custom subtitle
        clear_screen: Whether to clear screen before showing banner
    """
    if clear_screen:
        console.clear()
    
    # Create banner text with gradient effect
    banner_text = Text()
    
    # Add banner with red gradient
    lines = BANNER.strip().split('\n')
    colors = ["red", "bright_red", "red", "bright_red", "red", "bright_red"]
    
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        banner_text.append(line + "\n", style=f"bold {color}")
    
    # Add subtitle and version
    banner_text.append("\n")
    banner_text.append(subtitle or SUBTITLE, style="bold cyan")
    banner_text.append("\n")
    banner_text.append(VERSION, style="dim white")
    
    # Create panel with double box
    panel = Panel(
        Align.center(banner_text),
        box=box.DOUBLE,
        border_style="bright_red",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()


def show_loading(message: str = "Initializing", duration: float = 2.0, steps: list = None):
    """
    Show a loading animation with progress bar.
    
    Args:
        message: Loading message to display
        duration: Total duration in seconds
        steps: Optional list of step descriptions
    """
    if steps is None:
        steps = [
            "Loading modules",
            "Initializing security components",
            "Connecting to network",
            "Ready"
        ]
    
    with Progress(
        SpinnerColumn(spinner_name="dots", style="red"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="red", finished_style="bright_red"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task(f"[cyan]{message}...", total=len(steps))
        
        step_duration = duration / len(steps)
        
        for step in steps:
            progress.update(task, description=f"[cyan]{step}...")
            time.sleep(step_duration)
            progress.advance(task)
    
    console.print(f"[bold green]✓[/bold green] {message} complete!\n")


def show_command_header(command_name: str, description: str):
    """
    Show a header for a command execution.
    
    Args:
        command_name: Name of the command
        description: Brief description
    """
    header = Text()
    header.append("⚡ ", style="bold yellow")
    header.append(command_name.upper(), style="bold red")
    header.append(" ⚡", style="bold yellow")
    header.append("\n")
    header.append(description, style="cyan")
    
    panel = Panel(
        Align.center(header),
        box=box.ROUNDED,
        border_style="red",
        padding=(0, 2)
    )
    
    console.print(panel)
    console.print()


def show_success(message: str):
    """Show a success message."""
    console.print(f"\n[bold green]✓[/bold green] {message}\n")


def show_error(message: str):
    """Show an error message."""
    console.print(f"\n[bold red]✗[/bold red] {message}\n")


def show_warning(message: str):
    """Show a warning message."""
    console.print(f"\n[bold yellow]⚠[/bold yellow] {message}\n")


def show_info(message: str):
    """Show an info message."""
    console.print(f"\n[bold cyan]ℹ[/bold cyan] {message}\n")


def animate_banner_chars(delay: float = 0.02):
    """
    Animate banner character by character.
    
    Args:
        delay: Delay between characters in seconds
    """
    console.clear()
    
    lines = BANNER.strip().split('\n')
    colors = ["red", "bright_red", "red", "bright_red", "red", "bright_red"]
    
    # Print each character with delay
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        for char in line:
            console.print(char, style=f"bold {color}", end="")
            time.sleep(delay)
        console.print()
    
    # Print subtitle and version
    console.print()
    for char in SUBTITLE:
        console.print(char, style="bold cyan", end="")
        time.sleep(delay * 0.5)
    console.print()
    
    for char in VERSION:
        console.print(char, style="dim white", end="")
        time.sleep(delay * 0.5)
    console.print("\n")


def show_section_divider(title: str = None):
    """Show a section divider."""
    if title:
        console.print(f"\n[bold red]{'═' * 20}[/bold red] [bold white]{title}[/bold white] [bold red]{'═' * 20}[/bold red]\n")
    else:
        console.print(f"\n[bold red]{'═' * 60}[/bold red]\n")
