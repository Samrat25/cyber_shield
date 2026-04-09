#!/usr/bin/env python3
"""
Test script to verify PeerRegistry creates peers.json file correctly
"""

import json
from pathlib import Path
from cybershield.commands.network import PeerRegistry

def test_peer_registry():
    print("Testing PeerRegistry...")
    
    # Create registry
    registry = PeerRegistry()
    
    # Register a test peer
    print("\n1. Registering test peer...")
    registry.register("test-kali", "192.168.1.50", {"os": "Kali Linux"})
    
    # Check file exists - use correct path
    peers_file = Path.home() / ".cybershield" / "logs" / "peers.json"
    if peers_file.exists():
        print(f"✓ File created: {peers_file}")
        
        # Read and display content
        with open(peers_file) as f:
            data = json.load(f)
        print(f"\n2. File content:")
        print(json.dumps(data, indent=2))
    else:
        print(f"✗ File NOT created: {peers_file}")
        return False
    
    # Update metrics
    print("\n3. Updating metrics...")
    registry.update_metrics("test-kali", {
        "cpu_percent": 45.2,
        "memory_percent": 62.8,
        "process_count": 156,
        "verdict": "safe"
    })
    
    # Read updated content
    with open(peers_file) as f:
        data = json.load(f)
    print(f"\n4. Updated content:")
    print(json.dumps(data, indent=2))
    
    # Verify data
    peer = data.get("test-kali")
    if peer:
        print(f"\n5. Verification:")
        print(f"   Node ID: {peer.get('node_id')}")
        print(f"   IP: {peer.get('ip')}")
        print(f"   CPU: {peer.get('cpu_percent')}%")
        print(f"   Memory: {peer.get('memory_percent')}%")
        print(f"   OS: {peer.get('os')}")
        print(f"   Status: {peer.get('status')}")
        print("\n✓ PeerRegistry working correctly!")
        return True
    else:
        print("\n✗ Peer data not found in file")
        return False

if __name__ == "__main__":
    success = test_peer_registry()
    exit(0 if success else 1)
