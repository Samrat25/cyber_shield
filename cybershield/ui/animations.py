"""Animation utilities for CLI."""

import time
from rich.console import Console
from rich.text import Text

console = Console()


def animate_text(text: str, style: str = "bold cyan", delay: float = 0.03):
    """
    Animate text character by character.
    
    Args:
        text: Text to animate
        style: Rich style string
        delay: Delay between characters
    """
    for char in text:
        console.print(char, style=style, end="")
        time.sleep(delay)
    console.print()


def show_progress(total: int = 100, message: str = "Processing"):
    """
    Show a simple progress animation.
    
    Args:
        total: Total steps
        message: Progress message
    """
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    
    with Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="red", finished_style="bright_red"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task(f"[cyan]{message}...", total=total)
        
        for _ in range(total):
            time.sleep(0.02)
            progress.advance(task)


def typewriter_effect(text: str, style: str = "white", delay: float = 0.05):
    """
    Display text with typewriter effect.
    
    Args:
        text: Text to display
        style: Rich style
        delay: Delay between characters
    """
    for char in text:
        console.print(char, style=style, end="", highlight=False)
        time.sleep(delay)
    console.print()


def pulse_text(text: str, times: int = 3, delay: float = 0.3):
    """
    Make text pulse by changing brightness.
    
    Args:
        text: Text to pulse
        times: Number of pulses
        delay: Delay between pulses
    """
    styles = ["dim red", "red", "bright_red", "red"]
    
    for _ in range(times):
        for style in styles:
            console.print(f"\r{text}", style=f"bold {style}", end="")
            time.sleep(delay / len(styles))
    console.print()


def show_spinner(message: str = "Loading", duration: float = 2.0):
    """
    Show a spinner animation.
    
    Args:
        message: Message to display
        duration: Duration in seconds
    """
    from rich.spinner import Spinner
    from rich.live import Live
    
    spinner = Spinner("dots", text=f"[cyan]{message}...", style="red")
    
    with Live(spinner, console=console, transient=True):
        time.sleep(duration)
    
    console.print(f"[bold green]✓[/bold green] {message} complete!")
