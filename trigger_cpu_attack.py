#!/usr/bin/env python3
"""
Trigger a CPU spike attack for demo purposes.
This will cause the monitor to detect an intrusion.
"""

import multiprocessing
import time
import sys

def cpu_stress():
    """Infinite loop to stress CPU."""
    while True:
        _ = sum(range(1000000))

if __name__ == "__main__":
    print("=" * 60)
    print("CyberShield - CPU Attack Simulator")
    print("=" * 60)
    print()
    print("This will spike CPU to ~100% for 30 seconds.")
    print("The monitor should detect this as 'CPU Exhaustion / DoS Attack'")
    print()
    
    duration = 30
    num_cores = multiprocessing.cpu_count()
    
    print(f"Starting CPU stress on {num_cores} cores for {duration} seconds...")
    print("Watch the monitor in the other terminal!")
    print()
    
    # Start stress processes
    processes = []
    for i in range(num_cores):
        p = multiprocessing.Process(target=cpu_stress)
        p.start()
        processes.append(p)
        print(f"  Core {i+1}/{num_cores} stressed")
    
    print()
    print(f"Attack running... ({duration} seconds)")
    
    # Wait
    time.sleep(duration)
    
    # Stop
    print()
    print("Stopping attack...")
    for p in processes:
        p.terminate()
        p.join()
    
    print("✓ Attack stopped")
    print()
    print("Check the monitor - it should have detected the intrusion!")
