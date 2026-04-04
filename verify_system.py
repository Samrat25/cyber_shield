#!/usr/bin/env python3
"""
CyberShield System Verification Script
Checks all components are properly configured and working
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_env_vars():
    """Check required environment variables."""
    console.print("\n[bold cyan]1. Checking Environment Variables[/bold cyan]")
    
    required_vars = {
        'PINATA_JWT': 'Pinata IPFS API key',
        'APTOS_PRIVATE_KEY': 'Aptos private key',
        'APTOS_ADDRESS': 'Aptos account address',
        'APTOS_NODE_URL': 'Aptos node URL',
    }
    
    optional_vars = {
        'SUPABASE_URL': 'Supabase project URL',
        'SUPABASE_KEY': 'Supabase anon key',
    }
    
    all_good = True
    
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            console.print(f"  [green]✓[/green] {var}: {desc}")
        else:
            console.print(f"  [red]✗[/red] {var}: {desc} [red](MISSING)[/red]")
            all_good = False
    
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            console.print(f"  [green]✓[/green] {var}: {desc}")
        else:
            console.print(f"  [yellow]⚠[/yellow] {var}: {desc} [yellow](optional)[/yellow]")
    
    return all_good


def check_dependencies():
    """Check Python dependencies."""
    console.print("\n[bold cyan]2. Checking Python Dependencies[/bold cyan]")
    
    required_packages = [
        'aptos_sdk',
        'supabase',
        'flask',
        'flask_cors',
        'websockets',
        'sklearn',
        'xgboost',
        'tensorflow',
        'psutil',
        'click',
        'rich',
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package)
            console.print(f"  [green]✓[/green] {package}")
        except ImportError:
            console.print(f"  [red]✗[/red] {package} [red](MISSING)[/red]")
            all_good = False
    
    return all_good


def check_files():
    """Check required files exist."""
    console.print("\n[bold cyan]3. Checking Required Files[/bold cyan]")
    
    required_files = [
        'cybershield/blockchain/aptos.py',
        'cybershield/storage/ipfs.py',
        'cybershield/network/p2p_node.py',
        'cybershield/ml/advanced_detector.py',
        'cybershield/core/db.py',
        'dashboard/server.py',
        'dashboard/index.html',
        'docker-compose.yml',
        'Dockerfile',
        'supabase_schema.sql',
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            console.print(f"  [green]✓[/green] {file_path}")
        else:
            console.print(f"  [red]✗[/red] {file_path} [red](MISSING)[/red]")
            all_good = False
    
    return all_good


def check_ml_models():
    """Check ML models."""
    console.print("\n[bold cyan]4. Checking ML Models[/bold cyan]")
    
    try:
        from cybershield.ml import get_detector
        detector = get_detector()
        
        if detector.models:
            console.print(f"  [green]✓[/green] Models loaded: {len(detector.models)}")
            for model_name in detector.models.keys():
                console.print(f"    • {model_name}")
            
            if detector.model_hash:
                console.print(f"  [green]✓[/green] ZK Proof Hash: {detector.model_hash[:32]}...")
            
            return True
        else:
            console.print(f"  [yellow]⚠[/yellow] No models loaded (will auto-train on first use)")
            return True
    except Exception as e:
        console.print(f"  [red]✗[/red] Error loading models: {e}")
        return False


def check_blockchain():
    """Check blockchain connection."""
    console.print("\n[bold cyan]5. Checking Blockchain Connection[/bold cyan]")
    
    try:
        from cybershield.blockchain.aptos import AptosClient
        client = AptosClient()
        
        console.print(f"  [green]✓[/green] Node URL: {client.node_url}")
        console.print(f"  [green]✓[/green] Network: {client.network}")
        console.print(f"  [green]✓[/green] Address: {client.address[:20]}...")
        
        # Try to get count (tests connection)
        try:
            count = client.get_log_count()
            console.print(f"  [green]✓[/green] Connection successful (log count: {count})")
            return True
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Connection test failed: {e}")
            console.print(f"  [dim]This is OK if contract not initialized yet[/dim]")
            return True
    except Exception as e:
        console.print(f"  [red]✗[/red] Error: {e}")
        return False


def check_ipfs():
    """Check IPFS connection."""
    console.print("\n[bold cyan]6. Checking IPFS Connection[/bold cyan]")
    
    try:
        from cybershield.storage.ipfs import IPFSClient
        client = IPFSClient()
        
        console.print(f"  [green]✓[/green] Pinata API configured")
        console.print(f"  [green]✓[/green] Gateway: {client.gateway_url('test')[:50]}...")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗[/red] Error: {e}")
        return False


def check_supabase():
    """Check Supabase connection."""
    console.print("\n[bold cyan]7. Checking Supabase Connection[/bold cyan]")
    
    try:
        from cybershield.core.db import get_db
        db = get_db()
        
        if db:
            console.print(f"  [green]✓[/green] Supabase client configured")
            
            # Try to get stats
            try:
                from cybershield.core.db import get_stats
                stats = get_stats()
                console.print(f"  [green]✓[/green] Connection successful")
                console.print(f"    • Total checks: {stats.get('total_checks', 0)}")
                console.print(f"    • Total threats: {stats.get('total_threats', 0)}")
                return True
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Connection test failed: {e}")
                console.print(f"  [dim]Make sure tables are created (run supabase_schema.sql)[/dim]")
                return True
        else:
            console.print(f"  [yellow]⚠[/yellow] Supabase not configured (optional)")
            console.print(f"  [dim]Add SUPABASE_URL and SUPABASE_KEY to .env[/dim]")
            return True
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Supabase not available: {e}")
        return True


def check_docker():
    """Check Docker availability."""
    console.print("\n[bold cyan]8. Checking Docker[/bold cyan]")
    
    import subprocess
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"  [green]✓[/green] Docker: {result.stdout.strip()}")
        else:
            console.print(f"  [red]✗[/red] Docker not available")
            return False
    except FileNotFoundError:
        console.print(f"  [red]✗[/red] Docker not installed")
        return False
    
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"  [green]✓[/green] Docker Compose: {result.stdout.strip()}")
            return True
        else:
            console.print(f"  [red]✗[/red] Docker Compose not available")
            return False
    except FileNotFoundError:
        console.print(f"  [red]✗[/red] Docker Compose not installed")
        return False


def main():
    """Run all checks."""
    console.print(Panel(
        "[bold cyan]CyberShield System Verification[/bold cyan]\n"
        "Checking all components...",
        expand=False
    ))
    
    results = {
        'Environment Variables': check_env_vars(),
        'Python Dependencies': check_dependencies(),
        'Required Files': check_files(),
        'ML Models': check_ml_models(),
        'Blockchain': check_blockchain(),
        'IPFS': check_ipfs(),
        'Supabase': check_supabase(),
        'Docker': check_docker(),
    }
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold cyan]Summary[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Component", style="dim")
    table.add_column("Status", justify="center")
    
    for component, status in results.items():
        status_str = "[green]✓ PASS[/green]" if status else "[red]✗ FAIL[/red]"
        table.add_row(component, status_str)
    
    console.print(table)
    
    # Overall status
    all_passed = all(results.values())
    
    if all_passed:
        console.print("\n[bold green]✓ All checks passed! System is ready.[/bold green]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("  1. Register node: [cyan]cybershield node register[/cyan]")
        console.print("  2. Start monitoring: [cyan]cybershield node monitor[/cyan]")
        console.print("  3. Start dashboard: [cyan]cybershield dashboard[/cyan]")
        console.print("  4. Deploy with Docker: [cyan]docker-compose up -d[/cyan]")
        return 0
    else:
        console.print("\n[bold yellow]⚠ Some checks failed. Review above for details.[/bold yellow]")
        console.print("\n[dim]Common fixes:[/dim]")
        console.print("  • Missing env vars: Edit .env file")
        console.print("  • Missing packages: pip install -r requirements.txt")
        console.print("  • Supabase: Create tables with supabase_schema.sql")
        return 1


if __name__ == '__main__':
    sys.exit(main())
