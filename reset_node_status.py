#!/usr/bin/env python3
"""
Reset node status back to online after a demo.
Run this between demos to reset the quarantine state.
"""

import json
from pathlib import Path

state_file = Path("logs/node_state.json")

if state_file.exists():
    with open(state_file) as f:
        state = json.load(f)
    
    print(f"Current status: {state.get('status', 'unknown')}")
    
    state['status'] = 'online'
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"✓ Status reset to: online")
    print("\nYou can now run 'cybershield node monitor' again.")
else:
    print("✗ No node_state.json found. Run 'cybershield node register' first.")
