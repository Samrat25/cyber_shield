# Kali VM Setup — Real P2P Peer for CyberShield

This guide shows how to connect your Kali VM as a **real second node** in the CyberShield network.

## Prerequisites

- Kali VM on same WiFi as your Windows laptop
- Both machines can ping each other
- Python 3 installed on Kali (default)

## Step 1: Find Your IPs

### On Windows (your laptop):
```powershell
ipconfig | findstr IPv4
# You'll see something like: 192.168.29.58
```

### On Kali:
```bash
ip addr show | grep "inet " | grep -v 127
# You'll see something like: inet 192.168.29.XX/24
```

## Step 2: Create kali_peer.py on Kali

Save this file on your Kali VM:

```python
#!/usr/bin/env python3
# kali_peer.py
# Run on Kali: python3 kali_peer.py 192.168.29.58
# This makes Kali a REAL second node in your CyberShield network

import asyncio, json, time, socket, datetime, sys
import psutil

try:
    import websockets
except ImportError:
    import subprocess
    subprocess.run(["pip3", "install", "websockets", "psutil"], check=True)
    import websockets

TARGET_IP   = sys.argv[1] if len(sys.argv) > 1 else "192.168.29.58"
TARGET_PORT = 8765
NODE_ID     = f"kali-{socket.gethostname()}"
MY_IP       = socket.gethostbyname(socket.gethostname())

def get_metrics() -> dict:
    net  = psutil.net_io_counters()
    mem  = psutil.virtual_memory()
    return {
        "node_id"          : NODE_ID,
        "ip"               : MY_IP,
        "type"             : "real",
        "os"               : "Kali Linux",
        "timestamp"        : datetime.datetime.utcnow().isoformat(),
        "cpu_percent"      : psutil.cpu_percent(interval=0.5),
        "memory_percent"   : mem.percent,
        "process_count"    : len(psutil.pids()),
        "net_bytes_recv"   : net.bytes_recv,
        "net_bytes_sent"   : net.bytes_sent,
        "net_packets_recv" : net.packets_recv,
        "net_packets_sent" : net.packets_sent,
        "disk_percent"     : psutil.disk_usage("/").percent,
        "status"           : "online",
        "verdict"          : "safe",
    }

async def connect_and_send():
    uri = f"ws://{TARGET_IP}:{TARGET_PORT}"
    print(f"[Kali Peer] Node: {NODE_ID}")
    print(f"[Kali Peer] Connecting to CyberShield at {uri}")
    print(f"[Kali Peer] Sending heartbeats every 5s. Ctrl+C to stop.\n")
    
    while True:
        try:
            async with websockets.connect(uri, ping_interval=10) as ws:
                print(f"[Kali Peer] ✓ Connected to {TARGET_IP}:{TARGET_PORT}")
                
                # Register this node
                reg = {"type": "register", "node_id": NODE_ID,
                       "ip": MY_IP, "os": "Kali Linux"}
                await ws.send(json.dumps(reg))
                
                while True:
                    m = get_metrics()
                    msg = {"type": "heartbeat", "data": m}
                    await ws.send(json.dumps(msg))
                    print(f"  → sent: CPU={m['cpu_percent']:.1f}%  "
                          f"MEM={m['memory_percent']:.1f}%  "
                          f"PROCS={m['process_count']}")
                    await asyncio.sleep(5)
        
        except (websockets.exceptions.ConnectionClosed,
                ConnectionRefusedError, OSError) as e:
            print(f"[Kali Peer] Disconnected ({e}). Retrying in 5s...")
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("\n[Kali Peer] Stopped.")
            break

if __name__ == "__main__":
    asyncio.run(connect_and_send())
```

## Step 3: Install Dependencies on Kali

```bash
pip3 install websockets psutil
```

## Step 4: Start P2P Listener on Windows

On your Windows laptop, open a terminal and run:

```powershell
cybershield network listen
```

This starts the WebSocket server on port 8765.

## Step 5: Connect Kali Peer

On Kali, run:

```bash
python3 kali_peer.py 192.168.29.58
```

Replace `192.168.29.58` with your actual Windows laptop IP.

You should see:
```
[Kali Peer] Node: kali-kali
[Kali Peer] Connecting to CyberShield at ws://192.168.29.58:8765
[Kali Peer] ✓ Connected to 192.168.29.58:8765
  → sent: CPU=12.3%  MEM=45.2%  PROCS=156
```

## Step 6: View in Dashboard

Open the dashboard on Windows:
```powershell
cybershield dashboard --no-browser
```

Navigate to `http://localhost:7000?key=<your-key>`

You'll see:
- **SAMRAT** (green circle, top center) — your Windows laptop
- **kali-kali** (amber circle, bottom left) — your Kali VM with REAL metrics
- **node-mock** (gray circle, bottom right) — mock node for scale

The amber line between SAMRAT and Kali is a **real WebSocket connection**.

## Step 7: Launch Attack from Kali

On Kali, while kali_peer.py is still running, open another terminal:

```bash
# CPU stress
stress --cpu 4 --timeout 30 &

# Network scan
sudo nmap -sV -T4 192.168.29.58 &

# Network flood
sudo hping3 --flood -p 80 192.168.29.58 &
```

Watch the dashboard:
- SAMRAT node turns **red** (compromised)
- Edges show **SEVERED** labels
- Kali node stays **amber** (online, peer continues)
- Full intrusion alert with payload analysis

## Troubleshooting

### Connection refused
- Check Windows firewall allows port 8765
- Verify `cybershield network listen` is running
- Ping Windows laptop from Kali: `ping 192.168.29.58`

### Kali not showing in dashboard
- Check `logs/peers.json` exists on Windows
- Refresh dashboard (F5)
- Check P2P listener terminal for "Peer registered" message

### Attack not detected
- Ensure `cybershield node monitor --p2p` is running
- Check baseline is calibrated: `cybershield setup`
- Verify observation window (needs 15-20 seconds)

## Complete Demo Terminal Layout

**Terminal 1 (Windows)** — Primary node monitor:
```powershell
cybershield node monitor --p2p
```

**Terminal 2 (Windows)** — Dashboard:
```powershell
cybershield dashboard --no-browser
```

**Terminal 3 (Windows)** — P2P listener:
```powershell
cybershield network listen
```

**Terminal 4 (Kali)** — Peer node:
```bash
python3 kali_peer.py 192.168.29.58
```

**Terminal 5 (Kali)** — Attack launcher:
```bash
stress --cpu 4 --timeout 30 &
sudo nmap -sV -T4 192.168.29.58 &
```

## What Makes This Real

- **Real WebSocket connection** between Windows and Kali
- **Real metrics** from Kali (actual CPU, MEM, PROCS)
- **Real attack traffic** from Kali to Windows
- **Real detection** on Windows with ML ensemble
- **Real blockchain logging** with Aptos
- **Real IPFS storage** with Pinata
- **Real ZK proofs** with docker-snarkjs

The dashboard shows a **verifiable, live P2P network** with real nodes, real connections, and real threat detection.
