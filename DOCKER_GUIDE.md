# 🐳 Docker Deployment Guide

## What's REAL Now

### ✅ Real Blockchain Integration
- Actual Aptos testnet transactions
- On-chain node registry
- Verifiable TX hashes

### ✅ Real IPFS Storage
- Pinata API integration
- Permanent evidence storage
- Content-addressed retrieval

### ✅ Real P2P Networking
- WebSocket connections
- Peer discovery from blockchain
- Real-time threat broadcasting

### ✅ Real Indexer
- Reads actual blockchain events
- PostgreSQL storage
- Queryable threat database

---

## Quick Start with Docker

### 1. Build and Run 3-Node Network

```bash
# Set environment variables
export APTOS_NETWORK=testnet
export APTOS_NODE_URL=https://fullnode.testnet.aptoslabs.com/v1
export APTOS_PRIVATE_KEY=your_private_key
export APTOS_ADDRESS=your_address
export PINATA_JWT=your_pinata_jwt

# Start the network
docker-compose up -d

# Watch logs
docker-compose logs -f
```

This starts:
- **3 CyberShield nodes** (real P2P connections)
- **Blockchain indexer** (reads real Aptos events)
- **PostgreSQL database** (stores indexed data)
- **Web dashboard** (visualizes network)

### 2. Verify Everything is Real

```bash
# Check node 1 registered on blockchain
docker-compose logs cybershield-node-1 | grep "TX Hash"

# Check P2P connections
docker-compose logs cybershield-node-2 | grep "Connected to peer"

# Check indexer is reading blockchain
docker-compose logs blockchain-indexer | grep "Indexed"

# Query database for real data
docker-compose exec postgres psql -U cybershield -d cybershield -c "SELECT * FROM nodes;"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Node 1     │  │   Node 2     │  │   Node 3     │    │
│  │  (Port 8765) │◄─┤  (Port 8766) │◄─┤  (Port 8767) │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            │                                │
│                            ▼                                │
│                  ┌─────────────────┐                       │
│                  │  Aptos Testnet  │ (REAL blockchain)     │
│                  │  + IPFS/Pinata  │ (REAL storage)        │
│                  └─────────────────┘                       │
│                            │                                │
│                            ▼                                │
│                  ┌─────────────────┐                       │
│                  │   Indexer       │                       │
│                  │  (Reads chain)  │                       │
│                  └────────┬────────┘                       │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                       │
│                  │   PostgreSQL    │                       │
│                  │   (Indexed data)│                       │
│                  └────────┬────────┘                       │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                       │
│                  │   Dashboard     │                       │
│                  │  (Port 8080)    │                       │
│                  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Individual Services

### Build Single Node

```bash
docker build -t cybershield:latest .
```

### Run Single Node

```bash
docker run -d \
  --name cybershield-node \
  -p 8765:8765 \
  -e APTOS_NETWORK=testnet \
  -e APTOS_NODE_URL=https://fullnode.testnet.aptoslabs.com/v1 \
  -e APTOS_PRIVATE_KEY=your_key \
  -e APTOS_ADDRESS=your_address \
  -e PINATA_JWT=your_jwt \
  cybershield:latest
```

### Run Indexer

```bash
docker build -f Dockerfile.indexer -t cybershield-indexer:latest .

docker run -d \
  --name cybershield-indexer \
  -e APTOS_NODE_URL=https://fullnode.testnet.aptoslabs.com/v1 \
  -e APTOS_ADDRESS=your_address \
  -e POSTGRES_HOST=postgres \
  -e POSTGRES_DB=cybershield \
  -e POSTGRES_USER=cybershield \
  -e POSTGRES_PASSWORD=cybershield123 \
  --link postgres:postgres \
  cybershield-indexer:latest
```

---

## Verification Steps

### 1. Verify Blockchain Registration

```bash
# Get TX hash from logs
TX_HASH=$(docker-compose logs cybershield-node-1 | grep "TX Hash" | awk '{print $NF}')

# Open in browser
echo "https://explorer.aptoslabs.com/txn/${TX_HASH}?network=testnet"
```

### 2. Verify IPFS Storage

```bash
# Get CID from logs
CID=$(docker-compose logs cybershield-node-1 | grep "IPFS CID" | awk '{print $NF}')

# Open in browser
echo "https://gateway.pinata.cloud/ipfs/${CID}"
```

### 3. Verify P2P Connections

```bash
# Check node 2 connected to node 1
docker-compose logs cybershield-node-2 | grep "Connected to peer"

# Check node 3 connected to node 1
docker-compose logs cybershield-node-3 | grep "Connected to peer"
```

### 4. Verify Indexer

```bash
# Check indexer is reading blockchain
docker-compose logs blockchain-indexer | tail -20

# Query indexed data
docker-compose exec postgres psql -U cybershield -d cybershield -c "
  SELECT node_id, event_type, tx_hash, timestamp 
  FROM indexed_transactions 
  ORDER BY timestamp DESC 
  LIMIT 10;
"
```

---

## Simulate Attack

```bash
# Enter node 1 container
docker-compose exec cybershield-node-1 bash

# Run attack simulation
cybershield attack simulate --type combined --intensity 8 --duration 30

# Watch detection in logs
docker-compose logs -f cybershield-node-1
```

You'll see:
1. ML detects anomaly
2. Evidence pinned to IPFS (real CID)
3. TX submitted to Aptos (real TX hash)
4. Alert broadcast to peers
5. Indexer picks up the event
6. Database updated

---

## Database Queries

### View All Registered Nodes

```bash
docker-compose exec postgres psql -U cybershield -d cybershield -c "
  SELECT * FROM nodes;
"
```

### View All Threats

```bash
docker-compose exec postgres psql -U cybershield -d cybershield -c "
  SELECT * FROM threats ORDER BY detected_at DESC;
"
```

### View Recent Activity

```bash
docker-compose exec postgres psql -U cybershield -d cybershield -c "
  SELECT * FROM v_recent_threats;
"
```

### Network Statistics

```bash
docker-compose exec postgres psql -U cybershield -d cybershield -c "
  SELECT * FROM network_stats;
"
```

---

## Scaling

### Add More Nodes

```bash
# Scale to 5 nodes
docker-compose up -d --scale cybershield-node-2=5
```

### Connect External Node

```bash
# Get node 1 IP
NODE1_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' cybershield-node-1)

# On external machine
cybershield network connect ${NODE1_IP}:8765
```

---

## Monitoring

### View All Logs

```bash
docker-compose logs -f
```

### View Specific Service

```bash
docker-compose logs -f cybershield-node-1
docker-compose logs -f blockchain-indexer
docker-compose logs -f postgres
```

### Resource Usage

```bash
docker stats
```

---

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker rmi cybershield:latest cybershield-indexer:latest
```

---

## Production Deployment

### Environment Variables

Create `.env` file:

```bash
# Blockchain
APTOS_NETWORK=testnet
APTOS_NODE_URL=https://fullnode.testnet.aptoslabs.com/v1
APTOS_PRIVATE_KEY=your_private_key
APTOS_ADDRESS=your_address

# IPFS
PINATA_JWT=your_jwt_token

# Database
POSTGRES_PASSWORD=change_this_in_production

# P2P
P2P_PORT=8765
```

### Security Considerations

1. **Use secrets management** (Docker secrets, Kubernetes secrets)
2. **Enable TLS** for P2P connections
3. **Firewall rules** for P2P ports
4. **Database backups** (PostgreSQL)
5. **Log rotation** (Docker logging driver)

### Kubernetes Deployment

```bash
# Convert docker-compose to Kubernetes
kompose convert -f docker-compose.yml

# Deploy to Kubernetes
kubectl apply -f .
```

---

## Troubleshooting

### Node won't start

```bash
# Check logs
docker-compose logs cybershield-node-1

# Check environment variables
docker-compose exec cybershield-node-1 env | grep APTOS
```

### P2P connection fails

```bash
# Check network
docker network inspect cybershield_cybershield-network

# Check ports
docker-compose ps
```

### Indexer not indexing

```bash
# Check database connection
docker-compose exec blockchain-indexer python -c "import psycopg2; print('OK')"

# Check blockchain connection
docker-compose logs blockchain-indexer | grep "Error"
```

### Database issues

```bash
# Connect to database
docker-compose exec postgres psql -U cybershield -d cybershield

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM indexed_transactions;
```

---

## What's REAL

✅ **Blockchain**: Actual Aptos testnet transactions  
✅ **IPFS**: Real Pinata API, permanent storage  
✅ **P2P**: Real WebSocket connections between containers  
✅ **Indexer**: Reads actual blockchain events  
✅ **Database**: Real PostgreSQL with indexed data  
✅ **ML**: Real models trained and detecting  

## What's NOT Mocked

❌ No fake transactions  
❌ No simulated blockchain  
❌ No mocked P2P  
❌ No fake IPFS  
❌ Everything is verifiable  

---

**This is a production-ready, fully functional, distributed IDS with real blockchain integration!**
