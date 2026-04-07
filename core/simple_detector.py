# core/simple_detector.py
"""
Hybrid detector: Uses CICIDS2017-trained Random Forest when available,
falls back to rate-based detection.
"""
import json
import os
import numpy as np
from pathlib import Path
from collections import deque
from typing import Dict, Tuple

BASELINE_FILE = "logs/baseline.json"
RF_MODEL_PATH = "cybershield/ml/model/model_rf.pkl"
RF_SCALER_PATH = "cybershield/ml/model/scaler_rf.pkl"
RF_FEATURES_PATH = "cybershield/ml/model/features_rf.pkl"

WINDOW_SIZE = 6  # 6 readings = 30 seconds at 5s intervals

# Rate thresholds (per second) - fallback detection
THRESHOLDS = {
    "cpu_rate": 10.0,      # >10% CPU increase per second
    "mem_rate": 5.0,       # >5% memory increase per second
    "prc_rate": 20.0,      # >20 processes per second
    "pkt_rate": 1000.0,    # >1000 packets per second
    "byt_rate": 1_000_000, # >1MB per second
}

# Sliding window buffer
_history = deque(maxlen=WINDOW_SIZE)

def load_baseline() -> dict:
    """Load baseline from calibration."""
    if Path(BASELINE_FILE).exists():
        return json.loads(Path(BASELINE_FILE).read_text())
    # Default baseline if not calibrated
    return {
        "cpu_mean": 30.0, "cpu_std": 10.0,
        "mem_mean": 50.0, "mem_std": 10.0,
        "prc_mean": 150.0, "prc_std": 20.0,
        "pkt_mean": 100000.0, "pkt_std": 50000.0,
        "byt_mean": 10000000.0, "byt_std": 5000000.0,
    }

def calibrate(samples: int = 20, interval: float = 1.5) -> dict:
    """Sample machine for baseline - NO sklearn."""
    import time
    from core.monitor import get_metrics
    
    readings = []
    for _ in range(samples):
        m = get_metrics()
        readings.append({
            "cpu": m["cpu_percent"],
            "mem": m["memory_percent"],
            "prc": m["process_count"],
            "pkt": m.get("net_packets_sent", 0) + m.get("net_packets_recv", 0),
            "byt": m["net_bytes_sent"] + m["net_bytes_recv"],
        })
        time.sleep(interval)
    
    # Calculate mean and std
    def mean(vals): return sum(vals) / len(vals)
    def std(vals):
        m = mean(vals)
        return (sum((x - m) ** 2 for x in vals) / len(vals)) ** 0.5
    
    baseline = {
        "cpu_mean": mean([r["cpu"] for r in readings]),
        "cpu_std": max(std([r["cpu"] for r in readings]), 5.0),
        "mem_mean": mean([r["mem"] for r in readings]),
        "mem_std": max(std([r["mem"] for r in readings]), 3.0),
        "prc_mean": mean([r["prc"] for r in readings]),
        "prc_std": max(std([r["prc"] for r in readings]), 10.0),
        "pkt_mean": mean([r["pkt"] for r in readings]),
        "pkt_std": max(std([r["pkt"] for r in readings]), 1000.0),
        "byt_mean": mean([r["byt"] for r in readings]),
        "byt_std": max(std([r["byt"] for r in readings]), 50000.0),
    }
    
    # Adjust for high-memory machines (>90%)
    if baseline["mem_mean"] > 90.0:
        baseline["mem_std"] = 5.0
    
    Path(BASELINE_FILE).parent.mkdir(exist_ok=True)
    Path(BASELINE_FILE).write_text(json.dumps(baseline, indent=2))
    
    return baseline

def _detect_rf(metrics: Dict) -> Tuple[str, float, Dict]:
    """
    Uses Random Forest trained on CICIDS2017 dataset (~95% accuracy).
    Maps live system metrics to CICIDS feature space.
    """
    try:
        import joblib
        
        # Load trained models (may hang on Windows with sklearn)
        rf = joblib.load(RF_MODEL_PATH)
        scaler = joblib.load(RF_SCALER_PATH)
        features = joblib.load(RF_FEATURES_PATH)
    except Exception as e:
        # If loading fails, raise to trigger fallback
        raise Exception(f"Failed to load RF models: {e}")
    
    baseline = load_baseline()
    
    # Map psutil metrics to CICIDS2017 feature space
    # CICIDS has 78 features - we approximate the most important ones
    feature_map = {
        " Total Fwd Packets": metrics.get("net_packets_sent", 0),
        " Total Backward Packets": metrics.get("net_packets_recv", 0),
        "Total Length of Fwd Packets": metrics.get("net_bytes_sent", 0),
        " Total Length of Bwd Packets": metrics.get("net_bytes_recv", 0),
        " Flow Packets/s": metrics.get("net_packets_recv", 0) / 5.0,
        " Flow Bytes/s": metrics.get("net_bytes_recv", 0) / 5.0,
        " Flow Duration": 5000000,  # 5s in microseconds
        " Fwd Packet Length Max": 1500,
        " Bwd Packet Length Max": 1500,
        " Flow IAT Mean": 100,
        " Fwd IAT Total": 500000,
        " Active Mean": metrics.get("cpu_percent", 0) * 1000,
        " Idle Mean": (100 - metrics.get("cpu_percent", 0)) * 1000,
    }
    
    # Build feature vector in correct order
    X_row = np.array([[feature_map.get(f, 0) for f in features]])
    X_scaled = scaler.transform(X_row)
    
    # Predict
    pred = rf.predict(X_scaled)[0]  # 0=normal, 1=attack
    proba = rf.predict_proba(X_scaled)[0]  # [P(normal), P(attack)]
    
    # Convert to our convention: negative score = anomaly
    score = float(proba[0]) - 0.5  # negative if attack
    
    verdict = "anomaly" if pred == 1 else "safe"
    
    if verdict == "anomaly":
        # Classify threat type based on metrics
        threat_info = _classify_threat_rf(metrics, baseline, proba[1])
        return "anomaly", abs(score), threat_info
    
    return "safe", abs(score), {}

def _classify_threat_rf(metrics: Dict, baseline: dict, attack_prob: float) -> Dict:
    """Classify threat type based on which metrics are elevated."""
    cpu = metrics.get("cpu_percent", 0)
    mem = metrics.get("memory_percent", 0)
    procs = metrics.get("process_count", 0)
    pkt_rate = metrics.get("net_packets_sent", 0) / 5.0
    byt_rate = metrics.get("net_bytes_sent", 0) / 5.0
    
    # Determine threat type
    if pkt_rate > 1000 or byt_rate > 1000000:
        threat_type = "ddos"
        threat_label = "DDoS Attack (CICIDS2017 Model)"
        severity = "CRITICAL"
    elif cpu > baseline["cpu_mean"] + 2 * baseline["cpu_std"]:
        threat_type = "cpu_spike"
        threat_label = "CPU Spike Attack (CICIDS2017 Model)"
        severity = "HIGH"
    elif mem > baseline["mem_mean"] + 2 * baseline["mem_std"]:
        threat_type = "memory_bomb"
        threat_label = "Memory Bomb (CICIDS2017 Model)"
        severity = "CRITICAL"
    elif procs > baseline["prc_mean"] + 2 * baseline["prc_std"]:
        threat_type = "fork_bomb"
        threat_label = "Fork Bomb (CICIDS2017 Model)"
        severity = "CRITICAL"
    else:
        threat_type = "intrusion"
        threat_label = "Network Intrusion (CICIDS2017 Model)"
        severity = "HIGH"
    
    return {
        "threat_type": threat_type,
        "threat_label": threat_label,
        "severity": severity,
        "model": "Random Forest (CICIDS2017, 95% accuracy)",
        "attack_probability": f"{attack_prob*100:.1f}%",
        "payload": {
            "cpu_actual": f"{cpu:.1f}",
            "cpu_baseline": f"{baseline['cpu_mean']:.1f}",
            "cpu_rate": f"{abs(cpu - baseline['cpu_mean']):.1f}%",
            "mem_actual": f"{mem:.1f}",
            "mem_baseline": f"{baseline['mem_mean']:.1f}",
            "mem_rate": f"{abs(mem - baseline['mem_mean']):.1f}%",
            "procs_actual": f"{procs}",
            "procs_baseline": f"{baseline['prc_mean']:.0f}",
            "procs_rate": f"{abs(procs - baseline['prc_mean']):.0f}",
            "pkt_rate": f"{pkt_rate:.0f}/s",
            "byt_rate": f"{byt_rate/1024/1024:.2f}MB/s",
        }
    }

def _detect_rate_based(metrics: Dict) -> Tuple[str, float, Dict]:
    """
    Fallback rate-based detection - looks for SUDDEN CHANGES.
    """
    baseline = load_baseline()
    
    # Extract current values
    current = {
        "cpu": metrics["cpu_percent"],
        "mem": metrics["memory_percent"],
        "prc": metrics["process_count"],
        "pkt": metrics.get("net_packets_sent", 0) + metrics.get("net_packets_recv", 0),
        "byt": metrics["net_bytes_sent"] + metrics["net_bytes_recv"],
    }
    
    # Add to history
    _history.append(current)
    
    # Need at least 2 readings to calculate rate
    if len(_history) < 2:
        return "safe", 0.0, {}
    
    # Calculate rates (change per second, assuming 5s interval)
    interval = 5.0  # seconds between readings
    prev = _history[-2]
    
    rates = {
        "cpu_rate": abs(current["cpu"] - prev["cpu"]) / interval,
        "mem_rate": abs(current["mem"] - prev["mem"]) / interval,
        "prc_rate": abs(current["prc"] - prev["prc"]) / interval,
        "pkt_rate": abs(current["pkt"] - prev["pkt"]) / interval,
        "byt_rate": abs(current["byt"] - prev["byt"]) / interval,
    }
    
    # Check if any rate exceeds threshold
    anomalies = []
    for key, rate in rates.items():
        if rate > THRESHOLDS[key]:
            anomalies.append(key)
    
    # Classify threat type
    threat_type = "unknown"
    threat_label = "Unknown"
    severity = "LOW"
    
    if anomalies:
        if "cpu_rate" in anomalies:
            threat_type = "cpu_spike"
            threat_label = "CPU Spike Attack (Rate-Based)"
            severity = "HIGH"
        elif "mem_rate" in anomalies:
            threat_type = "memory_bomb"
            threat_label = "Memory Bomb (Rate-Based)"
            severity = "CRITICAL"
        elif "prc_rate" in anomalies:
            threat_type = "fork_bomb"
            threat_label = "Fork Bomb (Rate-Based)"
            severity = "CRITICAL"
        elif "pkt_rate" in anomalies or "byt_rate" in anomalies:
            threat_type = "ddos"
            threat_label = "DDoS Attack (Rate-Based)"
            severity = "HIGH"
    
    # Calculate anomaly score (0-1)
    score = 0.0
    for key in anomalies:
        score += min(rates[key] / THRESHOLDS[key], 2.0)  # Cap at 2x threshold
    score = min(score / len(THRESHOLDS), 1.0)  # Normalize to 0-1
    
    if not anomalies:
        return "safe", score, {}
    
    # Build threat info payload
    threat_info = {
        "threat_type": threat_type,
        "threat_label": threat_label,
        "severity": severity,
        "model": "Rate-Based Detection (Fallback)",
        "payload": {
            "cpu_actual": f"{current['cpu']:.1f}",
            "cpu_baseline": f"{baseline['cpu_mean']:.1f}",
            "cpu_rate": f"{rates['cpu_rate']:.1f}%/s",
            "mem_actual": f"{current['mem']:.1f}",
            "mem_baseline": f"{baseline['mem_mean']:.1f}",
            "mem_rate": f"{rates['mem_rate']:.1f}%/s",
            "procs_actual": f"{current['prc']}",
            "procs_baseline": f"{baseline['prc_mean']:.0f}",
            "procs_rate": f"{rates['prc_rate']:.1f}/s",
            "pkt_rate": f"{rates['pkt_rate']:.0f}/s",
            "byt_rate": f"{rates['byt_rate']/1024/1024:.2f}MB/s",
        }
    }
    
    return "anomaly", score, threat_info

def detect(metrics: Dict) -> Tuple[str, float, Dict]:
    """
    Main detection function.
    Uses Random Forest (CICIDS2017, 95% accuracy) if available,
    falls back to rate-based detection.
    
    NOTE: RF model disabled on Windows due to sklearn/joblib hanging issue.
    Use rate-based detection which works reliably.
    """
    # DISABLED: RF model hangs on Windows when loading sklearn objects
    # Try RF model first
    # if os.path.exists(RF_MODEL_PATH):
    #     try:
    #         return _detect_rf(metrics)
    #     except Exception as e:
    #         # RF failed, fall back to rate-based
    #         print(f"[Warning] RF model failed: {e}, using rate-based detection")
    #         return _detect_rate_based(metrics)
    
    # Use rate-based detection (works reliably on Windows)
    return _detect_rate_based(metrics)

def train():
    """Dummy train function for compatibility - models are pre-trained."""
    pass

