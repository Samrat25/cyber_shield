#!/usr/bin/env python3
"""
Quick test to verify monitor can start without errors.
"""

import sys
import asyncio
from pathlib import Path
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from cybershield.commands.node import _monitor_async

# Load state
state_file = Path("logs/node_state.json")
if not state_file.exists():
    print("✗ Node not registered. Run: cybershield node register")
    sys.exit(1)

state = json.loads(state_file.read_text())
node_id = state['node_id']

print(f"Testing monitor for node: {node_id}")
print("Will run for 10 seconds...")
print()

async def test_monitor():
    """Run monitor for 10 seconds."""
    try:
        # Create a task for monitoring
        monitor_task = asyncio.create_task(_monitor_async(node_id, state, False, 8765))
        
        # Wait for 10 seconds
        await asyncio.sleep(10)
        
        # Cancel the monitor
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        print("\n✓ Monitor test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run test
success = asyncio.run(test_monitor())
sys.exit(0 if success else 1)
