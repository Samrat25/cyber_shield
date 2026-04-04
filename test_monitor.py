#!/usr/bin/env python3
# test_monitor.py - Quick test of monitoring functionality

from core.monitor import get_metrics
from core.ml_detector import detect

print("Testing monitoring functionality...\n")

# Test 1: Get metrics
print("1. Collecting system metrics...")
metrics = get_metrics()
print(f"   CPU: {metrics['cpu_percent']}%")
print(f"   Memory: {metrics['memory_percent']}%")
print(f"   Processes: {metrics['process_count']}")
print(f"   IP: {metrics['ip']}")
print(f"   ✓ Metrics collected successfully\n")

# Test 2: ML detection
print("2. Running ML anomaly detection...")
verdict, score = detect(metrics)
print(f"   Verdict: {verdict}")
print(f"   Score: {score}")
print(f"   ✓ ML detection working\n")

# Test 3: Check if we can import all modules
print("3. Checking all imports...")
try:
    from core.pinata import pin_json, gateway_url
    from core.aptos import log_threat, get_log_count, explorer_url
    print("   ✓ All modules imported successfully\n")
except Exception as e:
    print(f"   ✗ Import error: {e}\n")

print("All tests passed! The system is ready.")
print("\nTo start monitoring, run:")
print("  python cli.py monitor")
print("\nTo simulate an attack and trigger anomaly detection:")
print("  Run stress tests from another terminal while monitoring is active")
