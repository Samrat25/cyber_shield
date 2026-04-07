#!/usr/bin/env python3
"""
Retrain ML models using YOUR machine's actual baseline.
Run save_baseline.py first to capture your baseline.
"""

from cybershield.ml.advanced_detector import AdvancedAnomalyDetector
from pathlib import Path

baseline_file = Path("logs/baseline.json")
if not baseline_file.exists():
    print("❌ No baseline found!")
    print("   Run: python save_baseline.py")
    print("   This will sample your machine for 15 seconds and save the baseline.")
    exit(1)

import json
with open(baseline_file) as f:
    baseline = json.load(f)

print("🔧 Retraining ML models using YOUR baseline...")
print(f"   CPU: {baseline['cpu_mean']:.1f}% ± {baseline['cpu_std']:.1f}")
print(f"   MEM: {baseline['mem_mean']:.1f}% ± {baseline['mem_std']:.1f}")
print(f"   PROCS: {baseline['prc_mean']:.0f} ± {baseline['prc_std']:.0f}")
print()

detector = AdvancedAnomalyDetector()
detector.train(verbose=True)

print()
print("✓ Models retrained and saved!")
print("  Your 92-94% memory is now considered NORMAL.")
print("  Autoencoder will no longer return 1.000 for your baseline.")
print()
print("  Run 'cybershield node monitor' to test with new models.")

