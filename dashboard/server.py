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
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from cybershield.core.monitor import SystemMonitor
from cybershield.ml import get_detector
from cybershield.core.db import get_recent_events, get_stats

app = Flask(__name__)
CORS(app)

# Generate fresh UUID key every time dashboard starts
# Only someone who ran the CLI can see this key - security by design
SESSION_KEY = str(uuid.uuid4())
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
    events = get_recent_events(limit=50)
    return jsonify({"events": events})

# ── API: summary stats ──────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    _check_key()
    return jsonify(get_stats())

# ── Background thread: collect metrics into buffer ─────────────────────────
def _collector():
    monitor = SystemMonitor()
    detector = get_detector()
    
    while True:
        try:
            m = monitor.get_metrics()
            verdict, score, _ = detector.detect(m)
            m["verdict"] = verdict
            m["ml_score"] = score
            m["node_id"] = os.getenv("NODE_ID", "unknown")
            
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
        f"  [dim]Share this link with judges. Key expires when you stop the server.[/dim]",
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
