#!/usr/bin/env python3
"""
Test ZK proof generation with and without Docker.
"""

import sys
from cybershield.zk_proof import generate_proof

print("=" * 60)
print("Testing ZK Proof Generation")
print("=" * 60)
print()

# Test data
metrics = {
    "node_id": "TEST-NODE",
    "cpu_percent": 85.3,
    "memory_percent": 97.8,
}
score = 0.95
cid = "QmTestCID123456789"

print("Test Input:")
print(f"  Node ID: {metrics['node_id']}")
print(f"  Score: {score}")
print(f"  CID: {cid}")
print()

# Generate proof
print("Generating proof...")
proof = generate_proof(metrics, score, cid)

print()
print("=" * 60)
print("Proof Generated:")
print("=" * 60)
print(f"  Method: {proof['method']}")
print(f"  Proof Hash: {proof['proof_hash'][:32]}...")
print(f"  Commitment: {proof['commitment'][:32]}...")
print(f"  Verified: {proof['verified']}")
print(f"  Public Signals: {len(proof['public_signals'])} items")
print()

if proof['method'] == 'docker-snarkjs':
    print("✓ SUCCESS: Docker ZK proof generated!")
    print("  This is a REAL cryptographic proof.")
    sys.exit(0)
elif proof['method'] == 'sha256-commitment':
    print("⚠ FALLBACK: SHA256 commitment used")
    print("  Docker container not available.")
    print("  This is still cryptographically sound, just not a ZK circuit.")
    print()
    print("To enable Docker ZK proofs:")
    print("  1. Make sure Docker Desktop is running")
    print("  2. Run: docker build -t cybershield-zk:latest docker/zk/")
    print("  3. Test: docker run --rm -e NODE_ID=test -e SCORE=0.95 -e CID=QmTest -e COMMITMENT=abc123 cybershield-zk:latest")
    sys.exit(1)
else:
    print("✗ ERROR: Unknown proof method")
    sys.exit(1)
