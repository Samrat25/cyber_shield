# CyberShield Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Aptos CLI (for blockchain deployment)
- 4GB RAM minimum
- Internet connection

## Installation Methods

### Method 1: Install from Source (Recommended for Hackathon)

```bash
# Clone or navigate to the project directory
cd cybershield

# Install in development mode
pip install -e .

# Verify installation
cybershield --version
```

### Method 2: Install from PyPI (When Published)

```bash
pip install cybershield
```

### Method 3: Install with Optional Dependencies

```bash
# Full installation with all ML models
pip install cybershield[full]

# Minimal installation (basic models only)
pip install cybershield[minimal]
```

## Configuration

### 1. Set up Environment Variables

Create a `.env` file in your project root or `~/.cybershield/`:

```bash
# Blockchain Configuration
APTOS_NETWORK=testnet
APTOS_NODE_URL=https://fullnode.testnet.aptoslabs.com/v1
APTOS_PRIVATE_KEY=0x...your_private_key...
APTOS_ADDRESS=0x...your_address...

# IPFS Configuration
PINATA_JWT=eyJ...your_jwt_token...

# P2P Configuration (Optional)
P2P_PORT=8765
P2P_HOST=0.0.0.0

# ML Configuration (Optional)
ML_CHECK_INTERVAL=5
ML_ENSEMBLE_THRESHOLD=0.6
```

### 2. Deploy Smart Contract (One-time Setup)

```bash
# Install Aptos CLI if not already installed
curl -fsSL "https://aptos.dev/scripts/install_cli.py" | python3

# Initialize Aptos account
aptos init --network testnet

# Fund your account
aptos account fund-with-faucet \
  --account default \
  --faucet-url https://faucet.testnet.aptoslabs.com \
  --amount 100000000

# Deploy contract
cd contract
aptos move compile --named-addresses cybershield_addr=default
aptos move publish --named-addresses cybershield_addr=default --network testnet

# Initialize contract storage
aptos move run \
  --function-id default::threat_logger::init_store \
  --network testnet

cd ..
```

### 3. Initialize CyberShield

```bash
# Initialize node configuration
cybershield node init

# Train ML models
cybershield ml train --advanced

# Register on blockchain
cybershield node register
```

## Verification

```bash
# Check installation
cybershield --version

# Check node status
cybershield status

# Check ML models
cybershield ml info

# Test ML detection
cybershield ml test
```

## Quick Start

```bash
# Start monitoring
cybershield node monitor

# In another terminal, simulate an attack
cybershield attack simulate --type cpu
```

## Troubleshooting

### ImportError: No module named 'cybershield'

```bash
# Reinstall in development mode
pip install -e .
```

### ML models not found

```bash
# Retrain models
cybershield ml train --advanced
```

### Blockchain connection failed

```bash
# Check your .env file
# Verify Aptos testnet is accessible
# Fund your account if needed
```

### P2P connection refused

```bash
# Check firewall settings
# Verify port is not in use: netstat -an | grep 8765
# Try a different port: cybershield network listen --port 8766
```

## Uninstallation

```bash
# Remove package
pip uninstall cybershield

# Remove configuration and data (optional)
rm -rf ~/.cybershield
```

## Next Steps

- Read [HACKATHON_DEMO.md](HACKATHON_DEMO.md) for demo guide
- Check [README.md](README.md) for usage examples
- Join our community for support

## System Requirements

### Minimum:
- CPU: 2 cores
- RAM: 4GB
- Disk: 1GB free space
- Network: Broadband internet

### Recommended:
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 5GB+ free space
- Network: High-speed internet

## Platform Support

- ✅ Linux (Ubuntu 20.04+, Debian 10+)
- ✅ macOS (10.15+)
- ✅ Windows 10/11 (with WSL2 recommended)

## Dependencies

Core dependencies are automatically installed:
- psutil (system monitoring)
- scikit-learn (ML models)
- rich (CLI interface)
- aptos-sdk (blockchain)
- websockets (P2P networking)
- click (CLI framework)

Optional dependencies:
- tensorflow (deep learning models)
- xgboost (gradient boosting)
- pandas (data analysis)

## Support

For installation issues:
1. Check logs: `~/.cybershield/logs/`
2. Run diagnostics: `cybershield status`
3. Verify environment: `cybershield --version`
4. Check dependencies: `pip list | grep cybershield`
