# cybershield/core/monitor.py
import psutil
import socket
import datetime


class SystemMonitor:
    """Collects comprehensive system metrics."""
    
    def __init__(self):
        self.baseline = self._get_baseline()
    
    def _get_baseline(self):
        """Get baseline metrics for comparison."""
        return {
            'cpu': psutil.cpu_percent(interval=0.1),
            'memory': psutil.virtual_memory().percent,
            'processes': len(psutil.pids())
        }
    
    def get_metrics(self) -> dict:
        """Collect current system metrics."""
        # Network I/O
        net_io = psutil.net_io_counters()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        
        # Disk usage percentage
        try:
            disk_usage = psutil.disk_usage('/').percent
        except Exception:
            disk_usage = 0.0
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "127.0.0.1"
        
        return {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "memory_percent": psutil.virtual_memory().percent,
            "process_count": len(psutil.pids()),
            "net_bytes_sent": net_io.bytes_sent,
            "net_bytes_recv": net_io.bytes_recv,
            "net_packets_sent": net_io.packets_sent if hasattr(net_io, 'packets_sent') else 0,
            "net_packets_recv": net_io.packets_recv if hasattr(net_io, 'packets_recv') else 0,
            "disk_read_bytes": disk_io.read_bytes if disk_io else 0,
            "disk_write_bytes": disk_io.write_bytes if disk_io else 0,
            "disk_percent": disk_usage,
            "ip": local_ip,
        }
