# cybershield/core/db.py
"""
Supabase integration for persistent event logging and dashboard
All monitoring events are logged here for real-time visualization
"""

import os
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_db():
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL", "")
            key = os.getenv("SUPABASE_KEY", "")
            if url and key:
                _client = create_client(url, key)
        except ImportError:
            print("[DB] Supabase not installed. Run: pip install supabase")
        except Exception as e:
            print(f"[DB] Failed to connect: {e}")
    return _client

def log_event(metrics: dict, verdict: str, ml_score: float,
              ipfs_cid: str = None, aptos_tx: str = None,
              threat_type: str = None, threat_label: str = None,
              severity: str = None, zk_proof: str = None):
    """
    Log every monitoring check to Supabase.
    Called from monitor loop for both safe and anomaly events.
    """
    db = get_db()
    if not db:
        return  # Silently skip if Supabase not configured
    
    row = {
        "node_id"         : metrics.get("node_id", "unknown"),
        "ip"              : metrics.get("ip"),
        "cpu"             : metrics.get("cpu_percent"),
        "memory"          : metrics.get("memory_percent"),
        "process_count"   : metrics.get("process_count"),
        "net_bytes_recv"  : metrics.get("net_bytes_recv"),
        "net_packets_recv": metrics.get("net_packets_recv", 0),
        "disk"            : metrics.get("disk_percent", 0),
        "verdict"         : verdict,
        "ml_score"        : ml_score,
        "ipfs_cid"        : ipfs_cid,
        "aptos_tx"        : aptos_tx,
        "threat_type"     : threat_type,
        "threat_label"    : threat_label,
        "severity"        : severity,
        "zk_proof"        : zk_proof,
    }
    
    try:
        db.table("events").insert(row).execute()
    except Exception as e:
        print(f"[DB] Insert failed: {e}")

def upsert_node(node_id: str, ip: str, status: str,
                reg_cid: str = None, reg_tx: str = None):
    """
    Keep nodes table current.
    Called on register and status changes.
    """
    db = get_db()
    if not db:
        return
    
    row = {
        "node_id": node_id,
        "ip": ip,
        "status": status,
    }
    
    if reg_cid:
        row["reg_cid"] = reg_cid
    if reg_tx:
        row["reg_tx"] = reg_tx
    
    try:
        db.table("nodes").upsert(row, on_conflict="node_id").execute()
    except Exception as e:
        print(f"[DB] Upsert failed: {e}")

def get_recent_events(limit: int = 100) -> list:
    """Get recent events for dashboard."""
    db = get_db()
    if not db:
        return []
    
    try:
        res = db.table("events").select("*").order(
            "created_at", desc=True
        ).limit(limit).execute()
        return res.data
    except Exception:
        return []

def get_stats() -> dict:
    """Get summary statistics for dashboard."""
    db = get_db()
    if not db:
        return {}
    
    try:
        # Get all events
        all_events = db.table("events").select("verdict").execute().data
        total = len(all_events)
        threats = sum(1 for e in all_events if e.get("verdict") == "anomaly")
        
        # Get all nodes
        nodes = db.table("nodes").select("*").execute().data
        
        safe_rate = round((total - threats) / max(total, 1) * 100, 1) if total > 0 else 100.0
        
        return {
            "total_checks": total,
            "total_threats": threats,
            "nodes": nodes,
            "safe_rate": safe_rate
        }
    except Exception:
        return {}
