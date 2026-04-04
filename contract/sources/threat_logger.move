module cybershield_addr::threat_logger {
    use std::signer;
    use std::string::String;
    use std::vector;
    use aptos_framework::timestamp;

    struct ThreatLog has store, drop, copy {
        node_id  : String,
        ipfs_cid : String,
        verdict  : String,
        ts_micro : u64,
    }

    struct LogStore has key {
        logs  : vector<ThreatLog>,
        count : u64,
    }

    /// Call once after deployment to initialize storage
    public entry fun init_store(account: &signer) {
        move_to(account, LogStore {
            logs  : vector::empty<ThreatLog>(),
            count : 0,
        });
    }

    /// Called every time an anomaly is detected — stores node + IPFS CID on-chain
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

    #[view]
    public fun get_count(addr: address): u64 acquires LogStore {
        borrow_global<LogStore>(addr).count
    }
}
