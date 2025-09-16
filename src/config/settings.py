"""
Configuration settings for the Algorand DEX Monitor
"""

# Algorand client endpoints
MAINNET_ALGOD_URL = "https://mainnet-api.algonode.cloud"
MAINNET_INDEXER_URL = "https://mainnet-idx.algonode.cloud"

# Filter configurations
FILTERS = [
    # Application call filtering for DEXes
    {
        "name": "tinyman_app_calls",
        "filter": {
            "type": "appl",
            "app_id": [
                1002541853,  # Tinyman V2 main contract
                350338509,   # Tinyman V1.1 (legacy)
            ]
        }
    },
    {
        "name": "pact_app_calls",
        "filter": {
            "type": "appl", 
            "app_id": [
                # Note: Pact uses multiple app IDs for different pools
                # You'll need to research current Pact app IDs
                # These are examples - check Pact documentation
            ]
        }
    },

    # Asset transfer filtering for major trading pairs
    {
        "name": "major_asset_transfers",
        "filter": {
            "type": "axfer",
            "asset_id": [
                31566704,   # USDC
                312769,     # USDT  
                386192725,  # goBTC
                386195940,  # goETH
            ],
            "min_amount": 1000000  # Filter for significant amounts
        }
    },

    # Large ALGO transfers (potential swaps)
    {
        "name": "algo_transfers",
        "filter": {
            "type": "pay", 
            "min_amount": 10000000  # 10+ ALGO
        }
    },

    # Catch-all for any transaction
    {
        "name": "all_transactions",
        "filter": {}  # Empty filter to catch all transactions
    }
]

# Subscriber configuration
SUBSCRIBER_CONFIG = {
    "filters": FILTERS,
    "wait_for_block_when_at_tip": True,
    "sync_behaviour": "skip-sync-newest",  # Start from current tip
    "max_rounds_to_sync": 50,
}

# Asset lookup table
ASSET_NAMES = {
    31566704: 'USDC',
    312769: 'USDT', 
    386192725: 'goBTC',
    386195940: 'goETH'
}
