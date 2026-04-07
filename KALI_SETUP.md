# Kali VM Setup - Real P2P Node

## Overview
This guide shows how to connect your Kali VM as a real peer node in the CyberShield network.

## Prerequisites
- Kali VM running on same WiFi as your Windows laptop
- Python 3 installed on Kali (pre-installed)
- Your Windows laptop IP: `192.168.29.58`

## Step 1: Find Kali's IP Address

On Kali terminal:
```bash
ip addr show | grep "inet " | grep -v 127
```

You'll see something like:
```
inet 192.168.29.XX/24 brd 192.168.29.255 scope global dynamic eth0
```

Note the IP (e.g., `192.168.29.105`)

## Step 2: Create kali_peer.py

On Kali, create this file:

```bash
nano ~/kali_peer.py
```

Paste this code:

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

Save and exit (Ctrl+X, Y, Enter)

## Step 3: Install Dependencies

```bash
pip3 install websockets psutil
```

## Step 4: Make Executable

```bash
chmod +x ~/kali_peer.py
```

## Step 5: Run the Peer

```bash
python3 ~/kali_peer.py 192.168.29.58
```

You should see:
```
[Kali Peer] Node: kali-kali
[Kali Peer] Connecting to CyberShield at ws://192.168.29.58:8765
[Kali Peer] Sending heartbeats every 5s. Ctrl+C to stop.

[Kali Peer] ✓ Connected to 192.168.29.58:8765
  → sent: CPU=5.2%  MEM=45.3%  PROCS=156
  → sent: CPU=3.8%  MEM=45.5%  PROCS=157
```

## Step 6: Launch Attack (After Connection)

In a separate Kali terminal:

```bash
# CPU stress
stress --cpu 4 --timeout 30

# Network scan
sudo nmap -sV -T4 192.168.29.58

# Network flood
sudo hping3 --flood -p 80 192.168.29.58
```

## Troubleshooting

### "Connection refused"
- Make sure Windows laptop is running: `cybershield network listen`
- Check Windows firewall allows port 8765

### "Cannot connect"
- Verify both machines on same WiFi
- Ping from Kali: `ping 192.168.29.58`
- Check IP is correct

### "Module not found"
```bash
pip3 install --upgrade websockets psutil
```

## What You'll See

### On Kali:
```
[Kali Peer] ✓ Connected to 192.168.29.58:8765
  → sent: CPU=5.2%  MEM=45.3%  PROCS=156
  → sent: CPU=3.8%  MEM=45.5%  PROCS=157
```

### On Windows Dashboard:
- Kali node appears as amber circle (bottom left)
- Shows real-time CPU/MEM from Kali
- "Kali Linux" label below node
- Amber line connecting to SAMRAT node

### When Attack Launched:
- SAMRAT node turns red (compromised)
- Edges show "SEVERED" label
- Kali node stays amber (online)
- Status bar shows "Primary node COMPROMISED"

## Demo Flow

1. **Terminal 1 (Windows)**: `cybershield node monitor`
2. **Terminal 2 (Windows)**: `cybershield network listen`
3. **Terminal 3 (Windows)**: `cybershield dashboard`
4. **Terminal 4 (Kali)**: `python3 kali_peer.py 192.168.29.58`
5. **Terminal 5 (Kali)**: Launch attack commands

## Network Topology

```
Windows Laptop (192.168.29.58:8765)
    ↑
    | WebSocket
    | (amber line in dashboard)
    ↓
Kali VM (192.168.29.XX)
    ↓
    | Attack traffic
    ↓
Windows Laptop (target)
```

## Key Points for Judges

1. **Real Connection**: The amber line is a live WebSocket connection
2. **Real Metrics**: CPU/MEM shown are Kali's actual values
3. **Real Attack**: nmap/hping3 running on Kali, targeting Windows
4. **Real Detection**: Windows detects the attack, quarantines itself
5. **Real Isolation**: Kali node continues operating (peer resilience)

## Stop Everything

- Kali peer: `Ctrl+C` in Terminal 4
- Windows monitor: `Ctrl+C` in Terminal 1
- Windows P2P: `Ctrl+C` in Terminal 2
- Dashboard: `Ctrl+C` in Terminal 3
