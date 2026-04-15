#!/usr/bin/env python3
"""
Kali Linux Peer Node - Connects to CyberShield Windows Server
Sends real-time system metrics to the P2P network
"""

import asyncio
import json
import socket
import psutil
import argparse
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Error: websockets not installed")
    print("Install with: pip3 install websockets")
    exit(1)


def get_node_id():
    """Get Kali node ID from hostname."""
    return socket.gethostname()


def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_metrics():
    """Collect system metrics."""
    return {
        "node_id": get_node_id(),
        "ip": get_local_ip(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "process_count": len(psutil.pids()),
        "timestamp": datetime.utcnow().isoformat(),
        "os": "Kali Linux",
        "verdict": "safe"
    }


async def connect_to_server(server_address):
    """Connect to CyberShield Windows server and send metrics."""
    node_id = get_node_id()
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("CyberShield Kali Peer Node")
    print("=" * 60)
    print(f"\nNode ID: {node_id}")
    print(f"Local IP: {local_ip}")
    print(f"Server: {server_address}")
    
    # Validate server address format
    if not server_address or server_address.startswith("-"):
        print("\n✗ Error: Invalid server address format")
        print("Usage: python3 kali_peer.py --server <IP>:<PORT>")
        print("Example: python3 kali_peer.py --server 192.168.29.58:8765")
        return
    
    print("\nConnecting...\n")
    
    uri = f"ws://{server_address}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✓ Connected to CyberShield server")
            
            # Send registration
            await websocket.send(json.dumps({
                "type": "register",
                "node_id": node_id,
                "ip": local_ip,
                "os": "Kali Linux"
            }))
            
            # Wait for acknowledgment
            try:
                ack = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                ack_data = json.loads(ack)
                if ack_data.get("type") == "ack":
                    print(f"✓ Registration confirmed")
                    print(f"  {ack_data.get('message', '')}")
                    print(f"  Total peers: {ack_data.get('peers', 1)}\n")
            except asyncio.TimeoutError:
                print("⚠ No acknowledgment received, continuing...\n")
            
            print("Sending metrics every 5 seconds...")
            print("Press Ctrl+C to disconnect\n")
            
            # Send metrics periodically
            counter = 0
            while True:
                metrics = get_metrics()
                
                await websocket.send(json.dumps({
                    "type": "heartbeat",
                    "data": metrics
                }))
                
                counter += 1
                print(f"[{counter:03d}] Sent: CPU={metrics['cpu_percent']:.1f}%  "
                      f"MEM={metrics['memory_percent']:.1f}%  "
                      f"PROCS={metrics['process_count']}")
                
                await asyncio.sleep(5)
    
    except websockets.exceptions.WebSocketException as e:
        print(f"\n✗ Connection error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure Windows server is running:")
        print("     cybershield network listen --port 8765")
        print("  2. Check Windows IP address is correct")
        print("  3. Check firewall allows port 8765")
        print("  4. Test connection: telnet <WINDOWS_IP> 8765")
    
    except KeyboardInterrupt:
        print("\n\n✓ Disconnected from server")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Kali Linux peer node for CyberShield",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 kali_peer.py --server 192.168.29.58:8765
  python3 kali_peer.py --server 10.0.0.5:8765
        """
    )
    parser.add_argument(
        "--server",
        required=True,
        metavar="IP:PORT",
        help="Windows server address (e.g., 192.168.29.58:8765)"
    )
    
    args = parser.parse_args()
    
    # Validate server address format
    if ":" not in args.server:
        print("✗ Error: Server address must include port")
        print("\nCorrect format: IP:PORT")
        print("Example: python3 kali_peer.py --server 192.168.29.58:8765")
        exit(1)
    
    # Validate IP and port
    try:
        ip, port = args.server.split(":")
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
    except ValueError as e:
        print(f"✗ Error: Invalid server address - {e}")
        print("\nExample: python3 kali_peer.py --server 192.168.29.58:8765")
        exit(1)
    
    print(f"\n[Kali Peer] Starting connection to {args.server}...")
    
    try:
        asyncio.run(connect_to_server(args.server))
    except KeyboardInterrupt:
        print("\n\nShutdown complete")


if __name__ == "__main__":
    main()
