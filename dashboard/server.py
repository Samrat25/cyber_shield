# dashboard/server.py
"""
Flask server for CyberShield dashboard
Serves real-time monitoring UI with session key security
"""

import os
import uuid
import threading
import webbrowser
import time
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = Flask(__name__)
CORS(app)

# Save key to file so it persists across restarts
_KEY_FILE = Path("logs/dashboard_key.txt")
_KEY_FILE.parent.mkdir(exist_ok=True)

if _KEY_FILE.exists():
    SESSION_KEY = _KEY_FILE.read_text().strip()
else:
    SESSION_KEY = str(uuid.uuid4())
    _KEY_FILE.write_text(SESSION_KEY)
DASHBOARD_PORT = 7000

# In-memory buffer of last 60 metric readings for live chart
_live_buffer = []
_buffer_lock = threading.Lock()

def _check_key():
    """Middleware: every API call must carry ?key=SESSION_KEY."""
    k = request.args.get("key") or request.headers.get("X-Dashboard-Key")
    if k != SESSION_KEY:
        abort(403)

# ── Main dashboard HTML page ────────────────────────────────────────────────
@app.route("/")
def index():
    key = request.args.get("key", "")
    if key != SESSION_KEY:
        return "<h2 style='font-family:system-ui;color:#f87171;padding:40px'>"\
               "403 — Invalid or missing dashboard key.</h2>", 403
    return send_file(os.path.join(os.path.dirname(__file__), "index.html"))

# ── API: live metrics (last reading) ───────────────────────────────────────
@app.route("/api/metrics")
def api_metrics():
    _check_key()
    with _buffer_lock:
        return jsonify({
            "metrics": _live_buffer[-1] if _live_buffer else {},
            "history": list(_live_buffer)
        })

# ── API: threat + event log from Supabase ──────────────────────────────────
@app.route("/api/threats")
def api_threats():
    _check_key()
    try:
        from cybershield.core.db import get_recent_events
        events = get_recent_events(limit=50)
    except Exception:
        events = []
    return jsonify({"events": events})

# ── API: summary stats ──────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    _check_key()
    try:
        from cybershield.core.db import get_stats
        return jsonify(get_stats())
    except Exception:
        return jsonify({})

# ── API: P2P topology ───────────────────────────────────────────────────────
@app.route("/api/p2p")
def api_p2p():
    """
    Returns real P2P topology.
    - YOUR node from logs/node_state.json
    - Real connected peers from logs/peers.json
    - Mock node-3 to show network has scale
    """
    _check_key()
    import json
    from pathlib import Path
    
    # Your node
    state   = {}
    sf      = Path("logs/node_state.json")
    if sf.exists():
        try: state = json.loads(sf.read_text())
        except: pass
    
    node1_id     = state.get("node_id", "SAMRAT")
    node1_ip     = state.get("ip", "192.168.29.58")
    node1_status = state.get("status", "online")
    
    nodes = [{
        "id"    : node1_id,
        "ip"    : node1_ip,
        "status": node1_status,
        "type"  : "real",
        "role"  : "primary",
        "cpu"   : None,
        "mem"   : None,
    }]
    
    # Real peers from WebSocket connections
    pf = Path("logs/peers.json")
    real_peers = []
    if pf.exists():
        try:
            real_peers = list(json.loads(pf.read_text()).values())
        except: pass
    
    for p in real_peers:
        nodes.append({
            "id"    : p.get("node_id", "peer"),
            "ip"    : p.get("ip", "?"),
            "status": p.get("status", "online"),
            "type"  : "real",
            "role"  : "peer",
            "cpu"   : p.get("cpu_percent"),
            "mem"   : p.get("memory_percent"),
            "os"    : p.get("os", ""),
        })
    
    # Always add one mock node for visual scale
    nodes.append({
        "id"    : "node-mock",
        "ip"    : "192.168.29.99",
        "status": "online",
        "type"  : "mock",
        "role"  : "peer",
        "cpu"   : None,
        "mem"   : None,
    })
    
    compromised = node1_status in ("COMPROMISED", "compromised")
    
    # Build edges
    edges = []
    for n in nodes[1:]:   # all non-primary nodes
        edges.append({
            "from"   : node1_id,
            "to"     : n["id"],
            "active" : not compromised,
            "severed": compromised,
            "real"   : n["type"] == "real",
        })
    # Peer-to-peer edges (between non-primary)
    if len(nodes) > 2:
        edges.append({
            "from": nodes[1]["id"], "to": nodes[-1]["id"],
            "active": True, "severed": False, "real": False
        })
    
    last_threat = state.get("last_threat", {})
    
    return jsonify({
        "nodes"      : nodes,
        "edges"      : edges,
        "compromised": compromised,
        "last_threat": last_threat,
        "real_peers" : len(real_peers),
    })

# ── Background thread: collect metrics into buffer ─────────────────────────
def _collector():
    # Use core/ modules (Windows-safe, no heavy deps)
    from core.monitor import get_metrics
    from core.ml_detector import detect

    while True:
        try:
            m = get_metrics()
            verdict, score, threat_info = detect(m)
            m["verdict"] = verdict
            m["ml_score"] = score
            if threat_info:
                m["threat_type"] = threat_info.get("threat_type", "")
                m["threat_label"] = threat_info.get("threat_label", "")
                m["severity"] = threat_info.get("severity", "")

            with _buffer_lock:
                _live_buffer.append(m)
                if len(_live_buffer) > 60:
                    _live_buffer.pop(0)
        except Exception as e:
            print(f"[Collector] Error: {e}")

        time.sleep(5)

def start(open_browser=True):
    """Entry point called by CLI dashboard command."""
    from rich.console import Console
    from rich.panel import Panel

    c = Console()

    c.print(Panel(
        f"[bold cyan]CyberShield Dashboard[/bold cyan]\n\n"
        f"  URL : [cyan]http://localhost:{DASHBOARD_PORT}[/cyan]\n"
        f"  Key : [yellow]{SESSION_KEY}[/yellow]\n\n"
        f"  Full link:\n"
        f"  [green]http://localhost:{DASHBOARD_PORT}?key={SESSION_KEY}[/green]\n\n"
        f"  [dim]Share this link with judges. Key persists across restarts.[/dim]\n"
        f"  [dim]Reset with: del logs\\dashboard_key.txt[/dim]",
        border_style="cyan", expand=False
    ))

    # Start metric collector in background
    t = threading.Thread(target=_collector, daemon=True)
    t.start()

    # Auto-open browser
    if open_browser:
        url = f"http://localhost:{DASHBOARD_PORT}?key={SESSION_KEY}"
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    app.run(host="0.0.0.0", port=DASHBOARD_PORT, debug=False, use_reloader=False)
