# cybershield/network/p2p_node.py
"""
Real P2P Node Implementation using WebSockets
Nodes can discover, connect, and share threat intelligence
"""

import asyncio
import json
import socket
import uuid
from typing import Dict, Set, Optional
from datetime import datetime
import websockets
from websockets.server import serve
from websockets.client import connect

from ..config import P2P_PORT, P2P_HOST, LOGS_DIR


class P2PNode:
    """Peer-to-peer node for distributed threat detection network."""
    
    def __init__(self, node_id: Optional[str] = None, port: int = P2P_PORT):
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.port = port
        self.host = P2P_HOST
        self.peers: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.peer_info: Dict[str, Dict] = {}
        self.server = None
        self.running = False
        self.message_handlers = {}
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            self.local_ip = "127.0.0.1"
    
    async def start(self):
        """Start the P2P node server."""
        self.running = True
        self.server = await serve(
            self._handle_connection,
            self.host,
            self.port
        )
        print(f"🌐 P2P Node started: {self.node_id}")
        print(f"   Listening on {self.local_ip}:{self.port}")
    
    async def stop(self):
        """Stop the P2P node server."""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all peer connections
        for peer_id, ws in list(self.peers.items()):
            await ws.close()
        
        self.peers.clear()
        self.peer_info.clear()
    
    async def _handle_connection(self, websocket, path):
        """Handle incoming peer connection."""
        peer_id = None
        try:
            # Wait for handshake
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get('type') == 'handshake':
                peer_id = data['node_id']
                self.peers[peer_id] = websocket
                self.peer_info[peer_id] = {
                    'node_id': peer_id,
                    'ip': data.get('ip', 'unknown'),
                    'connected_at': datetime.utcnow().isoformat(),
                    'status': 'online'
                }
                
                # Send handshake response
                await websocket.send(json.dumps({
                    'type': 'handshake_ack',
                    'node_id': self.node_id,
                    'ip': self.local_ip
                }))
                
                print(f"✓ Peer connected: {peer_id} ({self.peer_info[peer_id]['ip']})")
                
                # Listen for messages
                async for message in websocket:
                    await self._handle_message(peer_id, message)
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            if peer_id and peer_id in self.peers:
                del self.peers[peer_id]
                if peer_id in self.peer_info:
                    self.peer_info[peer_id]['status'] = 'offline'
                print(f"✗ Peer disconnected: {peer_id}")
    
    async def connect_to_peer(self, peer_address: str):
        """Connect to another peer node."""
        try:
            websocket = await connect(f"ws://{peer_address}")
            
            # Send handshake
            await websocket.send(json.dumps({
                'type': 'handshake',
                'node_id': self.node_id,
                'ip': self.local_ip
            }))
            
            # Wait for handshake response
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get('type') == 'handshake_ack':
                peer_id = data['node_id']
                self.peers[peer_id] = websocket
                self.peer_info[peer_id] = {
                    'node_id': peer_id,
                    'ip': data.get('ip', peer_address.split(':')[0]),
                    'connected_at': datetime.utcnow().isoformat(),
                    'status': 'online'
                }
                
                print(f"✓ Connected to peer: {peer_id} ({peer_address})")
                
                # Listen for messages in background
                asyncio.create_task(self._listen_to_peer(peer_id, websocket))
                
                return True
        
        except Exception as e:
            print(f"Failed to connect to {peer_address}: {e}")
            return False
    
    async def _listen_to_peer(self, peer_id: str, websocket):
        """Listen for messages from a peer."""
        try:
            async for message in websocket:
                await self._handle_message(peer_id, message)
        except websockets.exceptions.ConnectionClosed:
            if peer_id in self.peers:
                del self.peers[peer_id]
            if peer_id in self.peer_info:
                self.peer_info[peer_id]['status'] = 'offline'
            print(f"✗ Peer disconnected: {peer_id}")
    
    async def _handle_message(self, peer_id: str, message: str):
        """Handle incoming message from peer."""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            # Call registered handler
            if msg_type in self.message_handlers:
                await self.message_handlers[msg_type](peer_id, data)
            
        except Exception as e:
            print(f"Error handling message from {peer_id}: {e}")
    
    def register_handler(self, message_type: str, handler):
        """Register a message handler."""
        self.message_handlers[message_type] = handler
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected peers."""
        message_json = json.dumps(message)
        
        for peer_id, websocket in list(self.peers.items()):
            try:
                await websocket.send(message_json)
            except Exception as e:
                print(f"Failed to send to {peer_id}: {e}")
    
    async def send_to_peer(self, peer_id: str, message: Dict):
        """Send message to specific peer."""
        if peer_id in self.peers:
            try:
                await self.peers[peer_id].send(json.dumps(message))
            except Exception as e:
                print(f"Failed to send to {peer_id}: {e}")
    
    def get_peer_count(self) -> int:
        """Get number of connected peers."""
        return len(self.peers)
    
    def get_peer_list(self) -> list:
        """Get list of connected peers."""
        return [
            {
                'node_id': peer_id,
                **info
            }
            for peer_id, info in self.peer_info.items()
        ]
