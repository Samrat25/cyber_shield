# CyberShield Setup Complete! ✓

## What's Been Done

### 1. Dependencies Installed ✓
- Python virtual environment created
- All required packages installed (psutil, scikit-learn, aptos-sdk, rich, etc.)

### 2. Smart Contract Deployed ✓
- Move contract compiled successfully
- Deployed to Aptos testnet
- Contract address: `0x851c087b280c6853667631d72147716d15276a7383608257ca9736eb01cd6af9`
- Deployment TX: `0xc051370f6a59314479b596db85421b3914fc62b715c6019213923393bc1e0d5e`
- Initialization TX: `0x0d5f345460e653176c19105ce9333c624d6b59846a373d6e1719548c60a3b41c`

### 3. ML Model Trained ✓
- Isolation Forest model trained on baseline data
- Model saved to `logs/model.pkl`

### 4. Node Registered ✓
- Node ID: SAMRAT
- IP: 192.168.29.58
- IPFS CID: `QmR6EEtcsz1CxQQyuWhabnEirLtYCTQbF9XYW1nM15T1NB`
- Registration TX: `0xe6be33ea83ab7f6a3313a2105c6ef3524726048ff1e714e27481436743d054e5`

### 5. All Systems Tested ✓
- System metrics collection working
- ML anomaly detection working
- IPFS pinning working
- Blockchain transactions working

## View Your Deployment

### Aptos Explorer
- Account: https://explorer.aptoslabs.com/account/0x851c087b280c6853667631d72147716d15276a7383608257ca9736eb01cd6af9?network=testnet
- Registration TX: https://explorer.aptoslabs.com/txn/0xe6be33ea83ab7f6a3313a2105c6ef3524726048ff1e714e27481436743d054e5?network=testnet

### IPFS Gateway
- Registration Data: https://gateway.pinata.cloud/ipfs/QmR6EEtcsz1CxQQyuWhabnEirLtYCTQbF9XYW1nM15T1NB

## How to Run the Demo

### Terminal 1: Your Node (Main Demo)
```bash
.\venv\Scripts\activate
python cli.py monitor
```

### Terminal 2: Mock Peer Nodes (Visual Effect)
```bash
.\venv\Scripts\activate
python mock_nodes.py
```

### Terminal 3: Attack Simulation (When Ready)
To trigger an anomaly, you can:
- Run CPU stress: `stress --cpu 8 --timeout 25` (if you have stress installed)
- Or just wait - your current system load (CPU 46%, MEM 91%) might already trigger it!

## What Happens During Monitoring

1. Every 5 seconds: System checks CPU, memory, processes
2. ML model analyzes metrics for anomalies
3. Safe status: Prints green "SAFE" message
4. Every 30 seconds: Pins heartbeat to IPFS
5. On anomaly detection:
   - Evidence pinned to IPFS (permanent)
   - Transaction logged on Aptos blockchain (immutable)
   - Node quarantined from network
   - All proof URLs displayed

## Available Commands

```bash
python cli.py register   # Register node (already done)
python cli.py monitor    # Start monitoring (run this for demo)
python cli.py status     # Show current status
python cli.py train      # Retrain ML model
python test_monitor.py   # Quick functionality test
```

## Demo Tips

1. Open browser tabs BEFORE starting monitor:
   - Your Aptos account page
   - Keep IPFS gateway ready to paste CIDs

2. When anomaly fires:
   - CLI will print the new IPFS CID
   - CLI will print the new TX hash
   - Copy/paste into browser to show judges
   - Everything is REAL and verifiable!

3. The mock_nodes.py is just for visual effect
   - Shows "network topology"
   - Makes demo look more impressive
   - Not required for core functionality

## System Status

Current metrics show your system is running hot:
- CPU: 46.2%
- Memory: 91.1%
- This might trigger anomaly detection quickly!

If you want to ensure it triggers, you can:
1. Open several browser tabs
2. Run a video or heavy application
3. Or just wait - the ML model is sensitive

## Everything is Ready! 🚀

Your CyberShield system is fully deployed and operational. Just run `python cli.py monitor` to start the demo!
