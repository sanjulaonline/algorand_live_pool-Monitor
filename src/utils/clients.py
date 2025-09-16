"""
Algorand client initialization
"""

from algosdk.v2client import algod, indexer
from src.config.settings import MAINNET_ALGOD_URL, MAINNET_INDEXER_URL

def create_clients():
    """Create and return Algorand API clients"""
    # No token required for public nodes
    algod_token = ""
    indexer_token = ""
    
    # Create clients
    algod_client = algod.AlgodClient(algod_token, MAINNET_ALGOD_URL)
    indexer_client = indexer.IndexerClient(indexer_token, MAINNET_INDEXER_URL)
    
    return algod_client, indexer_client
