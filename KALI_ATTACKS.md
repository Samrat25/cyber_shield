# Kali Linux Attack Guide for CyberShield Demo

## Setup

1. **Connect Kali to same WiFi as Windows laptop**
2. **Find IPs:**
   - Windows: `ipconfig` → e.g., 192.168.29.58
   - Kali: `ip addr show` → e.g., 192.168.29.XX

3. **Test connectivity:**
```bash
ping 192.168.29.58
```

---

## Attack Scenarios for Demo

### 1. CPU Exhaustion Attack (Recommended for Quick Demo)

**On Kali:**
```bash
# Install stress if not present
sudo apt-get install stress

# Launch CPU attack (30 seconds)
stress --cpu 4 --timeout 30
```

**Expected Detection:**
- Time to detect: 15-20 seconds
- Attack Type: "CPU Exhaustion / DoS Attack"
- Severity: CRITICAL
- Deviation: +4-5σ on CPU

---

### 2. Port Scan (Reconnaissance)

**On Kali:**
```bash
# Service version scan
sudo nmap -sV -T4 192.168.29.58

# Aggressive scan
sudo nmap -A 192.168.29.58

# Full port scan
sudo nmap -p- 192.168.29.58
```

**Expected Detection:**
- Time to detect: 10-15 seconds
- Attack Type: "Port Scan / Reconnaissance"
- Severity: MEDIUM
- Deviation: High packet count, low bytes

---

### 3. Network Flood (DDoS Simulation)

**On Kali:**
```bash
# Install hping3 if not present
sudo apt-get install hping3

# SYN flood
sudo hping3 --flood -S -p 80 192.168.29.58

# UDP flood
sudo hping3 --flood --udp -p 53 192.168.29.58

# ICMP flood
sudo hping3 --flood --icmp 192.168.29.58
```

**Expected Detection:**
- Time to detect: 5-10 seconds
- Attack Type: "Network Flood / DDoS"
- Severity: HIGH
- Deviation: +10-20σ on network bytes/packets

**Stop attack:** Press Ctrl+C

---

### 4. Combined APT (Advanced Persistent Threat)

**On Kali:**
```bash
# Run multiple attacks simultaneously
sudo nmap -sV 192.168.29.58 &
stress --cpu 2 --timeout 30 &
sudo hping3 --flood -p 80 192.168.29.58
```

**Expected Detection:**
- Time to detect: 10-15 seconds
- Attack Type: "Combined APT — Multiple Vectors"
- Severity: CRITICAL
- Deviation: Multiple metrics spiking

---

## Demo Flow with Kali

### Setup (Before Demo)

**Terminal 1 (Windows):**
```powershell
cybershield node monitor
```

**Terminal 2 (Windows):**
```powershell
cybershield dashboard --no-browser
```

**Terminal 3 (Windows):**
```powershell
cybershield network listen
```

**Terminal 4 (Kali):**
```bash
python3 kali_peer.py 192.168.29.58
```

### Demo Script

**1. Show Normal Operation (30 seconds)**
- Point to monitor showing "● SAFE"
- Point to dashboard showing green topology
- Explain personalized baseline

**2. Launch Attack from Kali (Terminal 5)**
```bash
# Quick CPU attack
stress --cpu 4 --timeout 30
```

**3. Show Detection (15-20 seconds)**
- Monitor shows ⚠ WARNING messages
- After 3 warnings → INTRUSION CONFIRMED
- Full payload analysis with sigma deviations
- IPFS Gateway URL
- Blockchain TX Hash

**4. Show Dashboard Updates**
- Refresh dashboard (F5)
- Node turns red (compromised)
- Kali peer stays amber (online)
- Edges show "SEVERED"
- Event log shows anomaly with IPFS/blockchain links

**5. Explain Distributed Resilience**
- "My laptop is compromised and quarantined"
- "But the Kali peer continues operating"
- "This demonstrates distributed resilience"
- "In a real network, other nodes would take over"

---

## Attack Comparison Table

| Attack Type | Command | Detection Time | Severity | Best For Demo |
|-------------|---------|----------------|----------|---------------|
| CPU Exhaustion | `stress --cpu 4 --timeout 30` | 15-20s | CRITICAL | ✅ Quick, reliable |
| Port Scan | `nmap -sV 192.168.29.58` | 10-15s | MEDIUM | Good for recon demo |
| Network Flood | `hping3 --flood -p 80 192.168.29.58` | 5-10s | HIGH | Very dramatic |
| Combined APT | Multiple commands | 10-15s | CRITICAL | Most impressive |

---

## Troubleshooting

### Attack not detected?
- Check monitor is running BEFORE launching attack
- Wait full 20 seconds for observation window
- Verify Kali can reach Windows: `ping 192.168.29.58`

### Kali peer not showing in dashboard?
- Check `cybershield network listen` is running
- Verify `logs/peers.json` exists
- Check Kali peer script is connected

### Dashboard not updating?
- Refresh browser (F5)
- Check `logs/node_state.json` has `status: "COMPROMISED"`

---

## Safety Notes

⚠️ **Only use these attacks:**
- On your own machines
- On isolated test networks
- With permission from network owner

❌ **Never use these attacks:**
- On production networks
- On networks you don't own
- Without explicit permission

---

## Quick Reference

**Start monitoring:**
```powershell
cybershield node monitor
```

**Launch quick attack from Kali:**
```bash
stress --cpu 4 --timeout 30
```

**Reset after demo:**
```powershell
python reset_node_status.py
```

**Total demo time:** 3-5 minutes
