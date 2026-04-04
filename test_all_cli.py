#!/usr/bin/env python3
"""
Test all CyberShield CLI commands
Run this before the demo to ensure everything works
"""

import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def run_command(cmd, description):
    """Run a command and return success/failure."""
    console.print(f"\n[cyan]Testing:[/cyan] {description}")
    console.print(f"[dim]Command: {cmd}[/dim]")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            console.print(f"[green]✓ PASS[/green]")
            return True
        else:
            console.print(f"[red]✗ FAIL[/red]")
            if result.stderr:
                console.print(f"[red]{result.stderr[:200]}[/red]")
            return False
    except subprocess.TimeoutExpired:
        console.print(f"[yellow]⚠ TIMEOUT[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]✗ ERROR: {e}[/red]")
        return False


def main():
    console.print(Panel(
        "[bold cyan]CyberShield CLI Test Suite[/bold cyan]\n"
        "Testing all commands before demo",
        expand=False
    ))
    
    tests = [
        # Basic commands
        ("cybershield --version", "Version check"),
        ("cybershield --help", "Help command"),
        
        # Status commands
        ("cybershield status", "Node status"),
        ("cybershield ml info", "ML model info"),
        
        # ML commands
        ("cybershield ml test", "ML test"),
        
        # Network commands
        ("cybershield network list", "Network list"),
        
        # API command
        ("cybershield api --help", "API help"),
    ]
    
    results = []
    
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold cyan]Test Summary[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Test", style="dim")
    table.add_column("Result", justify="center")
    
    passed = 0
    for desc, success in results:
        status = "[green]✓ PASS[/green]" if success else "[red]✗ FAIL[/red]"
        table.add_row(desc, status)
        if success:
            passed += 1
    
    console.print(table)
    
    console.print(f"\n[bold]Results: {passed}/{len(results)} tests passed[/bold]")
    
    if passed == len(results):
        console.print("\n[bold green]✓ All tests passed! Ready for demo.[/bold green]")
        return 0
    else:
        console.print("\n[bold yellow]⚠ Some tests failed. Review above.[/bold yellow]")
        return 1


if __name__ == '__main__':
    sys.exit(main())
