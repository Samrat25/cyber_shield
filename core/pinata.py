# core/pinata.py
import os, json, requests, datetime
from dotenv import load_dotenv

load_dotenv()
JWT  = os.getenv("PINATA_JWT", "")
BASE = "https://api.pinata.cloud"

def _h():
    return {"Authorization": f"Bearer {JWT}", "Content-Type": "application/json"}

def pin_json(data: dict, name: str = "cybershield") -> str:
    payload = {
        "pinataContent" : {**data, "pinned_at": datetime.datetime.now(datetime.UTC).isoformat()},
        "pinataMetadata": {"name": name}
    }
    r = requests.post(f"{BASE}/pinning/pinJSONToIPFS", headers=_h(), json=payload, timeout=20)
    r.raise_for_status()
    return r.json()["IpfsHash"]

def gateway_url(cid: str) -> str:
    return f"https://gateway.pinata.cloud/ipfs/{cid}"
