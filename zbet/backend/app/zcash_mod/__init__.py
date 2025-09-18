import os

# Zcash configuration - supports both mainnet and testnet
ZCASH_RPC_USER = os.getenv("ZCASH_RPC_USER", "fortunethedev")
ZCASH_RPC_PASSWORD = os.getenv("ZCASH_RPC_PASSWORD", "D@t4knid9")

# Network configuration
USE_TESTNET = os.getenv("ZCASH_USE_TESTNET", "true").lower() == "true"

if USE_TESTNET:
    # Testnet configuration - using real public testnet RPC
    ZCASH_RPC_URL = os.getenv("ZCASH_RPC_URL", "http://zcash.mysideoftheweb.com:19067/")
    NETWORK = "testnet"
else:
    # Mainnet configuration (port 8232)
    ZCASH_RPC_URL = os.getenv("ZCASH_RPC_URL", "http://127.0.0.1:8232/")
    NETWORK = "mainnet"

# Alternative hosted nodes to try:
# Public testnet nodes are rare 
# Check on https://hosh.zec.rocks/zec for  nodes
# - Public testnet: http://zcash.mysideoftheweb.com:19067/
# - Public mainnet: htestnet.zec.rocks:443 
# - Local testnet: http://127.0.0.1:18232/
# - Local mainnet: http://127.0.0.1:8232/

# 
# For development, we use enhanced mock data that looks realistic 