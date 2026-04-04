# cybershield/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directories
BASE_DIR = Path.home() / ".cybershield"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Create directories
for dir_path in [BASE_DIR, DATA_DIR, MODELS_DIR, LOGS_DIR, CONFIG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Blockchain Configuration
APTOS_NETWORK = os.getenv("APTOS_NETWORK", "testnet")
APTOS_NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
APTOS_PRIVATE_KEY = os.getenv("APTOS_PRIVATE_KEY", "").replace("0xed25519-priv-", "")
APTOS_ADDRESS = os.getenv("APTOS_ADDRESS", "")

# IPFS Configuration
PINATA_JWT = os.getenv("PINATA_JWT", "")

# P2P Network Configuration
P2P_PORT = int(os.getenv("P2P_PORT", "8765"))
P2P_HOST = os.getenv("P2P_HOST", "0.0.0.0")
BOOTSTRAP_NODES = os.getenv("BOOTSTRAP_NODES", "").split(",") if os.getenv("BOOTSTRAP_NODES") else []

# ML Configuration
ML_CHECK_INTERVAL = int(os.getenv("ML_CHECK_INTERVAL", "5"))  # seconds
ML_MODELS = ["isolation_forest", "autoencoder", "lstm", "xgboost"]
ML_ENSEMBLE_THRESHOLD = float(os.getenv("ML_ENSEMBLE_THRESHOLD", "0.6"))

# Monitoring Configuration
METRICS_HISTORY_SIZE = int(os.getenv("METRICS_HISTORY_SIZE", "100"))
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))  # seconds
