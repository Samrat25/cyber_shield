# core/aptos_direct.py
"""
Direct Aptos API calls using requests - no async SDK needed.
Works reliably on Windows without hanging.
"""
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

NODE_URL    = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
PRIVATE_KEY = os.getenv("APTOS_PRIVATE_KEY", "").replace("0xed25519-priv-", "")
ADDRESS     = os.getenv("APTOS_ADDRESS", "")
NETWORK     = os.getenv("APTOS_NETWORK", "testnet")

def register_node(node_id: str, ip: str, ipfs_cid: str) -> str:
    """Register node using direct REST API calls."""
    return log_threat(node_id, ipfs_cid, "register")

def log_threat(node_id: str, ipfs_cid: str, verdict: str) -> str:
    """
    Submit transaction using direct REST API.
    This bypasses the hanging async SDK.
    """
    try:
        # Import here to avoid circular dependency
        from aptos_sdk.account import Account
        from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
        from aptos_sdk.bcs import Serializer
        
        # Create account from private key
        account = Account.load_key(PRIVATE_KEY)
        
        # Build transaction payload
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
        
        # Get account sequence number
        account_url = f"{NODE_URL}/accounts/{ADDRESS}"
        account_resp = requests.get(account_url, timeout=5)
        account_resp.raise_for_status()
        sequence_number = int(account_resp.json()["sequence_number"])
        
        # Build raw transaction
        from aptos_sdk.transactions import RawTransaction
        from aptos_sdk.type_tag import TypeTag
        
        raw_txn = RawTransaction(
            sender=account.address(),
            sequence_number=sequence_number,
            payload=payload,
            max_gas_amount=2000,
            gas_unit_price=100,
            expiration_timestamps_secs=int(time.time()) + 600,
            chain_id=2,  # testnet
        )
        
        # Sign transaction
        signature = account.sign(raw_txn.keyed())
        
        # Submit using REST API
        from aptos_sdk.authenticator import Authenticator, Ed25519Authenticator
        from aptos_sdk.transactions import SignedTransaction
        
        authenticator = Authenticator(
            Ed25519Authenticator(account.public_key(), signature)
        )
        
        signed_txn = SignedTransaction(raw_txn, authenticator)
        
        # Serialize and submit
        txn_bytes = signed_txn.bytes()
        
        headers = {"Content-Type": "application/x.aptos.signed_transaction+bcs"}
        submit_url = f"{NODE_URL}/transactions"
        
        submit_resp = requests.post(
            submit_url,
            data=txn_bytes,
            headers=headers,
            timeout=10
        )
        submit_resp.raise_for_status()
        
        tx_hash = submit_resp.json()["hash"]
        return tx_hash
        
    except Exception as e:
        raise Exception(f"Aptos direct API failed: {e}")

def get_log_count() -> int:
    """Get threat count using view function."""
    try:
        url = f"{NODE_URL}/view"
        payload = {
            "function": f"{ADDRESS}::threat_logger::get_count",
            "type_arguments": [],
            "arguments": [ADDRESS]
        }
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        result = resp.json()
        return int(result[0]) if result else 0
    except Exception:
        return 0

def explorer_url(tx_hash: str) -> str:
    return f"https://explorer.aptoslabs.com/txn/{tx_hash}?network={NETWORK}"
