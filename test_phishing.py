#!/usr/bin/env python3
"""
Test script for phishing detection module.
Demonstrates URL analysis and risk scoring.
"""

from cybershield.phishing.detector import PhishingDetector
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def test_phishing_detection():
    """Test phishing detection with various URLs."""
    
    console.print("\n[bold cyan]🔍 CyberShield Phishing Detection Test[/bold cyan]\n")
    
    detector = PhishingDetector()
    
    # Test URLs
    test_urls = [
        # Phishing examples
        "http://paypa1-secure-login.xyz/verify-account",
        "https://amaz0n-customer-service.tk/update",
        "http://192.168.1.1/banking-login",
        "https://secure-account-verify-microsoft.com.phishing.xyz",
        "http://g00gle-security-alert.com/signin",
        
        # Safe examples
        "https://www.paypal.com/signin",
        "https://www.amazon.com/account",
        "https://accounts.google.com/signin",
        "https://login.microsoft.com",
        "https://github.com/login"
    ]
    
    # Create results table
    table = Table(title="Phishing Detection Results", box=box.ROUNDED, show_lines=True)
    table.add_column("URL", style="cyan", no_wrap=False, max_width=40)
    table.add_column("Risk Level", justify="center", style="bold")
    table.add_column("Score", justify="center")
    table.add_column("Phishing", justify="center")
    
    results = []
    
    for url in test_urls:
        result = detector.detect(url)
        results.append(result)
        
        # Color based on risk
        risk_color = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "SAFE": "green"
        }.get(result["risk_level"], "white")
        
        phishing_indicator = "⚠️ YES" if result["is_phishing"] else "✅ NO"
        
        table.add_row(
            url,
            f"[{risk_color}]{result['risk_level']}[/{risk_color}]",
            str(result["risk_score"]),
            phishing_indicator
        )
    
    console.print(table)
    
    # Statistics
    console.print("\n[bold]Detection Statistics:[/bold]")
    high_risk = sum(1 for r in results if r["risk_level"] == "HIGH")
    medium_risk = sum(1 for r in results if r["risk_level"] == "MEDIUM")
    phishing_count = sum(1 for r in results if r["is_phishing"])
    safe_count = sum(1 for r in results if r["risk_level"] == "SAFE")
    
    console.print(f"  Total URLs tested: {len(results)}")
    console.print(f"  [red]High Risk: {high_risk}[/red]")
    console.print(f"  [yellow]Medium Risk: {medium_risk}[/yellow]")
    console.print(f"  [green]Safe: {safe_count}[/green]")
    console.print(f"  [red]Likely Phishing: {phishing_count}[/red]")
    
    # Detailed example
    console.print("\n[bold cyan]Detailed Analysis Example:[/bold cyan]\n")
    example_url = test_urls[0]
    result = detector.detect(example_url)
    
    console.print(f"[bold]URL:[/bold] {example_url}")
    console.print(f"[bold]Risk Level:[/bold] [{risk_color}]{result['risk_level']}[/{risk_color}]")
    console.print(f"[bold]Risk Score:[/bold] {result['risk_score']}/10")
    console.print(f"[bold]Is Phishing:[/bold] {'YES ⚠️' if result['is_phishing'] else 'NO ✅'}")
    console.print(f"\n[bold]Recommendation:[/bold]")
    console.print(f"  {result['recommendation']}")
    
    if result['score_breakdown']:
        console.print(f"\n[bold]Score Breakdown:[/bold]")
        for indicator, score in result['score_breakdown'].items():
            indicator_name = indicator.replace('_', ' ').title()
            console.print(f"  • {indicator_name}: {score:+d}")
    
    console.print("\n[green]✓ Phishing detection test completed![/green]\n")


if __name__ == "__main__":
    test_phishing_detection()
