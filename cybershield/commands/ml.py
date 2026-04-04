# cybershield/commands/ml.py
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from ..ml import get_detector

console = Console()


@click.group()
def ml():
    """Machine learning model management."""
    pass


@ml.command()
@click.option('--advanced', is_flag=True, help='Train advanced ensemble models')
@click.option('--quick', is_flag=True, help='Quick training (fewer epochs)')
def train(advanced, quick):
    """Train ML models for anomaly detection (optional - models auto-train on first use)."""
    console.print(Panel("[bold cyan]ML Model Training[/bold cyan]", expand=False))
    
    console.print("\n[dim]Note: Training is optional. Models auto-train on first use with synthetic data.[/dim]")
    console.print("[dim]Use this command to retrain with custom parameters.[/dim]\n")
    
    detector = get_detector()
    
    if advanced:
        console.print("[yellow]Training advanced ensemble (this may take a few minutes)...[/yellow]\n")
    else:
        console.print("[yellow]Training basic models...[/yellow]\n")
    
    detector.train(verbose=True)
    
    console.print("\n[green]✓ Training complete![/green]")
    console.print(f"[dim]Model hash (ZK proof): {detector.model_hash[:32]}...[/dim]\n")


@ml.command()
def info():
    """Show information about trained models."""
    detector = get_detector()
    
    console.print(Panel("[bold cyan]ML Model Information[/bold cyan]", expand=False))
    console.print()
    
    if not detector.models:
        console.print("[yellow]Models will auto-train on first use (30 seconds).[/yellow]")
        console.print("[dim]Or run 'cybershield ml train' to train now.[/dim]")
        return
    
    for model_name in detector.models.keys():
        console.print(f"  [green]✓[/green] {model_name}")
    
    console.print(f"\n  Total models: [cyan]{len(detector.models)}[/cyan]")
    console.print(f"  Features: [cyan]{len(detector.feature_names)}[/cyan]")
    
    # Show ZK proof info
    if detector.model_hash:
        console.print(f"\n  [yellow]ZK Proof Hash:[/yellow] [dim]{detector.model_hash[:32]}...[/dim]")
        console.print(f"  [dim]Verifies model integrity without exposing training data[/dim]")
    
    console.print()


@ml.command()
def test():
    """Test ML models with sample data."""
    from ..core.monitor import SystemMonitor
    
    console.print(Panel("[bold cyan]ML Model Testing[/bold cyan]", expand=False))
    
    detector = get_detector()
    monitor = SystemMonitor()
    
    console.print("\n[yellow]Collecting current system metrics...[/yellow]")
    metrics = monitor.get_metrics()
    
    console.print(f"  CPU: {metrics['cpu_percent']:.1f}%")
    console.print(f"  Memory: {metrics['memory_percent']:.1f}%")
    console.print(f"  Processes: {metrics['process_count']}")
    
    console.print("\n[yellow]Running ML detection...[/yellow]")
    verdict, confidence, model_scores = detector.detect(metrics)
    
    color = "green" if verdict == "safe" else "red"
    console.print(f"\n  Verdict: [{color}]{verdict.upper()}[/{color}]")
    console.print(f"  Confidence: [{color}]{confidence:.1%}[/{color}]")
    
    console.print("\n  Model Scores:")
    for model_name, score in model_scores.items():
        console.print(f"    {model_name}: {score:.3f}")
    
    console.print()
