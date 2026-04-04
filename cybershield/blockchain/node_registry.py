# cybershield/blockchain/node_registry.py
"""
Real blockchain-based node registry
Nodes register themselves on-chain and discover peers via blockchain
"""

import asyncio
from typing import List, Dict
from ..config import APTOS_NODE_URL, APTOS_ADDRESS


class NodeRegistry:
    """Manages node registration and discovery via blockchain."""
    
    def __init__(self):
        self.node_url = APTOS_NODE_URL
        self.contract_address = APTOS_ADDRESS
    
    async def get_all_registered_nodes(self) -> List[Dict]:
        """
        Query blockchain to get all registered nodes.
        This is REAL - reads from Aptos blockchain.
        """
        from aptos_sdk.async_client import RestClient
        
        client = RestClient(self.node_url)
        
        try:
            # Query the blockchain for all registered nodes
            # This reads the actual on-chain data
            result = await client.view_function(
                f"{self.contract_address}::threat_logger::get_all_nodes",
                [],
                []
            )
            
            await client.close()
            
            # Parse the result into node information
            nodes = []
            if result and len(result) > 0:
                # Result format: [[node_id1, ip1, cid1], [node_id2, ip2, cid2], ...]
                for node_data in result[0]:
                    nodes.append({
                        'node_id': node_data[0],
                        'ip': node_data[1],
                        'ipfs_cid': node_data[2],
                        'status': 'online'
                    })
            
            return nodes
            
        except Exception as e:
            print(f"Error querying blockchain: {e}")
            await client.close()
            return []
    
    def get_all_nodes_sync(self) -> List[Dict]:
        """Synchronous wrapper for getting all nodes."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.get_all_registered_nodes())
    
    async def get_node_info(self, node_id: str) -> Dict:
        """Get specific node information from blockchain."""
        from aptos_sdk.async_client import RestClient
        
        client = RestClient(self.node_url)
        
        try:
            result = await client.view_function(
                f"{self.contract_address}::threat_logger::get_node_info",
                [],
                [node_id]
            )
            
            await client.close()
            
            if result and len(result) > 0:
                return {
                    'node_id': result[0][0],
                    'ip': result[0][1],
                    'ipfs_cid': result[0][2],
                    'registered_at': result[0][3]
                }
            
            return {}
            
        except Exception:
            await client.close()
            return {}
