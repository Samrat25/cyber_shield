# cybershield/storage/ipfs.py
import requests
import datetime
from ..config import PINATA_JWT


class IPFSClient:
    """Client for IPFS storage via Pinata."""
    
    def __init__(self):
        self.jwt = PINATA_JWT
        self.base_url = "https://api.pinata.cloud"
    
    def _headers(self):
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.jwt}",
            "Content-Type": "application/json"
        }
    
    def pin_json(self, data: dict, name: str = "cybershield") -> str:
        """Pin JSON data to IPFS."""
        payload = {
            "pinataContent": {
                **data,
                "pinned_at": datetime.datetime.now(datetime.UTC).isoformat()
            },
            "pinataMetadata": {"name": name}
        }
        
        response = requests.post(
            f"{self.base_url}/pinning/pinJSONToIPFS",
            headers=self._headers(),
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        
        return response.json()["IpfsHash"]
    
    def gateway_url(self, cid: str) -> str:
        """Get gateway URL for CID."""
        return f"https://gateway.pinata.cloud/ipfs/{cid}"
