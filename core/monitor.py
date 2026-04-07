# core/monitor.py — Windows-safe, no hanging calls
import psutil, socket, datetime, os

def get_metrics() -> dict:
    """
    Collects 12+ system metrics.
    All calls have fallbacks — nothing hangs on Windows.
    """
    # cpu_percent with interval=0 uses cached value — instant, no block
    cpu = psutil.cpu_percent(interval=0)
    if cpu == 0.0:
        # First call returns 0 — call twice with small gap
        import time; time.sleep(0.2)
        cpu = psutil.cpu_percent(interval=0)

    mem  = psutil.virtual_memory()
    net  = psutil.net_io_counters()
    swap = psutil.swap_memory()

    # Disk — use C:\ on Windows, / on Linux
    disk_path = "C:\\" if os.name == "nt" else "/"
    try:
        disk = psutil.disk_usage(disk_path)
        disk_pct = disk.percent
    except Exception:
        disk_pct = 0.0

    # Disk I/O
    try:
        dio = psutil.disk_io_counters()
        disk_read_mb  = round(dio.read_bytes  / 1024 / 1024, 2) if dio else 0
        disk_write_mb = round(dio.write_bytes / 1024 / 1024, 2) if dio else 0
    except Exception:
        disk_read_mb = disk_write_mb = 0.0

    # Net connections — SKIP on Windows without admin (hangs/crashes)
    net_conns = 0
    if os.name != "nt":  # Linux/Mac only
        try:
            net_conns = len(psutil.net_connections(kind="all"))
        except Exception:
            net_conns = 0

    # CPU frequency
    try:
        freq = psutil.cpu_freq()
        cpu_freq = round(freq.current) if freq else 0
    except Exception:
        cpu_freq = 0

    # CPU temperature (Linux only)
    cpu_temp = 0.0
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    if entries:
                        cpu_temp = entries[0].current
                        break
    except Exception:
        pass

    # IP address
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "127.0.0.1"

    return {
        # Identity
        "node_id"          : socket.gethostname(),
        "ip"               : ip,
        "timestamp"        : datetime.datetime.utcnow().isoformat(),

        # Core metrics
        "cpu_percent"      : round(cpu, 2),
        "memory_percent"   : round(mem.percent, 2),
        "process_count"    : len(psutil.pids()),
        "net_bytes_recv"   : net.bytes_recv,
        "net_bytes_sent"   : net.bytes_sent,
        "net_packets_recv" : net.packets_recv,
        "net_packets_sent" : net.packets_sent,

        # Extended
        "disk_percent"     : round(disk_pct, 1),
        "disk_read_mb"     : disk_read_mb,
        "disk_write_mb"    : disk_write_mb,
        "net_connections"  : net_conns,    # 0 on Windows (safe fallback)
        "swap_percent"     : round(swap.percent, 1),
        "cpu_freq_mhz"     : cpu_freq,
        "cpu_temp"         : round(cpu_temp, 1),

        # Derived (useful for ML)
        "mem_used_mb"      : round(mem.used  / 1024 / 1024),
        "mem_total_mb"     : round(mem.total / 1024 / 1024),
        "pkt_byte_ratio"   : round(
            net.packets_recv / max(net.bytes_recv, 1) * 1000, 4
        ),
    }
