"""Phishing detection CLI commands with enhanced UI."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from cybershield.phishing.detector import PhishingDetector
from cybershield.ui.banner import show_banner, show_command_header, show_loading

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def phishing(ctx):
    """Phishing detection and URL analysis commands."""
    if ctx.invoked_subcommand is None:
        show_banner(subtitle="Phishing Detection Module", clear_screen=True)
        show_loading("Loading phishing detector", duration=1.0, steps=[
            "Loading ML model",
            "Initializing features",
            "Ready"
        ])
        console.print("[dim]Type 'cybershield phishing --help' for available commands[/dim]\n")


@phishing.command()
@click.option('--url', '-u', required=True, help='URL to check for phishing indicators')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed feature analysis')
def check(url: str, verbose: bool):
    """Check if a URL is potentially a phishing site using ML model."""
    show_banner(subtitle="Phishing Detection - URL Analysis", clear_screen=True)
    show_command_header("URL ANALYSIS", f"Analyzing: {url}")
    
    show_loading("Analyzing URL", duration=0.8, steps=[
        "Extracting features",
        "Running ML model",
        "Calculating confidence"
    ])
    
    detector = PhishingDetector()
    result = detector.detect(url)
    
    # Determine color based on risk level
    risk_colors = {
        "HIGH": "bold red",
        "MEDIUM": "bold yellow",
        "LOW": "bold blue",
        "SAFE": "bold green"
    }
    color = risk_colors.get(result["risk_level"], "white")
    
    # Build result panel content
    panel_content = f"[{color}]Risk Level: {result['risk_level']}[/{color}]\n"
    panel_content += f"[white]Risk Score: {result['risk_score']}/10[/white]\n"
    panel_content += f"[white]Phishing: {'YES ⚠️' if result['is_phishing'] else 'NO ✅'}[/white]\n"
    
    # Add ML-specific information if available
    if 'ml_confidence' in result:
        panel_content += f"\n[bold cyan]ML Detection:[/bold cyan]\n"
        panel_content += f"[white]Method: {result['detection_method']}[/white]\n"
        panel_content += f"[white]Model Accuracy: {result['model_accuracy']}[/white]\n"
        panel_content += f"[white]Confidence: {result['ml_confidence']:.2f}%[/white]\n"
        panel_content += f"[white]Phishing Probability: {result['phishing_probability']:.2f}%[/white]"
    else:
        panel_content += f"\n[dim]Detection Method: {result.get('detection_method', 'Rule-based')}[/dim]"
    
    # Display main result
    console.print(Panel.fit(
        panel_content,
        title="[bold]Detection Result[/bold]",
        border_style=color.split()[1] if " " in color else color,
        box=box.DOUBLE
    ))
    
    console.print()
    console.print(f"[italic]{result['recommendation']}[/italic]")
    console.print()
    
    # Display score breakdown if available (rule-based)
    if 'score_breakdown' in result and result['score_breakdown']:
        table = Table(title="Risk Score Breakdown", box=box.ROUNDED)
        table.add_column("Indicator", style="cyan")
        table.add_column("Score", justify="right", style="yellow")
        
        for indicator, score in result['score_breakdown'].items():
            indicator_name = indicator.replace('_', ' ').title()
            score_color = "green" if score < 0 else "red" if score >= 3 else "yellow"
            table.add_row(indicator_name, f"[{score_color}]{score:+d}[/{score_color}]")
        
        console.print(table)
        console.print()
    
    # Display detailed features if verbose
    if verbose:
        features = result['features']
        
        table = Table(title="Detailed Feature Analysis (24 ML Features)", box=box.ROUNDED)
        table.add_column("Feature", style="cyan")
        table.add_column("Value", style="white")
        
        # Group features
        length_features = {
            "URL Length": features['url_length'],
            "Domain Length": features['domain_length'],
            "Path Length": features['path_length']
        }
        
        char_features = {
            "Dots": features['num_dots'],
            "Hyphens": features['num_hyphens'],
            "Underscores": features['num_underscores'],
            "Slashes": features['num_slashes'],
            "@ Symbols": features['num_at'],
            "Ampersands": features.get('num_ampersands', 0),
            "Exclamations": features.get('num_exclamations', 0),
            "Percent Signs": features.get('num_percent', 0)
        }
        
        security_features = {
            "HTTPS": "✅" if features['has_https'] else "❌",
            "Has IP Address": "⚠️ Yes" if features['has_ip'] else "✅ No",
            "Trusted Domain": "✅ Yes" if features['is_trusted'] else "❌ No",
            "Suspicious TLD": "⚠️ Yes" if features.get('suspicious_tld', False) else "✅ No",
            "Suspicious Keywords": features['suspicious_words'],
            "URL Depth": features.get('url_depth', 0),
            "Subdomains": features['subdomain_count'],
            "Has WWW": "✅" if features.get('has_www', False) else "❌"
        }
        
        advanced_features = {
            "Domain Entropy": f"{features.get('domain_entropy', 0):.2f}",
            "Digit Ratio": f"{features.get('digit_ratio', 0):.2%}",
            "Percent Encoding": "⚠️ Yes" if features.get('has_percent_encoding', False) else "✅ No"
        }
        
        # Add to table
        table.add_section()
        table.add_row("[bold]Length Metrics[/bold]", "")
        for name, value in length_features.items():
            table.add_row(f"  {name}", str(value))
        
        table.add_section()
        table.add_row("[bold]Character Counts[/bold]", "")
        for name, value in char_features.items():
            table.add_row(f"  {name}", str(value))
        
        table.add_section()
        table.add_row("[bold]Security Indicators[/bold]", "")
        for name, value in security_features.items():
            table.add_row(f"  {name}", str(value))
        
        table.add_section()
        table.add_row("[bold]Advanced Features[/bold]", "")
        for name, value in advanced_features.items():
            table.add_row(f"  {name}", str(value))
        
        console.print(table)


@phishing.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), 
              help='File containing URLs to check (one per line)')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
def batch(file: str, output: str):
    """Check multiple URLs from a file."""
    import json
    
    show_banner(subtitle="Phishing Detection - Batch Analysis", clear_screen=True)
    show_command_header("BATCH ANALYSIS", f"Processing URLs from: {file}")
    
    # Read URLs from file
    with open(file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    console.print(f"[cyan]Found {len(urls)} URLs to analyze...[/cyan]\n")
    
    show_loading("Initializing batch analysis", duration=0.5, steps=[
        "Loading URLs",
        "Starting analysis"
    ])
    
    detector = PhishingDetector()
    results = []
    
    # Analyze each URL
    for i, url in enumerate(urls, 1):
        console.print(f"[dim]Analyzing {i}/{len(urls)}:[/dim] {url}")
        result = detector.detect(url)
        results.append(result)
    
    # Summary table
    console.print()
    table = Table(title="Batch Analysis Results", box=box.ROUNDED)
    table.add_column("URL", style="cyan", no_wrap=False, max_width=50)
    table.add_column("Risk", justify="center")
    table.add_column("Score", justify="center")
    
    for result in results:
        risk_color = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "SAFE": "green"
        }.get(result["risk_level"], "white")
        
        table.add_row(
            result["url"],
            f"[{risk_color}]{result['risk_level']}[/{risk_color}]",
            f"{result['risk_score']}"
        )
    
    console.print(table)
    
    # Statistics
    high_risk = sum(1 for r in results if r["risk_level"] == "HIGH")
    medium_risk = sum(1 for r in results if r["risk_level"] == "MEDIUM")
    phishing_count = sum(1 for r in results if r["is_phishing"])
    
    console.print()
    console.print(f"[bold]Summary:[/bold]")
    console.print(f"  Total URLs: {len(results)}")
    console.print(f"  [red]High Risk: {high_risk}[/red]")
    console.print(f"  [yellow]Medium Risk: {medium_risk}[/yellow]")
    console.print(f"  [red]Likely Phishing: {phishing_count}[/red]")
    
    # Save to file if requested
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        console.print(f"\n[green]✓ Results saved to {output}[/green]")


@phishing.command()
def examples():
    """Show example phishing URLs and safe URLs for testing."""
    show_banner(subtitle="Phishing Detection - Example URLs", clear_screen=True)
    show_command_header("EXAMPLE URLS", "Test the phishing detector with these examples")
    
    console.print("[bold red]⚠ Suspicious/Phishing URLs:[/bold red]\n")
    phishing_urls = [
        "http://paypa1-secure-login.xyz/verify-account",
        "https://amaz0n-customer-service.tk/update",
        "http://192.168.1.1/banking-login",
        "https://secure-account-verify-microsoft.com.phishing.xyz",
        "http://g00gle-security-alert.com/signin"
    ]
    for url in phishing_urls:
        console.print(f"  • {url}")
    
    console.print()
    
    # Safe examples
    console.print("[bold green]Safe URLs:[/bold green]")
    safe_urls = [
        "https://www.paypal.com/signin",
        "https://www.amazon.com/account",
        "https://accounts.google.com/signin",
        "https://login.microsoft.com",
        "https://github.com/login"
    ]
    for url in safe_urls:
        console.print(f"  • {url}")
    
    console.print()
    console.print("[dim]Try: cybershield phishing check --url <URL>[/dim]")
