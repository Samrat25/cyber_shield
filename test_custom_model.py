#!/usr/bin/env python3
"""Test custom model detection"""

from cybershield.ml.custom_detector import get_custom_detector

d = get_custom_detector()

print("Testing custom model with CPU spike:\n")

for i in range(15):
    cpu = 100 if i > 10 else 35
    m = {'cpu_percent': cpu, 'memory_percent': 90, 'process_count': 270}
    v, c, s = d.detect(m)
    prob = s.get('random_forest', 0)
    zscore = s.get('cpu_zscore', 0)
    
    status = "🔴 ANOMALY" if v == "anomaly" else "🟢 SAFE"
    print(f"{i:2d}: CPU={cpu:3.0f}% -> {status} conf={c:.2f} prob={prob:.2f} zscore={zscore:.2f}")

print("\n✓ Model integration test complete!")
