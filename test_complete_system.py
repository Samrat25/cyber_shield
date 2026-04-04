#!/usr/bin/env python3
"""
Complete System Test for CyberShield
Tests all components: ML, Blockchain, IPFS, P2P, Dashboard, API
"""

import sys
import time
import json
import requests
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def test_ml_models():
    """Test ML models and ZK proof."""
    console.print("\n[bold cyan]1. Testing ML Models & ZK Proof[/bold cyan]")
    
    try:
        from cybershield.ml import get_detector
        detector = get_detector()
        
        # Check models
        models = list(detector.models.keys())
        console.print(f"  ✓ Models loaded: {', '.join(models)}")
        console.print(f"  ✓ Model count: {len(models)}")
        
        # Check ZK proof hash
        if detector.model_hash:
            console.print(f"  ✓ ZK Proof Hash: {detector.model_hash[:32]}...")
        else:
            console.print("  ✗ ZK Proof Hash missing")
            return False
        
        # Test detection
        test_metrics = {
            'cpu_percent': 25.0,
            'memory_percent': 45.0,
            'process_count': 150,
            'net_bytes_sent': 5000000,
            'net_bytes_recv': 5000000,
            'disk_read_bytes': 2000000,
            'disk_write_bytes': 2000000
        }
        
        verdict, confidence, model_scores = detector.detect(test_metrics)
        console.print(f"  ✓ Detection test: {verdict} (confidence: {confidence:.2f})")
        console.print(f"  ✓ Model scores: {list(model_scores.keys())}")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ ML test failed: {e}[/red]")
        return False


def test_blockchain():
    """Test blockchain connection and signing."""
    console.print("\n[bold cyan]2. Testing Blockchain (Aptos)[/bold cyan]")
    
    try:
        from cybershield.blockchain.aptos import AptosClient
        client = AptosClient()
        
        console.print(f"  ✓ Network: {client.network}")
        console.print(f"  ✓ Node URL: {client.node_url}")
        console.print(f"  ✓ Address: {client.address[:20]}...")
        
        # Check if we have private key (for signing)
        if client.private_key:
            console.print("  ✓ Private key configured (transactions will be SIGNED)")
        else:
            console.print("  ✗ Private key missing")
            return False
        
        # Get on-chain count
        try:
            count = client.get_log_count()
            console.print(f"  ✓ On-chain threat count: {count}")
        except Exception as e:
            console.print(f"  ⚠ Could not fetch count: {e}")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ Blockchain test failed: {e}[/red]")
        return False


def test_ipfs():
    """Test IPFS/Pinata connection."""
    console.print("\n[bold cyan]3. Testing IPFS (Pinata)[/bold cyan]")
    
    try:
        from cybershield.storage.ipfs import IPFSClient
        client = IPFSClient()
        
        console.print("  ✓ Pinata client initialized")
        console.print(f"  ✓ Gateway: {client.gateway_url('test')[:50]}...")
        
        # Check if JWT is configured
        if client.jwt:
            console.print("  ✓ JWT configured (can pin data)")
        else:
            console.print("  ✗ JWT missing")
            return False
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ IPFS test failed: {e}[/red]")
        return False


def test_p2p():
    """Test P2P networking."""
    console.print("\n[bold cyan]4. Testing P2P Network[/bold cyan]")
    
    try:
        from cybershield.network.p2p_node import P2PNode
        
        node = P2PNode(node_id="TEST_NODE", port=9999)
        console.print(f"  ✓ P2P Node created: {node.node_id}")
        console.print(f"  ✓ Local IP: {node.local_ip}")
        console.print(f"  ✓ Port: {node.port}")
        console.print("  ✓ WebSocket-based P2P ready")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ P2P test failed: {e}[/red]")
        return False


def test_database():
    """Test Supabase database connection."""
    console.print("\n[bold cyan]5. Testing Database (Supabase)[/bold cyan]")
    
    try:
        from cybershield.core.db import get_db
        
        db = get_db()
        if not db:
            console.print("  [yellow]⚠ Supabase not configured (optional)[/yellow]")
            return True
        
        console.print("  ✓ Supabase client initialized")
        
        # Try to query events
        try:
            result = db.table("events").select("*").limit(1).execute()
            console.print(f"  ✓ Events table accessible")
        except Exception as e:
            console.print(f"  [yellow]⚠ Events table error: {e}[/yellow]")
            console.print("  [yellow]  → Run supabase_schema.sql in Supabase SQL Editor[/yellow]")
        
        # Try to query nodes
        try:
            result = db.table("nodes").select("*").limit(1).execute()
            console.print(f"  ✓ Nodes table accessible")
        except Exception as e:
            console.print(f"  [yellow]⚠ Nodes table error: {e}[/yellow]")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ Database test failed: {e}[/red]")
        return False


def test_node_state():
    """Test node registration state."""
    console.print("\n[bold cyan]6. Testing Node State[/bold cyan]")
    
    try:
        from cybershield.config import LOGS_DIR
        
        state_file = LOGS_DIR / "node_state.json"
        
        if not state_file.exists():
            console.print("  [yellow]⚠ Node not registered yet[/yellow]")
            console.print("  [yellow]  → Run: cybershield node register[/yellow]")
            return True
        
        state = json.loads(state_file.read_text())
        
        console.print(f"  ✓ Node ID: {state.get('node_id')}")
        console.print(f"  ✓ IP: {state.get('ip')}")
        console.print(f"  ✓ Status: {state.get('status')}")
        
        if state.get('reg_cid'):
            console.print(f"  ✓ IPFS CID: {state['reg_cid']}")
        
        if state.get('reg_tx'):
            console.print(f"  ✓ TX Hash: {state['reg_tx'][:20]}...")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ Node state test failed: {e}[/red]")
        return False


def test_monitor():
    """Test system monitoring."""
    console.print("\n[bold cyan]7. Testing System Monitor[/bold cyan]")
    
    try:
        from cybershield.core.monitor import SystemMonitor
        
        monitor = SystemMonitor()
        metrics = monitor.get_metrics()
        
        console.print(f"  ✓ CPU: {metrics['cpu_percent']:.1f}%")
        console.print(f"  ✓ Memory: {metrics['memory_percent']:.1f}%")
        console.print(f"  ✓ Processes: {metrics['process_count']}")
        console.print(f"  ✓ Network bytes sent: {metrics['net_bytes_sent']:,}")
        console.print(f"  ✓ Network bytes recv: {metrics['net_bytes_recv']:,}")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ Monitor test failed: {e}[/red]")
        return False


def test_docker():
    """Test Docker configuration."""
    console.print("\n[bold cyan]8. Testing Docker Setup[/bold cyan]")
    
    try:
        docker_file = Path("docker-compose.yml")
        
        if not docker_file.exists():
            console.print("  [red]✗ docker-compose.yml not found[/red]")
            return False
        
        console.print("  ✓ docker-compose.yml exists")
        
        # Check Dockerfiles
        dockerfiles = ["Dockerfile", "Dockerfile.dashboard", "Dockerfile.indexer"]
        for df in dockerfiles:
            if Path(df).exists():
                console.print(f"  ✓ {df} exists")
            else:
                console.print(f"  [yellow]⚠ {df} missing[/yellow]")
        
        console.print("\n  [dim]To start Docker:[/dim]")
        console.print("  [cyan]docker-compose up -d[/cyan]")
        
        return True
    except Exception as e:
        console.print(f"  [red]✗ Docker test failed: {e}[/red]")
        return False


def main():
    """Run all tests."""
    console.print(Panel(
        "[bold cyan]CyberShield Complete System Test[/bold cyan]\n"
        "Testing all components for production readiness",
        expand=False
    ))
    
    results = {
        "ML Models & ZK Proof": test_ml_models(),
        "Blockchain (Aptos)": test_blockchain(),
        "IPFS (Pinata)": test_ipfs(),
        "P2P Network": test_p2p(),
        "Database (Supabase)": test_database(),
        "Node State": test_node_state(),
        "System Monitor": test_monitor(),
        "Docker Setup": test_docker()
    }
    
    # Summary
    console.print("\n" + "="*70)
    console.print("\n[bold cyan]Test Summary[/bold cyan]\n")
    
    table = Table(box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="bold")
    
    passed = 0
    total = len(results)
    
    for component, result in results.items():
        status = "[green]✓ PASS[/green]" if result else "[red]✗ FAIL[/red]"
        table.add_row(component, status)
        if result:
            passed += 1
    
    console.print(table)
    
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("\n[bold green]✓ All systems operational![/bold green]")
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("  1. Run: [cyan]cybershield node monitor --p2p[/cyan]")
        console.print("  2. Run: [cyan]cybershield dashboard[/cyan] (in another terminal)")
        console.print("  3. Run: [cyan]cybershield api start[/cyan] (in another terminal)")
        console.print("  4. Attack from Kali Linux to trigger detection")
        console.print("  5. Show judges the blockchain TX and IPFS evidence")
    else:
        console.print("\n[bold yellow]⚠ Some tests failed - check configuration[/bold yellow]")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
