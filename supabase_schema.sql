-- Supabase Schema for CyberShield
-- Run this in Supabase SQL Editor

-- Table 1: Every monitoring event
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    node_id TEXT NOT NULL,
    ip TEXT,
    cpu FLOAT,
    memory FLOAT,
    process_count INT,
    net_bytes_recv BIGINT,
    net_packets_recv BIGINT,
    disk FLOAT,
    verdict TEXT,  -- 'safe' or 'anomaly'
    ml_score FLOAT,
    ipfs_cid TEXT,
    aptos_tx TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table 2: Registered nodes
CREATE TABLE IF NOT EXISTS nodes (
    id BIGSERIAL PRIMARY KEY,
    node_id TEXT UNIQUE NOT NULL,
    ip TEXT,
    status TEXT DEFAULT 'online',  -- online / compromised / offline
    reg_cid TEXT,
    reg_tx TEXT,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_node_id ON events(node_id);
CREATE INDEX IF NOT EXISTS idx_events_verdict ON events(verdict);
CREATE INDEX IF NOT EXISTS idx_nodes_node_id ON nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);

-- Enable Row Level Security
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE nodes ENABLE ROW LEVEL SECURITY;

-- Allow public read access (dashboard reads this)
CREATE POLICY "public_read_events" ON events
    FOR SELECT USING (true);

CREATE POLICY "public_read_nodes" ON nodes
    FOR SELECT USING (true);

-- Allow service to insert/update
CREATE POLICY "service_insert_events" ON events
    FOR INSERT WITH CHECK (true);

CREATE POLICY "service_upsert_nodes" ON nodes
    FOR ALL USING (true);

-- Create view for recent threats
CREATE OR REPLACE VIEW v_recent_threats AS
SELECT 
    e.id,
    e.node_id,
    e.ip,
    e.cpu,
    e.memory,
    e.verdict,
    e.ml_score,
    e.ipfs_cid,
    e.aptos_tx,
    e.created_at,
    n.status as node_status
FROM events e
LEFT JOIN nodes n ON e.node_id = n.node_id
WHERE e.verdict = 'anomaly'
ORDER BY e.created_at DESC
LIMIT 100;

-- Create view for node summary
CREATE OR REPLACE VIEW v_node_summary AS
SELECT 
    n.node_id,
    n.ip,
    n.status,
    n.registered_at,
    n.last_seen,
    COUNT(e.id) FILTER (WHERE e.verdict = 'anomaly') as threat_count,
    COUNT(e.id) as total_checks
FROM nodes n
LEFT JOIN events e ON n.node_id = e.node_id
GROUP BY n.id, n.node_id, n.ip, n.status, n.registered_at, n.last_seen
ORDER BY n.registered_at DESC;
