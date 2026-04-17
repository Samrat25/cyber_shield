# Network Setup & Attack Testing Guide

Complete manual guide for setting up P2P network and testing attack detection.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Network Setup](#network-setup)
- [Kali Peer Connection](#kali-peer-connection)
- [Attack Testing](#attack-testing)
- [Dashboard Verification](#dashboard-verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Windows Machine
- CyberShield installed and configured
- Virtual environment activated
- Node initialized and registered
- Firewall configured to allow port 8765

### Kali Linux Machine
- Python 3.8+ installed
- `psutil` and `websockets` packages
- Network connectivity to Windows machine
- `stress-ng` installed for attacks

### Network Requirements
- Both machines on same network (or accessible via internet)
- Windows firewall allows incoming connections on port 8765
- Know Windows machine's IP address

---

## Network Setup

### Step 1: Get Windows IP Address

```bash
# Windows Command Prompt or PowerShell
ipconfig
```

Look for **IPv4 Address** under your active network adapter:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 10.69.115.68
```

**Note this IP address** - you'll need it for Kali connection.

### Step 2: Configure Windows Firewall

```bash
# Windows PowerShell (Run as Administrator)
netsh advfirewall firewall add rule name="CyberShield P2P" dir=in action=allow protocol=TCP localport=8765
```

**Verify rule added:**
```bash
netsh advfirewall firewall show rule name="CyberShield P2P"
```

### Step 3: Start Windows P2P Server

```bash
# Windows Terminal 1
cd C:\Users\Samrat\OneDrive\Desktop\cyber_shield
.\venv\Scripts\activate
cybershield network listen --port 8765
```

**Expected output:**
```
╭──────────────────────────────────────────────╮
│ P2P Network Server — Real WebSocket Listener │
╰──────────────────────────────────────────────╯

✓ Server starting on port 8765
Waiting for peer connections...
✓ WebSocket server listening on 0.0.0.0:8765
```

**Keep this terminal running!**

### Step 4: Start Windows Monitoring

```bash
# Windows Terminal 2 (NEW TERMINAL)
cd C:\Users\Samrat\OneDrive\Desktop\cyber_shield
.\venv\Scripts\activate
cybershield node monitor
```

**Expected output:**
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
```

**Keep this terminal running!**

### Step 5: Start Windows Dashboard

```bash
# Windows Terminal 3 (NEW TERMINAL)
cd C:\Users\Samrat\OneDrive\Desktop\cyber_shield
.\venv\Scripts\activate
cybershield dashboard
```

**Expected output:**
```
╭───────────────────────────────────────╮
│ CyberShield Dashboard                 │
╰───────────────────────────────────────╯

✓ Dashboard running on http://localhost:5000
✓ Session key: abc123def456

Open this URL in your browser:
  http://localhost:5000?key=abc123def456
```

**Open the URL in your browser!**

---

## Kali Peer Connection

### Step 1: Install Dependencies on Kali

```bash
# Kali terminal
sudo apt update
sudo apt install python3-pip stress-ng -y

# Install Python packages
pip3 install psutil websockets
```

### Step 2: Copy Kali Peer Script

Transfer `kali_peer.py` from Windows to Kali:

**Option A: Using SCP (if SSH enabled)**
```bash
# From Kali
scp user@<WINDOWS_IP>:C:/Users/Samrat/OneDrive/Desktop/cyber_shield/kali_peer.py ~/
```

**Option B: Manual Copy**
1. Open `kali_peer.py` on Windows
2. Copy content
3. Create file on Kali: `nano ~/kali_peer.py`
4. Paste content
5. Save (Ctrl+X, Y, Enter)
6. Make executable: `chmod +x ~/kali_peer.py`

### Step 3: Connect Kali to Windows

```bash
# Kali terminal
cd ~
python3 kali_peer.py --server <WINDOWS_IP>:8765
```

**Replace `<WINDOWS_IP>`** with your Windows IP from Step 1.

**Example:**
```bash
python3 kali_peer.py --server 10.69.115.68:8765
```

**Expected output:**
```
============================================================
CyberShield Kali Peer Node
============================================================

Node ID: kali-kali
Local IP: 192.168.1.50
Server: 10.69.115.68:8765

Connecting...

✓ Connected to CyberShield server
✓ Registration confirmed
  Connected to CyberShield node SAMRAT
  Total peers: 1

Sending metrics every 5 seconds...
Press Ctrl+C to disconnect

[001] Sent: CPU=5.2%  MEM=42.3%  PROCS=156
[002] Sent: CPU=3.1%  MEM=42.4%  PROCS=157
[003] Sent: CPU=4.7%  MEM=42.5%  PROCS=158
```

**On Windows Terminal 1 (P2P Server), you should see:**
```
✓ Peer registered: kali-kali (192.168.1.50)
← kali-kali: CPU=5.2%  MEM=42.3%
← kali-kali: CPU=3.1%  MEM=42.4%
← kali-kali: CPU=4.7%  MEM=42.5%
```

**Keep Kali peer running!**

### Step 4: Verify Dashboard Shows Peer

1. Go to Windows browser with dashboard open
2. Scroll to **"🌐 P2P Network Topology"** section
3. You should see:
   - **SAMRAT** node in center (green, PRIMARY)
   - **kali-kali** node connected (amber, PEER)
   - Connection line between them (amber = real connection)
   - Live CPU/MEM metrics under kali-kali node
   - "Kali Linux" label under the node

**If not visible:**
- Wait 5 seconds (dashboard polls every 5s)
- Hard refresh browser (Ctrl+Shift+R)
- Check `C:\Users\<USERNAME>\.cybershield\logs\peers.json` exists

---

## Attack Testing

### Test 1: Windows CPU Attack

This tests detection on the Windows machine itself.

**Step 1: Run Attack Script**

```bash
# Windows Terminal 4 (NEW TERMINAL)
cd C:\Users\Samrat\OneDrive\Desktop\cyber_shield
.\venv\Scripts\activate
python windows_cpu_attack.py
```

**Expected output:**
```
============================================================
CyberShield - Real CPU Attack Test
============================================================

This will spike CPU to trigger detection.
Watch the monitor terminal for intrusion alert.

Starting CPU attack:
  Duration: 45 seconds
  Cores: 8
  Expected detection: ~10-15 seconds (3/4 warnings)

  [+] Started burner 1/8
  [+] Started burner 2/8
  ...
  [+] Started burner 8/8

[*] Attack running... (Ctrl+C to stop early)
```

**Step 2: Watch Monitor Terminal (Terminal 2)**

You should see warnings appear:

```
16:47:15  ⚠ WARNING [1/4 readings]  CPU 100.0%  MEM  85.4%  Threat: CPU Exhaustion / DoS Attack  conf=0.85
16:47:20  ⚠ WARNING [2/4 readings]  CPU 100.0%  MEM  84.8%  Threat: CPU Exhaustion / DoS Attack  conf=0.85
16:47:25  ⚠ WARNING [3/4 readings]  CPU 100.0%  MEM  85.2%  Threat: CPU Exhaustion / DoS Attack  conf=0.85
```

**After 3rd warning (15 seconds), intrusion alert fires:**

```
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
│   ────────────────────────────────────────────────────                 │
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

**Step 3: Verify on Dashboard**

1. Go to dashboard in browser
2. **Network Topology**: SAMRAT node should turn RED with "COMPROMISED" badge
3. **Metrics Chart**: CPU line should spike to 100%, Anomaly Risk line should turn red and spike to 80-100%
4. **Event Log**: New anomaly event should appear with IPFS CID and TX hash links

**Step 4: Click IPFS Gateway Link**

Click the IPFS Gateway URL in the monitor output or dashboard event log. You should see the evidence JSON:

```json
{
  "type": "threat_detected",
  "node_id": "SAMRAT",
  "metrics": { ... },
  "verdict": "anomaly",
  "confidence": 0.85,
  "threat_info": { ... },
  "zk_proof": { ... }
}
```

**Step 5: Click Blockchain Explorer Link**

Click the Aptos TX hash link. You should see the transaction on Aptos testnet explorer.

---

### Test 2: Kali CPU Attack

This tests detection of attacks from Kali machine (metrics visible on dashboard).

**Step 1: Run Attack on Kali**

```bash
# Kali terminal (NEW TERMINAL - keep peer running in other terminal)
stress-ng --cpu 4 --timeout 45s
```

**Expected output:**
```
stress-ng: info:  [12345] dispatching hogs: 4 cpu
stress-ng: info:  [12345] successful run completed in 45.00s
```

**Step 2: Watch Dashboard**

1. Go to dashboard in browser
2. **Network Topology**: Watch kali-kali node's CPU metric spike to 100%
3. **Metrics Chart**: Won't show Kali's CPU (only shows Windows metrics)
4. Kali node stays green (attack is on Kali, not Windows)

**Note:** This demonstrates P2P network showing peer metrics in real-time. The Windows node is not under attack, so no intrusion alert fires on Windows.

---

### Test 3: Network Attack from Kali to Windows

This tests network-based attacks (less reliable for detection).

**Step 1: Install hping3 on Kali**

```bash
# Kali terminal
sudo apt install hping3 -y
```

**Step 2: Run SYN Flood Attack**

```bash
# Kali terminal
# Replace <WINDOWS_IP> with your Windows IP
sudo hping3 -S -p 80 --flood <WINDOWS_IP>
```

**Example:**
```bash
sudo hping3 -S -p 80 --flood 10.69.115.68
```

**Step 3: Watch Monitor**

Network attacks may not spike CPU enough to trigger detection. This is expected - the system focuses on CPU/MEM/DISK metrics which are more reliable.

**Step 4: Stop Attack**

Press `Ctrl+C` to stop hping3.

---

## Dashboard Verification

### Network Topology Section

**What to look for:**

1. **Nodes:**
   - SAMRAT (center, green/red, PRIMARY badge)
   - kali-kali (connected, amber, PEER badge, "Kali Linux" label)
   - node-mock (gray, MOCK badge) - for visual scale

2. **Connections:**
   - Amber lines = real connections
   - Gray lines = mock connections
   - Red dashed lines = severed (when compromised)

3. **Metrics:**
   - Live CPU/MEM under each real node
   - Updates every 5 seconds

4. **Status Bar:**
   - "● All nodes online" (normal)
   - "⚠ Primary node COMPROMISED" (after attack)
   - Peer count: "(1 real peer connected)"

### Metrics Chart

**What to look for:**

1. **CPU % (blue line):**
   - Normal: 20-50%
   - Attack: 100%

2. **Memory % (purple line):**
   - Normal: 85-95% (your baseline)
   - Attack: May drop slightly

3. **Anomaly Risk % (orange/red line):**
   - Normal: 0-40% (green)
   - Warning: 40-60% (orange)
   - Attack: 60-100% (red)

4. **Time Labels:**
   - X-axis shows HH:MM:SS
   - Last 30 readings displayed

### Event Log

**What to look for:**

1. **Safe Events (green):**
   - "✓ SAFE" badge
   - CPU, Memory, ML Score
   - No IPFS/blockchain links

2. **Anomaly Events (red):**
   - "⚠️ ANOMALY" badge
   - Metrics at time of detection
   - IPFS CID with "View on Gateway" link
   - Aptos TX with "View on Explorer" link

3. **Sorting:**
   - Newest events at top
   - Scroll down for history

### Statistics Cards

**What to look for:**

1. **Total Checks:**
   - Increments every 5 seconds
   - Shows monitoring is active

2. **Threats Detected:**
   - Increments when attack detected
   - Should be 0 normally

3. **Safe Rate:**
   - Should be 100% normally
   - Drops when threats detected

4. **Active Nodes:**
   - Shows number of nodes in topology
   - Should be 2-3 (SAMRAT + kali-kali + mock)

---

## Troubleshooting

### Kali Can't Connect to Windows

**Problem:** Connection refused or timeout

**Solutions:**

1. **Verify Windows IP:**
   ```bash
   # Windows
   ipconfig
   ```

2. **Check firewall rule:**
   ```bash
   # Windows (as Administrator)
   netsh advfirewall firewall show rule name="CyberShield P2P"
   ```

3. **Test connectivity:**
   ```bash
   # Kali
   ping <WINDOWS_IP>
   telnet <WINDOWS_IP> 8765
   ```

4. **Verify P2P server running:**
   - Check Windows Terminal 1
   - Should show "WebSocket server listening"

5. **Try disabling Windows firewall temporarily:**
   ```bash
   # Windows (as Administrator) - TEMPORARY ONLY
   netsh advfirewall set allprofiles state off
   # Remember to turn back on after testing!
   netsh advfirewall set allprofiles state on
   ```

### Dashboard Not Showing Peer

**Problem:** Topology shows only SAMRAT and mock node

**Solutions:**

1. **Check peers.json file:**
   ```bash
   # Windows
   type C:\Users\<USERNAME>\.cybershield\logs\peers.json
   ```
   Should contain kali-kali entry.

2. **Verify Kali peer connected:**
   - Check Windows Terminal 1 (P2P server)
   - Should show "✓ Peer registered: kali-kali"

3. **Hard refresh dashboard:**
   - Press Ctrl+Shift+R or Ctrl+F5
   - Wait 5 seconds for next poll

4. **Restart dashboard:**
   ```bash
   # Windows Terminal 3
   # Press Ctrl+C to stop
   cybershield dashboard
   ```

5. **Reconnect Kali peer:**
   ```bash
   # Kali - stop with Ctrl+C, then:
   python3 kali_peer.py --server <WINDOWS_IP>:8765
   ```

### Attack Not Detected

**Problem:** CPU at 100% but showing SAFE

**Solutions:**

1. **Wait for observation window:**
   - Need 3 warnings (15 seconds minimum)
   - Attack must run for 45 seconds

2. **Check attack is running:**
   ```bash
   # Windows - check CPU in Task Manager
   # Should be 100%
   ```

3. **Verify monitor is running:**
   - Check Windows Terminal 2
   - Should show live metrics

4. **Check baseline:**
   ```bash
   # Windows
   type C:\Users\<USERNAME>\.cybershield\logs\baseline.json
   ```
   If CPU baseline is very high, detection may be delayed.

5. **Run attack longer:**
   ```bash
   # Windows
   python windows_cpu_attack.py 60  # 60 seconds
   ```

### Port Already in Use

**Problem:** "Port 8765 already in use"

**Solutions:**

1. **Find process using port:**
   ```bash
   # Windows
   netstat -ano | findstr :8765
   ```

2. **Kill process:**
   ```bash
   # Windows (replace PID with actual process ID)
   taskkill /PID <PID> /F
   ```

3. **Use different port:**
   ```bash
   # Windows
   cybershield network listen --port 8766
   
   # Kali
   python3 kali_peer.py --server <WINDOWS_IP>:8766
   ```

### Dashboard Shows Offline CID

**Problem:** IPFS CID starts with "QmOFFLINE"

**Cause:** No internet connection or Pinata API error

**Solutions:**

1. **Check internet:**
   ```bash
   # Windows
   ping 8.8.8.8
   ```

2. **Verify Pinata JWT:**
   - Check `.env` file
   - Ensure `PINATA_JWT` is set correctly

3. **Test Pinata API:**
   ```bash
   # Windows
   curl -H "Authorization: Bearer YOUR_JWT" https://api.pinata.cloud/data/testAuthentication
   ```

4. **Continue without IPFS:**
   - System works offline
   - Evidence logged locally
   - Will sync when connection restored

---

## Best Practices

1. **Always run P2P server first** before connecting peers
2. **Keep all terminals open** during testing
3. **Wait 15 seconds** for attack detection (observation window)
4. **Run attacks for 45+ seconds** to ensure detection
5. **Check dashboard every 5 seconds** for updates
6. **Save IPFS CID and TX hash** for verification
7. **Stop attacks gracefully** with Ctrl+C
8. **Restart monitor after attack** to reset state

---

## Quick Reference

### Windows Setup (3 Terminals)

```bash
# Terminal 1: P2P Server
cybershield network listen --port 8765

# Terminal 2: Monitoring
cybershield node monitor

# Terminal 3: Dashboard
cybershield dashboard
```

### Kali Setup (2 Terminals)

```bash
# Terminal 1: Peer Connection
python3 kali_peer.py --server <WINDOWS_IP>:8765

# Terminal 2: Attacks
stress-ng --cpu 4 --timeout 45s
```

### Attack Commands

```bash
# Windows CPU attack
python windows_cpu_attack.py

# Kali CPU attack
stress-ng --cpu 4 --timeout 45s

# Kali network attack (less effective)
sudo hping3 -S -p 80 --flood <WINDOWS_IP>
```

### Verification URLs

```
# Dashboard
http://localhost:5000?key=<SESSION_KEY>

# IPFS Gateway
https://gateway.pinata.cloud/ipfs/<CID>

# Aptos Explorer
https://explorer.aptoslabs.com/txn/<TX_HASH>?network=testnet
```

---

**Version**: 1.0.0  
**Last Updated**: April 2026
