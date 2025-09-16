
"""
Enhanced DEX Transaction Monitor for Algorand
Monitors Tinyman and Pact transactions using multiple filter strategies
"""

from algokit_subscriber import AlgorandSubscriber, SubscribedTransaction
from algosdk.v2client import algod, indexer
import logging

# Setup logging  
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Algorand client (MainNet)
algorand = algod.AlgodClient("", "https://mainnet-api.algonode.cloud")
indexer_client = indexer.IndexerClient("", "https://mainnet-idx.algonode.cloud")

# Watermark for tracking progress
watermark = 0
def get_watermark() -> int:
    return watermark

def set_watermark(new_watermark: int) -> None:
    global watermark  
    watermark = new_watermark
    if new_watermark % 100 == 0:
        logger.info(f"📍 Processed through round {new_watermark}")

# Enhanced DEX monitoring with multiple filter strategies
subscriber = AlgorandSubscriber(
    algod_client=algorand,
    indexer_client=indexer_client,  # Add indexer for better performance
    config={
        "filters": [
            # Strategy 2: Application call filtering (most effective)
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

            # Strategy 3: Asset transfer filtering for major trading pairs
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

            # Strategy 4: Large ALGO transfers (potential swaps)
            {
                "name": "algo_transfers",
                "filter": {
                    "type": "pay", 
                    "min_amount": 10000000  # 10+ ALGO
                }
            },

            # Strategy 5: Catch-all for any transaction
            {
                "name": "all_transactions",
                "filter": {}  # Empty filter to catch all transactions
            }
        ],
        "wait_for_block_when_at_tip": True,
        "sync_behaviour": "skip-sync-newest",  # Start from current tip
        "max_rounds_to_sync": 50,
        "watermark_persistence": {
            "get": get_watermark,
            "set": set_watermark
        },
    },
)

# Enhanced handlers with better analysis
def handle_tinyman_note(txn: SubscribedTransaction, _: str) -> None:
    note = txn.get('note', b'')
    if isinstance(note, bytes):
        note = note.decode('utf-8', errors='replace')
    logger.info(f"🔸 TINYMAN NOTE: {txn['sender'][:8]}... | {note[:50]}...")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_pact_note(txn: SubscribedTransaction, _: str) -> None:
    note = txn.get('note', b'')
    if isinstance(note, bytes):
        note = note.decode('utf-8', errors='replace')
    logger.info(f"🔸 PACT NOTE: {txn['sender'][:8]}... | {note[:50]}...")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_tinyman_app(txn: SubscribedTransaction, _: str) -> None:
    app_id = txn.get('application-transaction', {}).get('application-id', 0)
    on_complete = txn.get('application-transaction', {}).get('on-completion', 'noop')
    args = txn.get('application-transaction', {}).get('application-args', [])

    logger.info(f"🔷 TINYMAN APP CALL: {txn['sender'][:8]}...")
    logger.info(f"   App: {app_id} | Action: {on_complete} | Args: {len(args)}")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

    # Check for inner transactions (common in DEX operations)
    inner_txns = txn.get('inner-txns', [])
    if inner_txns:
        logger.info(f"   📎 {len(inner_txns)} inner transactions")

def handle_pact_app(txn: SubscribedTransaction, _: str) -> None:
    app_id = txn.get('application-transaction', {}).get('application-id', 0) 
    logger.info(f"🔷 PACT APP CALL: {txn['sender'][:8]}... | App: {app_id}")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_asset_transfer(txn: SubscribedTransaction, _: str) -> None:
    asset_transfer = txn.get('asset-transfer-transaction', {})
    asset_id = asset_transfer.get('asset-id', 0)
    amount = asset_transfer.get('amount', 0)
    receiver = asset_transfer.get('receiver', '')

    # Map common assets
    asset_names = {
        31566704: 'USDC',
        312769: 'USDT', 
        386192725: 'goBTC',
        386195940: 'goETH'
    }
    asset_name = asset_names.get(asset_id, f'ASA-{asset_id}')

    logger.info(f"🪙 ASSET TRANSFER: {txn['sender'][:8]}... → {receiver[:8]}...")
    logger.info(f"   Asset: {asset_name} | Amount: {amount}")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_algo_transfer(txn: SubscribedTransaction, _: str) -> None:
    payment = txn.get('payment-transaction', {})
    amount = payment.get('amount', 0) 
    receiver = payment.get('receiver', '')
    algo_amount = amount / 1_000_000

    logger.info(f"💰 ALGO TRANSFER: {txn['sender'][:8]}... → {receiver[:8]}...")
    logger.info(f"   Amount: {algo_amount:.6f} ALGO")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_noted_transaction(txn: SubscribedTransaction, _: str) -> None:
    # Get the note and safely decode it
    note_bytes = txn.get('note', b'')
    if not note_bytes:
        return
        
    # Try to decode the note safely
    try:
        note = note_bytes.decode('utf-8', errors='replace')
        tx_type = txn.get('tx-type', 'unknown')
        
        # Check for Tinyman notes
        if 'tinyman' in note.lower():
            logger.info(f"🔸 TINYMAN NOTE: {txn['sender'][:8]}... | {note[:50]}...")
            logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")
            return
            
        # Check for Pact notes
        if 'pact' in note.lower():
            logger.info(f"🔸 PACT NOTE: {txn['sender'][:8]}... | {note[:50]}...")
            logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")
            return
            
        # Log other transactions with notes
        if len(note.strip()) > 0:
            logger.info(f"📝 TRANSACTION WITH NOTE ({tx_type.upper()}): {txn['sender'][:8]}...")
            logger.info(f"   Note: {note[:100]}...")
            logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")
    except Exception as e:
        # Just silently skip transactions with notes we can't decode
        pass

# Register all handlers
subscriber.on("tinyman_app_calls", handle_tinyman_app)
subscriber.on("pact_app_calls", handle_pact_app)
subscriber.on("major_asset_transfers", handle_asset_transfer)
subscriber.on("algo_transfers", handle_algo_transfer)
subscriber.on("all_transactions", handle_noted_transaction)

# Add general statistics tracking
transaction_count = 0
def track_stats(txn: SubscribedTransaction, _: str) -> None:
    global transaction_count
    transaction_count += 1
    if transaction_count % 20 == 0:
        logger.info(f"📊 Processed {transaction_count} relevant transactions")

# Register stats tracking for one of the filters
subscriber.on("all_transactions", track_stats)

if __name__ == "__main__":
    logger.info("🚀 Starting Enhanced DEX Monitor...")
    logger.info("📡 Monitoring Tinyman & Pact via multiple strategies:")
    logger.info("   • Application call filtering") 
    logger.info("   • Asset transfer filtering")
    logger.info("   • Large ALGO transfer filtering")
    logger.info("   • Transaction note inspection")

    try:
        # Test connection first
        status = algorand.status()
        logger.info(f"✅ Connected to MainNet | Current round: {status['last-round']}")

        # Start the subscriber
        subscriber.start()

    except KeyboardInterrupt:
        logger.info("⏹️ Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
