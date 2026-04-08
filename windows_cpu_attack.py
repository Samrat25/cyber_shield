#!/usr/bin/env python3
"""
Test script to trigger a REAL CPU attack that will be detected.
Run this while cybershield node monitor is running.
"""

import multiprocessing
import time
import sys

def cpu_burn():
    """Burn CPU in infinite loop."""
    while True:
        _ = sum(i*i for i in range(10000))

def main():
    print("=" * 60)
    print("CyberShield - Real CPU Attack Test")
    print("=" * 60)
    print("\nThis will spike CPU to trigger detection.")
    print("Watch the monitor terminal for intrusion alert.\n")
    
    duration = 45  # Increased from 30 to 45 seconds
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except:
            duration = 45
    
    cores = multiprocessing.cpu_count()
    
    print(f"Starting CPU attack:")
    print(f"  Duration: {duration} seconds")
    print(f"  Cores: {cores}")
    print(f"  Expected detection: ~10-15 seconds (3/4 warnings)\n")
    
    # Spawn CPU burners
    processes = []
    for i in range(cores):
        p = multiprocessing.Process(target=cpu_burn)
        p.start()
        processes.append(p)
        print(f"  [+] Started burner {i+1}/{cores}")
    
    print(f"\n[*] Attack running... (Ctrl+C to stop early)")
    
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    
    print("\n[*] Stopping attack...")
    for p in processes:
        p.terminate()
        p.join()
    
    print("[✓] Attack stopped\n")
    print("Check monitor terminal for:")
    print("  - ⚠ WARNING messages")
    print("  - INTRUSION CONFIRMED alert")
    print("  - IPFS Gateway URL")
    print("  - Blockchain TX Hash")
    print()

if __name__ == "__main__":
    main()
