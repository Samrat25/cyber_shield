# core/aptos.py
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

NODE_URL    = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
PRIVATE_KEY = os.getenv("APTOS_PRIVATE_KEY", "").replace("0xed25519-priv-", "")
ADDRESS     = os.getenv("APTOS_ADDRESS", "")
NETWORK     = os.getenv("APTOS_NETWORK", "testnet")

def _run_async(coro):
    """Helper to run async functions synchronously with proper event loop handling."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    else:
        # Already in async context - shouldn't happen but handle it
        return asyncio.create_task(coro)

async def _submit_async(node_id: str, ipfs_cid: str, verdict: str) -> str:
    """Submits a transaction to the blockchain."""
    from aptos_sdk.async_client import RestClient
    from aptos_sdk.account import Account
    from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
    from aptos_sdk.bcs import Serializer
    
    client = RestClient(NODE_URL)
    
    try:
        account = Account.load_key(PRIVATE_KEY)
        
        transaction_arguments = [
            TransactionArgument(node_id, Serializer.str),
            TransactionArgument(ipfs_cid, Serializer.str),
            TransactionArgument(verdict, Serializer.str),
        ]
        
        entry_function = EntryFunction.natural(
            f"{ADDRESS}::threat_logger",
            "log_threat",
            [],
            transaction_arguments
        )
        
        payload = TransactionPayload(entry_function)
        signed_tx = await client.create_bcs_signed_transaction(account, payload)
        tx_hash = await client.submit_bcs_transaction(signed_tx)
        
        # Don't wait for confirmation - just return hash immediately
        # This prevents hanging on slow testnet
        return tx_hash
        
    finally:
        await client.close()

def register_node(node_id: str, ip: str, ipfs_cid: str) -> str:
    """
    Logs node registration by calling log_threat with verdict='register'.
    This creates a real, permanent TX on testnet.
    """
    return _run_async(_submit_async(node_id, ipfs_cid, "register"))

def log_threat(node_id: str, ipfs_cid: str, verdict: str) -> str:
    """
    Calls the on-chain log_threat entry function.
    TX hash is permanent proof — visible on testnet explorer.
    """
    return _run_async(_submit_async(node_id, ipfs_cid, verdict))

async def _get_count_async() -> int:
    """Async version of get_log_count."""
    from aptos_sdk.async_client import RestClient
    
    client = RestClient(NODE_URL)
    try:
        result = await client.view_function(
            f"{ADDRESS}::threat_logger::get_count",
            [],
            [ADDRESS]
        )
        return int(result[0]) if result else 0
    except Exception:
        return 0
    finally:
        await client.close()

def get_log_count() -> int:
    """Reads the on-chain threat count — a live view function."""
    return _run_async(_get_count_async())

def explorer_url(tx_hash: str) -> str:
    return f"https://explorer.aptoslabs.com/txn/{tx_hash}?network={NETWORK}"
