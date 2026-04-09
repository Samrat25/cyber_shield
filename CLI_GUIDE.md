# CyberShield CLI Guide

Complete reference for all CyberShield command-line interface commands.

## Table of Contents

1. [Node Commands](#node-commands)
2. [Network Commands](#network-commands)
3. [ML Commands](#ml-commands)
4. [Dashboard Commands](#dashboard-commands)
5. [Status Commands](#status-commands)
6. [Common Workflows](#common-workflows)

---

## Node Commands

### `cybershield node init`

Initialize node configuration.

**Usage:**
```bash
cybershield node init
```

**What it does:**
- Generates node ID from hostname
- Detects local IP address
- Creates configuration file at `~/.cybershield/config/node_config.json`

**Output:**
```
╭─────────────────────────────────────╮
│ CyberShield Node Initialization     │
╰─────────────────────────────────────╯

✓ Node initialized
  Node ID: SAMRAT
  Local IP: 192.168.1.100
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
- `--force` - Force re-registration even if already registered

**What it does:**
1. Reads node configuration
2. Pins registration data to IPFS
3. Submits transaction to Aptos blockchain
4. Saves state to `~/.cybershield/logs/node_state.json`
5. Logs to Supabase (if configured)

**Output:**
```
╭─────────────────────────────────────╮
│ Node Registration                   │
╰─────────────────────────────────────╯

  Node ID: SAMRAT
  IP: 192.168.1.100

  ✓ IPFS CID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    → https://gateway.pinata.cloud/ipfs/QmXXXX...

  ✓ TX Hash: 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    → https://explorer.aptoslabs.com/txn/0xXXXX...

╭─────────────────────────────────────────────────╮
│ ✓ Node 'SAMRAT' registered successfully!       │
│ Blockchain and IPFS records confirmed.         │
╰─────────────────────────────────────────────────╯
```

**Requirements:**
- Node must be initialized (`cybershield node init`)
- `.env` file with APTOS_PRIVATE_KEY and PINATA_JWT
- Internet connection

**When to use:**
- After initializing node
- Before starting monitoring
- To update node registration

---

### `cybershield node monitor`

Start real-time monitoring with ML detection.

**Usage:**
```bash
# Basic monitoring (no P2P)
cybershield node monitor

# With P2P server
cybershield node monitor --p2p --port 8766

# Connect to existing P2P network
cybershield node monitor --p2p --connect 192.168.1.50:8765
```

**Options:**
- `--p2p / --no-p2p` - Enable/disable P2P networking (default: disabled)
- `--port PORT` - P2P port to listen on (default: 8766)
- `--connect ADDRESS` - Connect to peer address (e.g., 192.168.1.50:8765)

**What it does:**
1. Loads custom ML model
2. Reads system baseline
3. Starts P2P server/client (if enabled)
4. Monitors system metrics every 5 seconds
5. Runs ML detection + threat classification
6. Maintains observation window (20 seconds)
7. Fires alerts when 3/4 readings are anomalous
8. Logs evidence to IPFS, blockchain, ZK proof
9. Broadcasts alerts to P2P network

**Output (Normal):**
```
╭───────────────────────────────────────────────────────────────╮
│ CyberShield Monitoring - Node: SAMRAT                        │
│ Custom ML model active | Blockchain logging enabled          │
│ Observation window: 20s (66% threshold = 3/4 warnings)       │
│ P2P: Disabled                                                 │
│ Press Ctrl+C to stop                                          │
╰───────────────────────────────────────────────────────────────╯

16:45:00  ● SAFE  CPU  35.2%  MEM  90.1%  PROCS 265  conf=0.82
16:45:05  ● SAFE  CPU  28.3%  MEM  89.5%  PROCS 263  conf=0.75
  ↑ Heartbeat: QmXXXXXXXXXXXXXXXXXXXXXXXX...
16:45:10  ● SAFE  CPU  42.1%  MEM  91.2%  PROCS 267  conf=0.68
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

**Requirements:**
- Node must be registered
- Custom ML model trained (automatic on first run)
- Baseline saved (`cybershield ml baseline`)

**When to use:**
- Primary monitoring mode
- After node registration
- To detect intrusions in real-time

**Stop monitoring:**
- Press `Ctrl+C`

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
- `--port PORT` - Port to listen on (default: 8765)

**What it does:**
1. Starts WebSocket server on specified port
2. Waits for peer connections
3. Registers peers in `~/.cybershield/logs/peers.json`
4. Receives heartbeat metrics from peers
5. Updates dashboard with peer data

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
  ← kali-kali: CPU=7.8%  MEM=43.1%
```

**Requirements:**
- Node must be initialized
- Port must be available (not in use)
- Firewall must allow incoming connections

**When to use:**
- To accept peer connections
- As central hub for P2P network
- Before connecting Kali peer

**Stop server:**
- Press `Ctrl+C`

---

### `cybershield network connect`

Connect to a peer node.

**Usage:**
```bash
cybershield network connect <PEER_ADDRESS>

# Example
cybershield network connect 192.168.1.100:8765
```

**Arguments:**
- `PEER_ADDRESS` - Peer address in format `IP:PORT`

**Options:**
- `--port PORT` - Local P2P port (default: 8765)

**What it does:**
1. Starts local P2P node
2. Connects to specified peer
3. Sends handshake
4. Maintains connection
5. Shares threat intelligence

**Output:**
```
╭─────────────────────────────────────╮
│ Connecting to Peer Network          │
╰─────────────────────────────────────╯

  Your Node: SAMRAT
  Peer: 192.168.1.50:8765

🌐 P2P Node started: SAMRAT
   Listening on 192.168.1.100:8765
✓ Connected to peer: kali-kali (192.168.1.50:8765)

✓ Connected successfully!
  Total peers: 1

Press Ctrl+C to disconnect
```

**Requirements:**
- Node must be initialized
- Peer must be listening
- Network connectivity

**When to use:**
- To join existing P2P network
- To connect to another CyberShield node
- For distributed threat detection

---

### `cybershield network peers`

Show connected peers.

**Usage:**
```bash
cybershield network peers
```

**Output:**
```
This command requires an active monitoring session.
Run 'cybershield node monitor --p2p' to enable P2P networking.
```

**Note:** This command requires P2P to be enabled in monitoring mode.

---

## ML Commands

### `cybershield ml train`

Train ML models.

**Usage:**
```bash
cybershield ml train
```

**What it does:**
1. Loads system baseline
2. Generates synthetic training data
3. Trains ensemble models:
   - Isolation Forest
   - Autoencoder (if TensorFlow available)
   - LSTM (if TensorFlow available)
   - XGBoost (if XGBoost available)
4. Saves models to `~/.cybershield/models/`

**Output:**
```
🔧 Training Advanced ML Ensemble...
  [1/4] Training Isolation Forest...
  [2/4] Training Autoencoder...
  [3/4] Training LSTM...
  [4/4] Training XGBoost...
✓ Training complete!
```

**When to use:**
- First time setup
- After changing baseline
- To retrain models with new data

---

### `cybershield ml test`

Test ML detection.

**Usage:**
```bash
cybershield ml test
```

**What it does:**
1. Loads trained models
2. Collects current system metrics
3. Runs detection
4. Displays results

**Output:**
```
Testing ML detection...

Current Metrics:
  CPU: 35.2%
  Memory: 90.1%
  Processes: 265

Detection Result:
  Verdict: SAFE
  Confidence: 0.82
  Model Scores:
    - Isolation Forest: 0.15
    - Autoencoder: 0.12
    - LSTM: 0.08
    - XGBoost: 0.10
```

**When to use:**
- To verify models are working
- To test detection without monitoring
- For debugging

---

### `cybershield ml baseline`

Save system baseline.

**Usage:**
```bash
cybershield ml baseline
```

**What it does:**
1. Collects system metrics for 60 seconds
2. Calculates mean and standard deviation
3. Saves to `~/.cybershield/logs/baseline.json`

**Output:**
```
Collecting baseline metrics (60 seconds)...
[====================] 100%

Baseline saved:
  CPU: 36.6% ± 8.2%
  Memory: 90.5% ± 3.1%
  Processes: 270 ± 15
  Network Packets: 500 ± 200
  Network Bytes: 100000 ± 50000
  Disk: 70% ± 5%

File: ~/.cybershield/logs/baseline.json
```

**When to use:**
- Before first monitoring session
- After system changes
- When false positives occur

---

## Dashboard Commands

### `cybershield dashboard`

Start web dashboard.

**Usage:**
```bash
cybershield dashboard

# Custom port
cybershield dashboard --port 5001
```

**Options:**
- `--port PORT` - Port to run on (default: 5000)

**What it does:**
1. Starts Flask web server
2. Generates secure session key
3. Serves dashboard at http://localhost:5000
4. Polls metrics every 5 seconds
5. Updates charts and topology

**Output:**
```
╭─────────────────────────────────────╮
│ CyberShield Dashboard               │
╰─────────────────────────────────────╯

✓ Dashboard running at: http://localhost:5000?key=abc123def456

Press Ctrl+C to stop
```

**Dashboard Features:**
- Real-time metrics chart (CPU, Memory, Anomaly Risk)
- Network topology diagram
- Event log with blockchain links
- Statistics (total checks, threats, safe rate)

**Requirements:**
- Node must be registered
- Monitoring should be running (for live data)

**When to use:**
- To visualize system status
- To view P2P network topology
- To access blockchain evidence

**Stop dashboard:**
- Press `Ctrl+C`

---

## Status Commands

### `cybershield status`

Show system status.

**Usage:**
```bash
cybershield status
```

**What it does:**
- Shows node configuration
- Displays registration status
- Lists connected peers
- Shows recent threats

**Output:**
```
╭─────────────────────────────────────╮
│ CyberShield Status                  │
╰─────────────────────────────────────╯

Node:
  ID: SAMRAT
  IP: 192.168.1.100
  Status: ONLINE
  Registered: Yes

Blockchain:
  Network: testnet
  Address: 0xXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

IPFS:
  Provider: Pinata
  Status: Connected

P2P Network:
  Peers: 1
  Status: Active

Recent Threats: 0
```

**When to use:**
- To check system health
- To verify configuration
- For troubleshooting

---

## Common Workflows

### First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install -e .

# 2. Configure environment
# Edit .env file with your keys

# 3. Initialize node
cybershield node init

# 4. Save baseline
cybershield ml baseline

# 5. Register node
cybershield node register

# 6. Start monitoring
cybershield node monitor
```

### Daily Monitoring

```bash
# Terminal 1: Start monitoring
cybershield node monitor

# Terminal 2: Start dashboard
cybershield dashboard
# Open http://localhost:5000
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
# Terminal 1: Start monitoring
cybershield node monitor

# Terminal 2: Run attack
python windows_cpu_attack.py

# Expected: INTRUSION CONFIRMED in ~15 seconds
```

### Troubleshooting

```bash
# Check status
cybershield status

# Verify baseline
cat ~/.cybershield/logs/baseline.json

# Test ML detection
cybershield ml test

# Retrain models
cybershield ml train

# Check node state
cat ~/.cybershield/logs/node_state.json

# Check connected peers
cat ~/.cybershield/logs/peers.json
```

---

## Environment Variables

Configure in `.env` file:

```env
# Required
APTOS_PRIVATE_KEY=your_private_key
APTOS_ADDRESS=your_address
PINATA_JWT=your_jwt_token

# Optional
APTOS_NETWORK=testnet
P2P_PORT=8765
P2P_HOST=0.0.0.0
ML_CHECK_INTERVAL=5
ML_ENSEMBLE_THRESHOLD=0.6
METRICS_HISTORY_SIZE=100
HEARTBEAT_INTERVAL=30
```

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Configuration error
- `3` - Network error
- `4` - Blockchain error
- `5` - IPFS error

---

## Tips

1. **Always save baseline first** before monitoring
2. **Use P2P on different ports** to avoid conflicts
3. **Keep dashboard open** for best visualization
4. **Check logs** in `~/.cybershield/logs/` for debugging
5. **Hard refresh browser** (Ctrl+Shift+R) if dashboard not updating
6. **Allow firewall** for P2P connections
7. **Use --force** to re-register if needed

---

**For attack testing and P2P setup, see `ATTACK_DEMO.md`**
