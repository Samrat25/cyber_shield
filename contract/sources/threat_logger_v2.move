// Enhanced Move contract with node registry and discovery
module cybershield_addr::threat_logger {
    use std::signer;
    use std::string::String;
    use std::vector;
    use aptos_framework::timestamp;
    use aptos_framework::table::{Self, Table};

    /// Node information stored on-chain
    struct NodeInfo has store, drop, copy {
        node_id  : String,
        ip       : String,
        ipfs_cid : String,
        registered_at : u64,
        status   : String,
    }

    /// Threat log entry
    struct ThreatLog has store, drop, copy {
        node_id  : String,
        ipfs_cid : String,
        verdict  : String,
        ts_micro : u64,
    }

    /// Global registry of all nodes
    struct NodeRegistry has key {
        nodes: Table<String, NodeInfo>,
        node_count: u64,
    }

    /// Per-account threat log storage
    struct LogStore has key {
        logs  : vector<ThreatLog>,
        count : u64,
    }

    /// Initialize the global node registry (call once after deployment)
    public entry fun init_registry(account: &signer) {
        let addr = signer::address_of(account);
        if (!exists<NodeRegistry>(addr)) {
            move_to(account, NodeRegistry {
                nodes: table::new(),
                node_count: 0,
            });
        };
    }

    /// Initialize per-account log storage
    public entry fun init_store(account: &signer) {
        move_to(account, LogStore {
            logs  : vector::empty<ThreatLog>(),
            count : 0,
        });
    }

    /// Register a new node on the blockchain
    public entry fun register_node(
        account: &signer,
        node_id: String,
        ip: String,
        ipfs_cid: String,
    ) acquires NodeRegistry {
        let addr = signer::address_of(account);
        let registry = borrow_global_mut<NodeRegistry>(addr);
        
        let node_info = NodeInfo {
            node_id,
            ip,
            ipfs_cid,
            registered_at: timestamp::now_microseconds(),
            status: std::string::utf8(b"online"),
        };
        
        table::add(&mut registry.nodes, node_id, node_info);
        registry.node_count = registry.node_count + 1;
    }

    /// Log a threat detection
    public entry fun log_threat(
        account  : &signer,
        node_id  : String,
        ipfs_cid : String,
        verdict  : String,
    ) acquires LogStore {
        let addr  = signer::address_of(account);
        let store = borrow_global_mut<LogStore>(addr);
        vector::push_back(&mut store.logs, ThreatLog {
            node_id, ipfs_cid, verdict,
            ts_micro: timestamp::now_microseconds(),
        });
        store.count = store.count + 1;
    }

    /// Update node status (online/offline/compromised)
    public entry fun update_node_status(
        account: &signer,
        node_id: String,
        new_status: String,
    ) acquires NodeRegistry {
        let addr = signer::address_of(account);
        let registry = borrow_global_mut<NodeRegistry>(addr);
        
        if (table::contains(&registry.nodes, node_id)) {
            let node = table::borrow_mut(&mut registry.nodes, node_id);
            node.status = new_status;
        };
    }

    // ========== VIEW FUNCTIONS ==========

    #[view]
    public fun get_count(addr: address): u64 acquires LogStore {
        borrow_global<LogStore>(addr).count
    }

    #[view]
    public fun get_node_count(addr: address): u64 acquires NodeRegistry {
        borrow_global<NodeRegistry>(addr).node_count
    }

    #[view]
    public fun get_node_info(addr: address, node_id: String): NodeInfo acquires NodeRegistry {
        let registry = borrow_global<NodeRegistry>(addr);
        *table::borrow(&registry.nodes, node_id)
    }

    #[view]
    public fun node_exists(addr: address, node_id: String): bool acquires NodeRegistry {
        let registry = borrow_global<NodeRegistry>(addr);
        table::contains(&registry.nodes, node_id)
    }
}
