# 🛡️ CyberShield - Decentralized Intrusion Detection System

A blockchain-based, ML-powered intrusion detection system with P2P threat intelligence sharing, IPFS evidence storage, and zero-knowledge proofs.

## 🌟 Features

- **Custom ML Detection**: RandomForest model trained on your system's baseline
- **Blockchain Logging**: Immutable threat records on Aptos blockchain
- **IPFS Storage**: Decentralized evidence storage via Pinata
- **P2P Network**: Real-time threat intelligence sharing between nodes
- **Zero-Knowledge Proofs**: Privacy-preserving threat verification
- **Real-Time Dashboard**: Live monitoring with network topology visualization
- **Observation Window**: Rate-limited detection (3/4 warnings = alert)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CyberShield Node                        │
├─────────────────────────────────────────────────────────────┤
│  System Monitor  →  Custom ML Model  →  Threat Classifier  │
│       ↓                    ↓                    ↓           │
│  Observation Window (20s, 66% threshold)                    │
│       ↓                                                      │
│  INTRUSION CONFIRMED                                         │
│       ↓                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   IPFS   │  │  Aptos   │  │ ZK Proof │  │   P2P    │  │
│  │ Evidence │  │   TX     │  │  Hash    │  │ Broadcast│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Requirements

- **Python**: 3.10+
- **OS**: Windows (primary), Linux (peer nodes)
- **Dependencies**: See `requirements.txt`

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd cyber_shield

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### 2. Configuration

Create `.env` file:

```env
# Aptos Blockchain
APTOS_NETWORK=testnet
APTOS_PRIVATE_KEY=your_private_key_here
APTOS_ADDRESS=your_address_here

# IPFS (Pinata)
PINATA_JWT=your_pinata_jwt_here

# Optional
P2P_PORT=8765
ML_CHECK_INTERVAL=5
```

### 3. Initialize Node

```bash
# Initialize node configuration
cybershield node init

# Register on blockchain and IPFS
cybershield node register
```

### 4. Start Monitoring

```bash
# Basic monitoring
cybershield node monitor

# With P2P enabled
cybershield node monitor --p2p --port 8766

# View dashboard
cybershield dashboard
# Open http://localhost:5000
```

## 📊 System Components

### Custom ML Model
- **Type**: RandomForestClassifier
- **Features**: 8 rolling statistics (value, mean, std, zscore, delta, delta_pct, max, max_ratio)
- **Training**: Pre-trained on your system baseline
- **Location**: `cybershield/ml/model/`

### Threat Detection
- **Extreme CPU Override**: CPU >90% = automatic anomaly
- **Absolute Threshold**: CPU >85% = DoS attack
- **Z-Score Threshold**: 1.5σ deviation from baseline
- **Observation Window**: 20 seconds, 66% threshold (3/4 warnings)

### Blockchain Integration
- **Network**: Aptos Testnet
- **Smart Contract**: Threat logger with node registry
- **Explorer**: https://explorer.aptoslabs.com/

### IPFS Storage
- **Provider**: Pinata Cloud
- **Gateway**: https://gateway.pinata.cloud/ipfs/
- **Content**: Threat evidence, metrics, ZK proofs

## 🌐 P2P Network

### Architecture
```
Windows Node (Primary)  ←→  Kali Node (Peer)
     ↓                           ↓
  Monitor                   Send Metrics
  Detect                    Receive Alerts
  Broadcast                 Update Dashboard
```

### Setup
See `ATTACK_DEMO.md` for complete P2P setup instructions.

## 📖 Documentation

- **CLI_GUIDE.md** - Complete command reference
- **ATTACK_DEMO.md** - Attack testing and P2P setup

## 🔧 CLI Commands

```bash
# Node Management
cybershield node init          # Initialize node
cybershield node register      # Register on blockchain
cybershield node monitor       # Start monitoring

# Network Management
cybershield network listen     # Start P2P server
cybershield network connect    # Connect to peer
cybershield network peers      # Show connected peers

# Dashboard
cybershield dashboard          # Start web dashboard

# ML Management
cybershield ml train           # Train ML models
cybershield ml test            # Test detection
cybershield ml baseline        # Save system baseline

# Status
cybershield status             # Show system status
```

## 🎯 Detection Flow

1. **Monitor** collects metrics every 5 seconds
2. **Custom ML Model** analyzes rolling statistics
3. **Threat Classifier** computes z-scores from baseline
4. **Hybrid Detection** combines ML + classifier + absolute thresholds
5. **Observation Window** requires 3/4 anomalous readings
6. **Alert Fired** when threshold reached
7. **Evidence Logged** to IPFS, blockchain, ZK proof
8. **P2P Broadcast** alerts all connected peers
9. **Dashboard Updated** shows compromised state

## 🧪 Testing

### Local Attack (Windows)
```bash
python windows_cpu_attack.py
```

### Remote Attack (Kali → Windows)
```bash
# Kali terminal
stress-ng --cpu 4 --timeout 45s
```

### Expected Detection Time
- First warning: ~5 seconds
- Second warning: ~10 seconds
- Third warning: ~15 seconds
- **INTRUSION CONFIRMED**: ~15 seconds

## 📁 Project Structure

```
cyber_shield/
├── cybershield/              # Main package
│   ├── blockchain/           # Aptos integration
│   ├── commands/             # CLI commands
│   ├── core/                 # Monitoring & detection
│   ├── ml/                   # ML models
│   │   └── model/            # Trained models
│   ├── network/              # P2P networking
│   └── storage/              # IPFS integration
├── dashboard/                # Web dashboard
├── contract/                 # Move smart contracts
├── logs/                     # Local logs (workspace)
├── ~/.cybershield/           # User data directory
│   ├── logs/                 # System logs
│   │   ├── node_state.json   # Node status
│   │   ├── peers.json        # Connected peers
│   │   └── baseline.json     # System baseline
│   └── config/               # Node configuration
├── windows_cpu_attack.py     # Local attack script
├── kali_peer.py              # Kali peer connector
└── requirements.txt          # Dependencies
```

## 🔐 Security Features

### Zero-Knowledge Proofs
- SHA-256 commitment of threat data
- Verifiable without revealing raw metrics
- Cryptographic hash of model weights

### Blockchain Immutability
- Tamper-proof threat records
- Timestamped evidence
- Public verification

### Decentralized Storage
- No single point of failure
- Content-addressed (CID)
- Permanent evidence retention

## 🎨 Dashboard Features

### Real-Time Metrics
- CPU, Memory, Process count
- Anomaly Risk % (0-100 scale)
- Color-coded risk line (green/orange/red)
- Dual Y-axis for clarity

### Network Topology
- Visual P2P network diagram
- Real-time peer metrics
- Compromised node highlighting
- Connection status (active/severed)

### Event Log
- Blockchain-verified events
- IPFS CID links
- Aptos TX explorer links
- Threat classification

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
cybershield network listen --port 8766
cybershield node monitor --p2p --port 8767
```

### Dashboard Not Updating
```bash
# Check logs exist
ls ~/.cybershield/logs/

# Restart dashboard
cybershield dashboard

# Hard refresh browser (Ctrl+Shift+R)
```

### Detection Not Working
```bash
# Check baseline exists
cat ~/.cybershield/logs/baseline.json

# Retrain if needed
cybershield ml baseline

# Test detection
python windows_cpu_attack.py
```

### Kali Peer Can't Connect
```bash
# Windows - check IP
ipconfig

# Windows - allow firewall
netsh advfirewall firewall add rule name="CyberShield" dir=in action=allow protocol=TCP localport=8765

# Kali - test connection
telnet <WINDOWS_IP> 8765
```

## 📊 Performance

- **Detection Latency**: 10-15 seconds
- **False Positive Rate**: <5% (with observation window)
- **Resource Usage**: <2% CPU, <100MB RAM
- **Dashboard Update**: 5 second polling
- **P2P Heartbeat**: 5 second interval

## 🤝 Contributing

This is a research/demo project. For production use:
1. Use production blockchain network
2. Implement proper key management
3. Add authentication/authorization
4. Scale P2P network with DHT
5. Add encrypted communication

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- **Aptos Labs** - Blockchain infrastructure
- **Pinata** - IPFS pinning service
- **scikit-learn** - ML framework
- **Chart.js** - Dashboard visualization

## 📞 Support

For issues and questions:
1. Check `CLI_GUIDE.md` for command help
2. Check `ATTACK_DEMO.md` for testing help
3. Review troubleshooting section above

## 🚀 Future Enhancements

- [ ] Multi-metric ML models (CPU, MEM, NET)
- [ ] Automated threat response
- [ ] Mobile dashboard app
- [ ] Distributed training
- [ ] Smart contract upgrades
- [ ] Advanced ZK-SNARK proofs
- [ ] Federated learning across nodes

---

**CyberShield v1.0** - Decentralized IDS for the Modern Era
