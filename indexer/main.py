#!/usr/bin/env python3
"""
Blockchain Indexer - Indexes all CyberShield events from Aptos blockchain
This is REAL - it reads actual blockchain data and stores it in PostgreSQL
"""

import asyncio
import os
import time
import psycopg2
from aptos_sdk.async_client import RestClient
from datetime import datetime

# Configuration
APTOS_NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
APTOS_ADDRESS = os.getenv("APTOS_ADDRESS", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cybershield")
POSTGRES_USER = os.getenv("POSTGRES_USER", "cybershield")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cybershield123")

# Database connection
def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

async def get_latest_indexed_version(conn):
    """Get the latest indexed transaction version."""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(version) FROM indexed_transactions")
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result[0] else 0

async def index_transaction(conn, tx_data):
    """Index a single transaction."""
    cursor = conn.cursor()
    
    try:
        version = tx_data.get('version')
        tx_hash = tx_data.get('hash')
        sender = tx_data.get('sender')
        timestamp = tx_data.get('timestamp')
        success = tx_data.get('success', False)
        
        # Parse payload to determine event type
        payload = tx_data.get('payload', {})
        function_name = payload.get('function', '')
        
        event_type = None
        node_id = None
        ipfs_cid = None
        verdict = None
        
        if 'register_node' in function_name:
            event_type = 'node_registration'
            args = payload.get('arguments', [])
            if len(args) >= 3:
                node_id = args[0]
                ipfs_cid = args[2]
        
        elif 'log_threat' in function_name:
            event_type = 'threat_detected'
            args = payload.get('arguments', [])
            if len(args) >= 3:
                node_id = args[0]
                ipfs_cid = args[1]
                verdict = args[2]
        
        elif 'update_node_status' in function_name:
            event_type = 'status_update'
            args = payload.get('arguments', [])
            if len(args) >= 2:
                node_id = args[0]
                verdict = args[1]
        
        # Insert into database
        cursor.execute("""
            INSERT INTO indexed_transactions 
            (version, tx_hash, sender, timestamp, success, event_type, node_id, ipfs_cid, verdict)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (version) DO NOTHING
        """, (version, tx_hash, sender, timestamp, success, event_type, node_id, ipfs_cid, verdict))
        
        conn.commit()
        
        if event_type:
            print(f"✓ Indexed {event_type}: version={version}, node={node_id}")
        
    except Exception as e:
        print(f"Error indexing transaction: {e}")
        conn.rollback()
    finally:
        cursor.close()

async def index_blockchain():
    """Main indexing loop - reads blockchain and indexes events."""
    print("🔍 Starting Blockchain Indexer...")
    print(f"   Aptos Node: {APTOS_NODE_URL}")
    print(f"   Contract: {APTOS_ADDRESS}")
    print(f"   Database: {POSTGRES_HOST}/{POSTGRES_DB}\n")
    
    # Wait for database to be ready
    while True:
        try:
            conn = get_db_connection()
            conn.close()
            print("✓ Database connection established\n")
            break
        except Exception as e:
            print(f"Waiting for database... {e}")
            time.sleep(5)
    
    client = RestClient(APTOS_NODE_URL)
    
    while True:
        try:
            conn = get_db_connection()
            
            # Get latest indexed version
            last_version = await get_latest_indexed_version(conn)
            
            # Get account transactions from blockchain
            # This is REAL - it queries actual Aptos blockchain
            transactions = await client.account_transactions(
                APTOS_ADDRESS,
                start=last_version + 1,
                limit=100
            )
            
            if transactions:
                print(f"📥 Found {len(transactions)} new transactions")
                
                for tx in transactions:
                    await index_transaction(conn, tx)
                
                print(f"✓ Indexed up to version {transactions[-1].get('version')}\n")
            
            conn.close()
            
            # Wait before next poll
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Error in indexing loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("=" * 60)
    print("CyberShield Blockchain Indexer")
    print("=" * 60)
    asyncio.run(index_blockchain())
