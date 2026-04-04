# cybershield/blockchain/aptos.py
import asyncio
from ..config import APTOS_NODE_URL, APTOS_PRIVATE_KEY, APTOS_ADDRESS, APTOS_NETWORK


class AptosClient:
    """Client for Aptos blockchain interactions."""
    
    def __init__(self):
        self.node_url = APTOS_NODE_URL
        self.private_key = APTOS_PRIVATE_KEY
        self.address = APTOS_ADDRESS
        self.network = APTOS_NETWORK
    
    def _run_async(self, coro):
        """Helper to run async functions synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    async def _submit_async(self, node_id: str, ipfs_cid: str, verdict: str) -> str:
        """Submit transaction to blockchain."""
        from aptos_sdk.async_client import RestClient
        from aptos_sdk.account import Account
        from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
        from aptos_sdk.bcs import Serializer
        
        client = RestClient(self.node_url)
        account = Account.load_key(self.private_key)
        
        entry_function = EntryFunction.natural(
            f"{self.address}::threat_logger",
            "log_threat",
            [],
            [
                TransactionArgument(node_id, Serializer.str),
                TransactionArgument(ipfs_cid, Serializer.str),
                TransactionArgument(verdict, Serializer.str),
            ]
        )
        
        payload = TransactionPayload(entry_function)
        signed_tx = await client.create_bcs_signed_transaction(account, payload)
        tx_hash = await client.submit_bcs_transaction(signed_tx)
        await client.wait_for_transaction(tx_hash)
        await client.close()
        
        return tx_hash
    
    def register_node(self, node_id: str, ip: str, ipfs_cid: str) -> str:
        """Register node on blockchain."""
        return self._run_async(self._submit_async(node_id, ipfs_cid, "register"))
    
    def log_threat(self, node_id: str, ipfs_cid: str, verdict: str) -> str:
        """Log threat on blockchain."""
        return self._run_async(self._submit_async(node_id, ipfs_cid, verdict))
    
    async def _get_count_async(self) -> int:
        """Get threat count from blockchain."""
        from aptos_sdk.async_client import RestClient
        
        client = RestClient(self.node_url)
        try:
            result = await client.view_function(
                f"{self.address}::threat_logger::get_count",
                [],
                [self.address]
            )
            await client.close()
            return int(result[0]) if result else 0
        except Exception:
            await client.close()
            return 0
    
    def get_log_count(self) -> int:
        """Get threat count from blockchain."""
        return self._run_async(self._get_count_async())
    
    def explorer_url(self, tx_hash: str) -> str:
        """Get explorer URL for transaction."""
        return f"https://explorer.aptoslabs.com/txn/{tx_hash}?network={self.network}"
