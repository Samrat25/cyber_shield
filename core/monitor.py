# core/monitor.py
import psutil
import socket
import datetime

def get_metrics() -> dict:
    """Collects real system metrics using psutil."""
    return {
        "timestamp"       : datetime.datetime.now(datetime.UTC).isoformat(),
        "cpu_percent"     : psutil.cpu_percent(interval=0.5),
        "memory_percent"  : psutil.virtual_memory().percent,
        "process_count"   : len(psutil.pids()),
        "net_bytes_sent"  : psutil.net_io_counters().bytes_sent,
        "net_bytes_recv"  : psutil.net_io_counters().bytes_recv,
        "ip"              : socket.gethostbyname(socket.gethostname()),
    }
