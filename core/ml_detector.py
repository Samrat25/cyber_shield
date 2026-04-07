# core/ml_detector.py
"""
ML detection layer.
Priority order:
  1. Random Forest (cybershield/ml/model/) — if sklearn version matches
  2. Rate-based spike detector             — always works, no version issues
  3. Isolation Forest (ml/)               — calibrated baseline
"""

import numpy as np
import os, json, time, warnings
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent
RF_MODEL_PATH = BASE_DIR / "cybershield" / "ml" / "model" / "model_rf.pkl"
RF_SCAL_PATH  = BASE_DIR / "cybershield" / "ml" / "model" / "scaler_rf.pkl"
IF_MODEL_PATH = BASE_DIR / "ml" / "model_if.pkl"
BASELINE_PATH = BASE_DIR / "logs" / "baseline.json"
(BASE_DIR / "ml").mkdir(exist_ok=True)

# ── Threat catalogue ──────────────────────────────────────────────────────────
THREAT_CATALOGUE = {
    "port_scan"    : "Port Scan / Reconnaissance (nmap -sV)",
    "dos_cpu"      : "CPU Exhaustion / Denial-of-Service (stress)",
    "net_flood"    : "Network Flood / DDoS (hping3 --flood)",
    "mem_attack"   : "Memory Exhaustion / Ransomware Prep",
    "fork_bomb"    : "Fork Bomb / Malware Process Spawning",
    "disk_attack"  : "Disk Exhaustion / Ransomware I/O",
    "combined_apt" : "Combined APT — Multiple Attack Vectors",
    "cpu_spike"    : "Sudden CPU Spike (unclassified)",
    "unknown"      : "Unknown Anomalous Behaviour",
}

# ── Baseline load/save ────────────────────────────────────────────────────────
def load_baseline() -> dict:
    if BASELINE_PATH.exists():
        with open(BASELINE_PATH) as f:
            return json.load(f)
    # Safe defaults — low RAM Windows machine
    return {
        "cpu_mean": 25.0, "cpu_std": 12.0,
        "mem_mean": 90.0, "mem_std":  5.0,   # high for Windows
        "prc_mean": 180.0,"prc_std": 30.0,
        "pkt_mean": 500.0,"pkt_std": 300.0,
        "byt_mean": 100000.0, "byt_std": 80000.0,
        "disk_mean": 70.0, "disk_std": 10.0,
        "conn_mean": 100.0, "conn_std": 50.0,
    }

def save_baseline(b: dict):
    with open(BASELINE_PATH, "w") as f:
        json.dump(b, f, indent=2)

# ── Calibration ───────────────────────────────────────────────────────────────
def calibrate(samples: int = 20, interval: float = 1.5) -> dict:
    import psutil, time
    print(f"[Calibrate] {samples} samples x {interval}s — keep system idle")
    readings = []
    for i in range(samples):
        net   = psutil.net_io_counters()
        disk  = psutil.disk_usage("C:\\" if os.name == "nt" else "/")
        readings.append({
            "cpu"  : psutil.cpu_percent(interval=0.3),
            "mem"  : psutil.virtual_memory().percent,
            "procs": len(psutil.pids()),
            "pkts" : net.packets_recv,
            "byts" : net.bytes_recv,
            "disk" : disk.percent,
            "conn" : 0,  # skip net_connections on Windows — hangs
        })
        print(f"  [{i+1:02d}/{samples}] CPU={readings[-1]['cpu']:.1f}%  MEM={readings[-1]['mem']:.1f}%")
        time.sleep(interval)

    def st(key):
        vals = [r[key] for r in readings]
        return float(np.mean(vals)), max(float(np.std(vals)), 1.0)

    c_m, c_s = st("cpu");  m_m, m_s = st("mem");  p_m, p_s = st("procs")
    pk_m,pk_s= st("pkts"); b_m, b_s = st("byts");  d_m, d_s = st("disk")

    baseline = {
        "cpu_mean":  c_m,  "cpu_std":  max(c_s, 5.0),
        "mem_mean":  m_m,  "mem_std":  max(m_s, 3.0),
        "prc_mean":  p_m,  "prc_std":  max(p_s, 10.0),
        "pkt_mean":  pk_m, "pkt_std":  max(pk_s, 200.0),
        "byt_mean":  b_m,  "byt_std":  max(b_s, 50000.0),
        "disk_mean": d_m,  "disk_std": max(d_s, 5.0),
        "conn_mean": 100.0,"conn_std": 50.0,
    }
    save_baseline(baseline)
    print(f"\n[Calibrate] Done. CPU_normal={c_m:.1f}%  MEM_normal={m_m:.1f}%")
    return baseline

# ── Threat classifier ─────────────────────────────────────────────────────────
def classify_threat(data: dict, baseline: dict) -> dict:
    """
    Computes z-scores per metric vs your personal baseline.
    Names the attack type and builds full payload analysis.
    Works independently of any ML model — pure math.
    """
    def z(val, mean, std):
        return (float(val) - float(mean)) / max(float(std), 0.1)

    cpu   = float(data.get("cpu_percent",       0))
    mem   = float(data.get("memory_percent",    0))
    procs = float(data.get("process_count",     0))
    pkts  = float(data.get("net_packets_recv",  0))
    byts  = float(data.get("net_bytes_recv",    0))
    disk  = float(data.get("disk_percent",      0))
    conn  = float(data.get("net_connections",   0))

    cpu_z  = z(cpu,   baseline["cpu_mean"],  baseline["cpu_std"])
    mem_z  = z(mem,   baseline["mem_mean"],  baseline["mem_std"])
    prc_z  = z(procs, baseline["prc_mean"],  baseline["prc_std"])
    pkt_z  = z(pkts,  baseline["pkt_mean"],  baseline["pkt_std"])
    byt_z  = z(byts,  baseline["byt_mean"],  baseline["byt_std"])
    dsk_z  = z(disk,  baseline.get("disk_mean", 70), baseline.get("disk_std", 10))
    con_z  = z(conn,  baseline.get("conn_mean",100), baseline.get("conn_std",  50))

    # Classification (order = most specific first)
    if cpu_z > 3 and pkt_z > 3 and prc_z > 3:
        threat = "combined_apt"
    elif pkt_z > 4 and byt_z < 1.5:
        threat = "port_scan"       # many small packets = nmap
    elif byt_z > 4 and pkt_z > 3:
        threat = "net_flood"       # high bytes + packets = hping3
    elif cpu_z > 4:
        threat = "dos_cpu"
    elif mem_z > 4:
        threat = "mem_attack"
    elif prc_z > 5:
        threat = "fork_bomb"
    elif dsk_z > 4:
        threat = "disk_attack"
    elif pkt_z > 3 or con_z > 4:
        threat = "port_scan"
    elif cpu_z > 2.5:
        threat = "cpu_spike"
    else:
        threat = "unknown"

    max_z = max(abs(cpu_z), abs(mem_z), abs(prc_z),
                abs(pkt_z), abs(byt_z), abs(dsk_z))

    if   max_z > 7: severity = "CRITICAL"
    elif max_z > 5: severity = "HIGH"
    elif max_z > 3: severity = "MEDIUM"
    else:           severity = "LOW"

    return {
        "threat_type"  : threat,
        "threat_label" : THREAT_CATALOGUE.get(threat, "Unknown"),
        "severity"     : severity,
        "payload": {
            "cpu_actual"    : round(cpu, 1),
            "cpu_baseline"  : round(baseline["cpu_mean"], 1),
            "cpu_sigma"     : f"{cpu_z:+.2f}\u03c3",
            "mem_actual"    : round(mem, 1),
            "mem_baseline"  : round(baseline["mem_mean"], 1),
            "mem_sigma"     : f"{mem_z:+.2f}\u03c3",
            "procs_actual"  : int(procs),
            "procs_baseline": int(baseline["prc_mean"]),
            "procs_sigma"   : f"{prc_z:+.2f}\u03c3",
            "pkt_sigma"     : f"{pkt_z:+.2f}\u03c3",
            "byt_sigma"     : f"{byt_z:+.2f}\u03c3",
            "disk_sigma"    : f"{dsk_z:+.2f}\u03c3",
            "conn_sigma"    : f"{con_z:+.2f}\u03c3",
            "max_deviation" : f"{max_z:.2f}\u03c3",
        },
        "deviations": {
            "cpu": round(cpu_z,2), "mem": round(mem_z,2),
            "procs": round(prc_z,2), "pkts": round(pkt_z,2),
            "bytes": round(byt_z,2), "disk": round(dsk_z,2),
        }
    }

# ── Rate-based spike detector (primary fallback, always reliable) ─────────────
class RateDetector:
    """
    Detects threats by watching for SPIKES above YOUR personal baseline.
    No sklearn, no version issues, no model files needed.

    Logic:
      - Each metric has a rolling window of last N readings
      - If current reading > mean + K*std -> spike detected
      - Multiple spikes at once -> anomaly
    """
    def __init__(self):
        self.history   = []   # list of metric dicts
        self.window    = 10   # keep last 10 readings
        self.spike_k   = 3.0  # 3 standard deviations = spike
        self.min_reads = 3    # need at least 3 readings before trusting

    def add(self, metrics: dict):
        self.history.append(metrics)
        if len(self.history) > self.window:
            self.history.pop(0)

    def _spike(self, key: str, current: float) -> float:
        """Returns z-score of current vs recent history. High = spike."""
        vals = [float(h.get(key, 0)) for h in self.history[:-1]]  # exclude current
        if len(vals) < self.min_reads:
            return 0.0
        mean = np.mean(vals)
        std  = max(np.std(vals), 1.0)
        return (current - mean) / std

    def detect(self, metrics: dict, baseline: dict) -> tuple:
        """
        Returns (verdict, score, threat_info).
        score: 0.0 = normal, positive = anomaly severity
        """
        self.add(metrics)

        cpu  = float(metrics.get("cpu_percent",      0))
        mem  = float(metrics.get("memory_percent",   0))
        pkts = float(metrics.get("net_packets_recv", 0))
        byts = float(metrics.get("net_bytes_recv",   0))
        prc  = float(metrics.get("process_count",    0))
        disk = float(metrics.get("disk_percent",     0))

        # Two-layer detection:
        # Layer 1: spike vs recent history (catches sudden attacks)
        cpu_spike  = self._spike("cpu_percent",      cpu)
        pkt_spike  = self._spike("net_packets_recv", pkts)
        byt_spike  = self._spike("net_bytes_recv",   byts)
        prc_spike  = self._spike("process_count",    prc)
        dsk_spike  = self._spike("disk_percent",     disk)

        # Layer 2: absolute threshold vs calibrated baseline
        cpu_thresh = (cpu  - baseline["cpu_mean"])  / max(baseline["cpu_std"],  1)
        pkt_thresh = (pkts - baseline["pkt_mean"])  / max(baseline["pkt_std"],  1)
        byt_thresh = (byts - baseline["byt_mean"])  / max(baseline["byt_std"],  1)
        prc_thresh = (prc  - baseline["prc_mean"])  / max(baseline["prc_std"],  1)

        # Score = max of (recent spike OR absolute threshold)
        cpu_score = max(cpu_spike,  cpu_thresh)
        pkt_score = max(pkt_spike,  pkt_thresh)
        byt_score = max(byt_spike,  byt_thresh)
        prc_score = max(prc_spike,  prc_thresh)
        dsk_score = max(dsk_spike,  0)

        max_score = max(cpu_score, pkt_score, byt_score, prc_score, dsk_score)

        # Anomaly if ANY metric exceeds spike_k std devs
        if max_score >= self.spike_k:
            # Use negative score convention (matches Isolation Forest)
            ml_score = -round(max_score / 10.0, 4)
            return "anomaly", ml_score, classify_threat(metrics, baseline)

        # Report a meaningful positive score (how "normal" this is)
        ml_score = round(1.0 - max_score / self.spike_k, 4)
        return "safe", ml_score, {}

# Global rate detector instance (persists across calls in monitor loop)
_rate_detector = RateDetector()

# ── RF model loader (version-safe) ────────────────────────────────────────────
_rf_model   = None
_rf_scaler  = None
_rf_enabled = False

def _try_load_rf():
    global _rf_model, _rf_scaler, _rf_enabled
    if not (RF_MODEL_PATH.exists() and RF_SCAL_PATH.exists()):
        return False
    try:
        import joblib
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rf  = joblib.load(RF_MODEL_PATH)
            sc  = joblib.load(RF_SCAL_PATH)
        # Quick sanity check — predict one row
        dummy = np.zeros((1, rf.n_features_in_))
        rf.predict(dummy)
        rf.predict_proba(dummy)
        _rf_model  = rf
        _rf_scaler = sc
        _rf_enabled = True
        return True
    except Exception as e:
        _rf_enabled = False
        return False

_try_load_rf()   # attempt on module load (silent)

def _detect_rf(data: dict, baseline: dict) -> tuple:
    """
    Uses the CICIDS2017-trained Random Forest.
    Maps your 12 psutil features -> CICIDS feature space.
    Score convention: positive = safe, negative = anomaly.
    """
    pkts = float(data.get("net_packets_recv", 0))
    byts = float(data.get("net_bytes_recv",   0))
    psnt = float(data.get("net_packets_sent", 0))
    bsnt = float(data.get("net_bytes_sent",   0))
    cpu  = float(data.get("cpu_percent",      0))
    conn = float(data.get("net_connections",  0))

    # Map to 12-feature CICIDS-like vector
    row = np.array([[
        psnt,                    # Total Fwd Packets
        pkts,                    # Total Backward Packets
        bsnt,                    # Total Length of Fwd Packets
        byts,                    # Total Length of Bwd Packets
        byts / 5.0,              # Flow Bytes/s (5s window)
        pkts / 5.0,              # Flow Packets/s
        5_000_000.0,             # Flow Duration (5s in us)
        1500.0,                  # Fwd Packet Length Max (MTU)
        1500.0,                  # Bwd Packet Length Max
        100.0,                   # Flow IAT Mean (ms)
        pkts * 0.5,              # Fwd IAT Total
        cpu * 1000.0,            # Active Mean (proxy via CPU)
    ]])

    try:
        X_s   = _rf_scaler.transform(row)
        pred  = _rf_model.predict(X_s)[0]         # 0=normal, 1=attack
        proba = _rf_model.predict_proba(X_s)[0]   # [P(normal), P(attack)]

        attack_prob = float(proba[1])
        # Convert to our score convention: negative = anomaly
        ml_score = round(0.5 - attack_prob, 4)

        if pred == 1 and attack_prob > 0.6:
            return "anomaly", ml_score, classify_threat(data, baseline)
        return "safe", ml_score, {}
    except Exception as e:
        # RF failed mid-call — fall back to rate detector
        return _rate_detector.detect(data, baseline)

# ── Training (Isolation Forest fallback) ──────────────────────────────────────
def train() -> None:
    try:
        from sklearn.ensemble import IsolationForest
        import joblib
    except ImportError:
        print("[Train] sklearn not installed — skipping Isolation Forest training.")
        print("[Train] Rate-based detector works without sklearn — no action needed.")
        return

    b = load_baseline()
    np.random.seed(42)
    n = 2000
    X = np.column_stack([
        np.clip(np.random.normal(b["cpu_mean"],  b["cpu_std"],  n), 0, 100),
        np.clip(np.random.normal(b["mem_mean"],  b["mem_std"],  n), 0, 100),
        np.clip(np.random.normal(b["prc_mean"],  b["prc_std"],  n), 5, 1000),
        np.clip(np.random.normal(b["pkt_mean"],  b["pkt_std"],  n), 0, None),
        np.clip(np.random.normal(b["byt_mean"],  b["byt_std"],  n), 0, None),
        np.clip(np.random.normal(b.get("disk_mean",70), b.get("disk_std",10), n), 0, 100),
    ])
    m = IsolationForest(n_estimators=100, contamination=0.04, random_state=42)
    m.fit(X)
    joblib.dump(m, IF_MODEL_PATH)
    print(f"[Train] Isolation Forest saved -> {IF_MODEL_PATH}")

def _detect_if(data: dict, baseline: dict) -> tuple:
    """Isolation Forest detection as third-tier fallback."""
    import joblib
    if not IF_MODEL_PATH.exists():
        train()
    m = joblib.load(IF_MODEL_PATH)
    X = np.array([[
        data.get("cpu_percent",      0),
        data.get("memory_percent",   0),
        data.get("process_count",    0),
        data.get("net_packets_recv", 0),
        data.get("net_bytes_recv",   0),
        data.get("disk_percent",     0),
    ]])
    pred  = m.predict(X)[0]
    score = float(m.score_samples(X)[0])
    if pred == -1:
        return "anomaly", round(score, 4), classify_threat(data, baseline)
    return "safe", round(score, 4), {}

# ── PUBLIC detect() ───────────────────────────────────────────────────────────
def detect(data: dict) -> tuple:
    """
    Returns (verdict, ml_score, threat_info).

    Detection priority:
      1. Random Forest (if sklearn version compatible)
      2. Rate-based spike detector (always works — primary fallback)
      3. Isolation Forest (calibrated baseline)

    verdict    : "safe" or "anomaly"
    ml_score   : float (negative convention = anomaly)
    threat_info: dict with threat_type, threat_label, severity, payload
                 empty dict when verdict is "safe"
    """
    baseline = load_baseline()

    if _rf_enabled and _rf_model is not None:
        try:
            return _detect_rf(data, baseline)
        except Exception:
            pass

    # Rate-based is the most reliable on Windows
    return _rate_detector.detect(data, baseline)
