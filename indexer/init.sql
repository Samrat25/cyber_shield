-- Database schema for CyberShield indexer

-- Indexed transactions from blockchain
CREATE TABLE IF NOT EXISTS indexed_transactions (
    id SERIAL PRIMARY KEY,
    version BIGINT UNIQUE NOT NULL,
    tx_hash VARCHAR(66) NOT NULL,
    sender VARCHAR(66) NOT NULL,
    timestamp BIGINT NOT NULL,
    success BOOLEAN NOT NULL,
    event_type VARCHAR(50),
    node_id VARCHAR(100),
    ipfs_cid VARCHAR(100),
    verdict VARCHAR(50),
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_version (version),
    INDEX idx_event_type (event_type),
    INDEX idx_node_id (node_id),
    INDEX idx_timestamp (timestamp)
);

-- Registered nodes (aggregated view)
CREATE TABLE IF NOT EXISTS nodes (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(100) UNIQUE NOT NULL,
    ip VARCHAR(45),
    ipfs_cid VARCHAR(100),
    status VARCHAR(20) DEFAULT 'online',
    registered_at TIMESTAMP,
    last_seen TIMESTAMP,
    threat_count INTEGER DEFAULT 0,
    INDEX idx_node_id (node_id),
    INDEX idx_status (status)
);

-- Threat detections (aggregated view)
CREATE TABLE IF NOT EXISTS threats (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(100) NOT NULL,
    ipfs_cid VARCHAR(100) NOT NULL,
    verdict VARCHAR(50) NOT NULL,
    tx_hash VARCHAR(66) NOT NULL,
    detected_at TIMESTAMP NOT NULL,
    INDEX idx_node_id (node_id),
    INDEX idx_detected_at (detected_at)
);

-- Network statistics
CREATE TABLE IF NOT EXISTS network_stats (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_nodes INTEGER DEFAULT 0,
    active_nodes INTEGER DEFAULT 0,
    total_threats INTEGER DEFAULT 0,
    threats_last_hour INTEGER DEFAULT 0,
    threats_last_day INTEGER DEFAULT 0
);

-- Create views for easy querying
CREATE OR REPLACE VIEW v_recent_threats AS
SELECT 
    t.node_id,
    t.ipfs_cid,
    t.verdict,
    t.tx_hash,
    t.detected_at,
    n.ip,
    n.status
FROM threats t
LEFT JOIN nodes n ON t.node_id = n.node_id
ORDER BY t.detected_at DESC
LIMIT 100;

CREATE OR REPLACE VIEW v_node_summary AS
SELECT 
    n.node_id,
    n.ip,
    n.status,
    n.registered_at,
    n.last_seen,
    n.threat_count,
    COUNT(t.id) as total_detections
FROM nodes n
LEFT JOIN threats t ON n.node_id = t.node_id
GROUP BY n.id, n.node_id, n.ip, n.status, n.registered_at, n.last_seen, n.threat_count
ORDER BY n.registered_at DESC;

-- Insert initial stats row
INSERT INTO network_stats (total_nodes, active_nodes, total_threats, threats_last_hour, threats_last_day)
VALUES (0, 0, 0, 0, 0);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cybershield;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cybershield;
