"""
Subscriber setup and configuration
"""

from algokit_subscriber import AlgorandSubscriber
from src.config.settings import SUBSCRIBER_CONFIG
from src.utils.watermark import get_watermark, set_watermark
from src.handlers.transaction_handlers import (
    handle_tinyman_app,
    handle_pact_app,
    handle_asset_transfer,
    handle_algo_transfer,
    handle_noted_transaction,
    track_stats
)

def setup_subscriber(algod_client, indexer_client):
    """Configure and return the AlgorandSubscriber"""
    
    # Create config with watermark persistence
    config = SUBSCRIBER_CONFIG.copy()
    config["watermark_persistence"] = {
        "get": get_watermark,
        "set": set_watermark
    }
    
    # Create subscriber
    subscriber = AlgorandSubscriber(
        algod_client=algod_client,
        indexer_client=indexer_client,
        config=config
    )
    
    # Register handlers
    subscriber.on("tinyman_app_calls", handle_tinyman_app)
    subscriber.on("pact_app_calls", handle_pact_app)
    subscriber.on("major_asset_transfers", handle_asset_transfer)
    subscriber.on("algo_transfers", handle_algo_transfer)
    subscriber.on("all_transactions", handle_noted_transaction)
    
    # Register statistics handler
    subscriber.on("all_transactions", track_stats)
    
    return subscriber
