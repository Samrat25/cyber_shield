#!/usr/bin/env python3
"""
Sample YOUR machine's actual baseline for 15 seconds.
This fixes the autoencoder always returning 1.000.
"""

import psutil
import numpy as np
import time
import json
import os

print('Sampling your machine for 15 seconds...')
print('(Network metrics will use safe defaults to avoid false positives)')
readings = []

for i in range(10):
    readings.append({
        'cpu': psutil.cpu_percent(interval=0.5),
        'mem': psutil.virtual_memory().percent,
        'procs': len(psutil.pids()),
    })
    print(f'  [{i+1}/10] CPU={readings[-1]["cpu"]:.1f}%  MEM={readings[-1]["mem"]:.1f}%  PROCS={readings[-1]["procs"]}')
    time.sleep(1.0)

cpu_mean = np.mean([r['cpu'] for r in readings])
mem_mean = np.mean([r['mem'] for r in readings])
prc_mean = np.mean([r['procs'] for r in readings])
cpu_std  = max(np.std([r['cpu'] for r in readings]), 5.0)
mem_std  = max(np.std([r['mem'] for r in readings]), 3.0)
prc_std  = max(np.std([r['procs'] for r in readings]), 10.0)

print(f'\nYour machine normal: CPU={cpu_mean:.1f}%±{cpu_std:.1f}  MEM={mem_mean:.1f}%±{mem_std:.1f}  PROCS={prc_mean:.0f}±{prc_std:.0f}')

# Save baseline with SAFE network defaults (to avoid false positives)
os.makedirs('logs', exist_ok=True)
baseline = {
    'cpu_mean': cpu_mean, 'cpu_std': cpu_std,
    'mem_mean': mem_mean, 'mem_std': mem_std,
    'prc_mean': prc_mean, 'prc_std': prc_std,
    # Network: Use high defaults to avoid false positives from normal traffic
    'pkt_mean': 5000.0, 'pkt_std': 3000.0,
    'byt_mean': 5000000.0, 'byt_std': 3000000.0,  # 5MB ± 3MB
    'disk_mean': 70.0, 'disk_std': 10.0,
}

with open('logs/baseline.json', 'w') as f:
    json.dump(baseline, f, indent=2)

print('✓ Saved to logs/baseline.json')
print(f'\nNetwork metrics use safe defaults to avoid false positives.')
print(f'This will be used to train models that understand YOUR system.')

