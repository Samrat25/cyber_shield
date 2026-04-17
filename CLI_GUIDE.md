# CyberShield CLI Guide

Complete reference for all CyberShield command-line interface commands.

## Table of Contents

- [Installation](#installation)
- [Node Commands](#node-commands)
- [Network Commands](#network-commands)
- [Dashboard Commands](#dashboard-commands)
- [ML Commands](#ml-commands)
- [Status Commands](#status-commands)
- [Common Workflows](#common-workflows)

---

## Installation

### Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Install CyberShield

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Verify installation
cybershield --help
```

---

## Node Commands

### `cybershield node init`

Initialize node configuration.

**Usage:**
```bash
cybershield node init
```

**What it does:**
- Creates node configuration file
- Generates node ID (hostname)
- Detects local IP address
- Saves to `~/.cybershield/config/node_config.json`

**Output:**
```
╭───────────────────────────────────────╮
│ CyberShield Node Initialization       │
╰───────────────────────────────────────╯

✓ Node initialized
  Node ID: SAMRAT
  Local IP: 10.69.115.68
  Config: C:\Users\...\node_config.json
```

**When to use:**
- First time setup
- After reinstalling system
- To reset node configuration

---

### `cybershield node register`

Register node on blockchain and IPFS.

**Usage:**
```bash
cybershield node register

# Force re-registration
cybershield node register --force
```

**Options:**
- `--force` - Re-register even if already registered

**What it does:**
- Pins node info to IPFS (gets CID)
- Registers on Aptos blockchain (gets TX hash)
- Saves state to `~/.cybershield/logs/node_state.json`
- Logs to Supabase database

**Output:**
```
╭───────────────────────────────────────╮
│ Node Registration                     │
╰───────────────────────────────────────╯

  Node ID: SAMRAT
  IP: 10.69.115.68

✓ IPFS CID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  → https://gateway.pinata.cloud/ipfs/QmXXXX...

✓ TX Hash: 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  → https://explorer.aptoslabs.com/txn/0xXXXX...

╭───────────────────────────────────────╮
│ ✓ Node 'SAMRAT' registered!          │
│ Blockchain and IPFS records confirmed│
╰───────────────────────────────────────╯
```

**Requirements:**
- Node must be initialized first
- `.env` file with APTOS and PINATA credentials
- Internet connection

**When to use:**
- After `node init`
- Before starting monitoring
- To update registration after IP change

---

### `cybershield node monitor`

Start real-time monitoring with ML detection.

**Usage:**
```bash
# Basic monitoring (no P2P)
cybershield node monitor

# With P2P networking (server mode)
cybershield node monitor --p2p --port 8766

# Connect to existing P2P network (client mode)
cybershield node monitor --p2p --connect 10.69.115.68:8765
```

**Options:**
- `--p2p` / `--no-p2p` - Enable/disable P2P networking (default: disabled)
- `--port INTEGER` - P2P port to listen on (default: 8766)
- `--connect ADDRESS` - Connect to peer address (e.g., 10.69.115.68:8765)

**What it does:**
- Collects system metrics every 5 seconds
- Runs custom ML model for detection
- Analyzes with threat classifier
- Uses observation window (20s, 66% threshold)
- Logs safe heartbeats to IPFS (every 30s)
- Fires intrusion alert when attack detected
- Broadcasts threats to P2P network (if enabled)

**Output (Normal):**
```
╭───────────────────────────────────────────────────────────╮
│ CyberShield Monitoring - Node: SAMRAT                     │
│ Custom ML model active | Blockchain logging enabled       │
│ Observation window: 20s (66% threshold = 3/4 warnings)    │
│ Extreme CPU override                                      │
│ P2P: Disabled                                             │
│ Press Ctrl+C to stop                                      │
╰───────────────────────────────────────────────────────────╯

16:45:00  ● SAFE  CPU  35.2%  MEM  90.1%  PROCS 265  conf=0.82
  ↑ Heartbeat: QmXXXXXXXXXXXXXXXXXXXXXXXX...
16:45:05  ● SAFE  CPU  28.3%  MEM  89.5%  PROCS 263  conf=0.75
16:45:10  ● SAFE  CPU  31.7%  MEM  91.2%  PROCS 264  conf=0.79
```

**Output (Attack Detected):**
```
16:47:15  ⚠ WARNING [1/4 readings]  CPU 100.0%  MEM  85.4%  Threat: CPU Exhaustion / DoS Attack  conf=0.85
16:47:20  ⚠ WARNING [2/4 readings]  CPU 100.0%  MEM  84.8%  Threat: CPU Exhaustion / DoS Attack  conf=0.85
16:47:25  ⚠ WARNING [3/4 readings]  CPU 100.0%  MEM  85.2%  Threat: CPU Exhaustion / DoS Attack  conf=0.85

╭────────────────────────────────────────────────────────────────────╮
│ ⚠  INTRUSION CONFIRMED — SAMRAT                                    │
│                                                                    │
│   Observation: 3 of 4 readings anomalous                           │
│   Attack Type: CPU Exhaustion / DoS Attack                         │
│   Severity   : HIGH                                                │
│   Confidence : 85.0%                                               │
│                                                                    │
│   Payload — Metric Deviations from YOUR Baseline:                  │
│   ────────────────────────────────────────────────                 │
│   CPU      100.0%  baseline=36.6%  spike=+6.32σ                   │
│   MEM       85.2%  baseline=90.5%  spike=-1.32σ                   │
│   PROCS     276    baseline=270    spike=+0.20σ                   │
│   NET PKT deviation  +2.15σ                                        │
│   NET BYT deviation  +3.42σ                                        │
│   DISK    deviation  +0.85σ                                        │
│   ────────────────────────────────────────────────                 │
│   MAX DEVIATION: 6.32σ                                             │
│                                                                    │
│   Primary trigger: CPU spiked +6.3σ above your personal baseline  │
╰────────────────────────────────────────────────────────────────────╯

✓ Evidence CID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
✓ IPFS Gateway: https://gateway.pinata.cloud/ipfs/QmXXXX...
✓ ZK Proof: 102260ec8a680310964d5d5a1144ed18... (sha256-commitment)
✓ TX Hash: 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

╭─────────────────────────────────────────────────────╮
│ NODE QUARANTINED                                    │
│                                                     │
│ This node has been flagged and isolated.            │
│ Evidence permanently stored on IPFS and blockchain. │
╰─────────────────────────────────────────────────────╯
```

**Stop Monitoring:**
- Press `Ctrl+C` to stop gracefully

**When to use:**
- Main monitoring command
- Run continuously for protection
- Use with dashboard for visualization

---

## Network Commands

### `cybershield network listen`

Start P2P server and wait for peer connections.

**Usage:**
```bash
# Default port 8765
cybershield network listen

# Custom port
cybershield network listen --port 8766
```

**Options:**
- `--port INTEGER` - Port to listen on (default: 8765)

**What it does:**
- Starts WebSocket server on specified port
- Waits for peer connections
- Receives and logs peer metrics
- Saves peer data to `~/.cybershield/logs/peers.json`
- Dashboard reads this file for topology

**Output:**
```
╭──────────────────────────────────────────────╮
│ P2P Network Server — Real WebSocket Listener │
╰──────────────────────────────────────────────╯

✓ Server starting on port 8765
Waiting for peer connections...
✓ WebSocket server listening on 0.0.0.0:8765

✓ Peer registered: kali-kali (192.168.1.50)
← kali-kali: CPU=5.2%  MEM=42.3%
← kali-kali: CPU=3.1%  MEM=42.4%
← kali-kali: CPU=4.7%  MEM=42.5%
```

**Stop Server:**
- Press `Ctrl+C` to stop

**When to use:**
- When you want dedicated P2P server
- To accept connections from multiple peers
- For dashboard topology visualization

**Note:**
- Cannot run on same port as `node monitor --p2p`
- Use different ports or choose one approach

---

### `cybershield network connect`

Connect to a peer node as a pure client (no server).

**Usage:**
```bash
# Connect to peer (must include port)
cybershield network connect 10.69.115.68:8765
```

**Arguments:**
- `PEER_ADDRESS` - Address of peer to connect to (format: IP:PORT)

**What it does:**
- Connects to specified peer as client only
- Does not start a server
- Maintains connection until stopped

**Output:**
```
╭────────────────────────────╮
│ Connecting to Peer Network │
╰────────────────────────────╯

  Your Node: SAMRAT
  Peer: 192.168.1.50:8765

Connecting...

✓ Connected successfully!
  Total peers: 1

Press Ctrl+C to disconnect
```

**When to use:**
- Rarely used directly
- Better to use `kali_peer.py` script for Kali connections
- Or use `node monitor --p2p --connect` for monitoring with P2P

**Note:**
- Peer address MUST include port (e.g., 192.168.1.50:8765)
- This is a client-only connection (doesn't start server)
- For most use cases, use the Kali peer script instead

---

### `cybershield network peers`

Show connected peers (requires active monitoring).

**Usage:**
```bash
cybershield network peers
```

**Output:**
```
This command requires an active monitoring session.
Run 'cybershield node monitor --p2p' to enable P2P networking.
```

**When to use:**
- To check peer status
- Currently requires active monitor session
- Better to check dashboard for peer info

---

## Dashboard Commands

### `cybershield dashboard`

Launch web dashboard for visualization.

**Usage:**
```bash
# Start dashboard
cybershield dashboard

# Custom port
cybershield dashboard --port 5001
```

**Options:**
- `--port INTEGER` - Port to run dashboard on (default: 5000)

**What it does:**
- Starts Flask web server
- Generates secure session key
- Collects metrics in background
- Serves real-time data via API
- Provides web interface

**Output:**
```
╭───────────────────────────────────────╮
│ CyberShield Dashboard                 │
╰───────────────────────────────────────╯

✓ Dashboard running on http://localhost:5000
✓ Session key: abc123def456

Open this URL in your browser:
  http://localhost:5000?key=abc123def456

Press Ctrl+C to stop
```

**Features:**
- Real-time metrics chart (CPU, Memory, Anomaly Risk)
- Network topology diagram
- Event log with blockchain links
- Statistics (checks, threats, safe rate, nodes)
- Auto-refresh every 5 seconds

**Stop Dashboard:**
- Press `Ctrl+C` to stop

**When to use:**
- For visual monitoring
- To see P2P network topology
- To view historical events
- To access IPFS/blockchain links

---

## ML Commands

### `cybershield ml train`

Train ML models (advanced - not typically needed).

**Usage:**
```bash
cybershield ml train
```

**What it does:**
- Trains ensemble ML models
- Generates synthetic training data based on baseline
- Saves models to `~/.cybershield/models/`

**When to use:**
- Rarely needed (models pre-trained)
- If you want to retrain with different parameters
- For experimentation

---

### `cybershield ml test`

Test ML detection on sample data.

**Usage:**
```bash
cybershield ml test
```

**What it does:**
- Loads trained models
- Tests on sample metrics
- Shows detection results

**When to use:**
- To verify ML models are working
- For debugging
- To understand detection behavior

---

## Status Commands

### `cybershield status`

Show system status and configuration.

**Usage:**
```bash
cybershield status
```

**What it does:**
- Shows node configuration
- Displays registration status
- Shows blockchain/IPFS status
- Lists active connections

**When to use:**
- To check if node is registered
- To verify configuration
- For troubleshooting

---

## Common Workflows

### First-Time Setup

```bash
# 1. Activate virtual environment
.\venv\Scripts\activate

# 2. Initialize node
cybershield node init

# 3. Register on blockchain
cybershield node register

# 4. Start monitoring
cybershield node monitor
```

### Daily Monitoring

```bash
# Terminal 1: Start monitoring
cybershield node monitor

# Terminal 2: Start dashboard
cybershield dashboard
# Open browser to displayed URL
```

### P2P Network Setup

```bash
# Windows Terminal 1: P2P Server
cybershield network listen --port 8765

# Windows Terminal 2: Monitoring
cybershield node monitor

# Windows Terminal 3: Dashboard
cybershield dashboard

# Kali Terminal: Connect peer
python3 kali_peer.py --server <WINDOWS_IP>:8765
```

### Attack Testing

```bash
# Terminal 1: Monitoring (must be running)
cybershield node monitor

# Terminal 2: Run attack
python windows_cpu_attack.py

# Terminal 3: Watch dashboard
# Open browser to dashboard URL
```

---

## Environment Variables

Configure via `.env` file:

```env
# Blockchain
APTOS_NETWORK=testnet
APTOS_NODE_URL=https://fullnode.testnet.aptoslabs.com/v1
APTOS_PRIVATE_KEY=your_key_here
APTOS_ADDRESS=your_address_here

# IPFS
PINATA_JWT=your_jwt_here

# P2P
P2P_PORT=8765
P2P_HOST=0.0.0.0

# ML
ML_CHECK_INTERVAL=5
ML_ENSEMBLE_THRESHOLD=0.6
METRICS_HISTORY_SIZE=100
HEARTBEAT_INTERVAL=30
```

---

## Troubleshooting

### Command Not Found

```bash
# Ensure package is installed
pip install -e .

# Verify installation
cybershield --help
```

### Port Already in Use

```bash
# Use different port
cybershield network listen --port 8766
cybershield dashboard --port 5001
```

### Node Not Registered

```bash
# Check status
cybershield status

# Re-register
cybershield node register --force
```

### No Internet Connection

- System works offline with offline CIDs
- IPFS/blockchain logging will fail gracefully
- Local logging continues
- Will sync when connection restored

---

## Tips

1. **Always activate virtual environment** before running commands
2. **Run dashboard in separate terminal** from monitoring
3. **Use P2P server on port 8765** and monitor on 8766 to avoid conflicts
4. **Check dashboard URL** includes the session key parameter
5. **Wait 10-15 seconds** for attack detection (observation window)
6. **Press Ctrl+C once** to stop gracefully, twice to force quit

---

## Getting Help

```bash
# General help
cybershield --help

# Command-specific help
cybershield node --help
cybershield node monitor --help
cybershield network --help
cybershield dashboard --help
```

---

**Version**: 1.0.0  
**Last Updated**: April 2026
