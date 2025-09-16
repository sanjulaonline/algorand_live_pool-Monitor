
"""
Live Algorand Pool Transaction Monitoring using AlgoKit Subscriber

This script demonstrates how to monitor pool transactions on Algorand DEXs like 
Tinyman, Pact, and AlgoFi using the AlgoKit Subscriber library.
"""

from algokit_subscriber import AlgorandSubscriber
from algosdk.v2client import algod, indexer
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlgorandPoolMonitor:
    def __init__(self, algod_client, indexer_client=None):
        self.algod = algod_client
        self.indexer = indexer_client
        self.watermark = 0

        # Major DEX App IDs (MainNet)
        self.dex_app_ids = {
            'tinyman_v2': 1002541853,  # Tinyman V2
            'pact': 463363983,         # Pact.fi (example)
            'algofi': 605753404,       # AlgoFi (example)
        }

        # Common pool-related assets
        self.major_assets = {
            'USDC': 31566704,
            'USDT': 312769,
            'ALGO': 0,  # Native ALGO
        }

    def create_pool_filters(self):
        """Create filters for pool transactions"""
        filters = [
            # Swap-in of ASA (asset transfer)
            {
                'name': 'swap_in',
                'filter': {
                    'type': 'axfer',
                    'min_amount': 1000,
                    'asset_id': list(self.major_assets.values())
                }
            },
            # ALGO-for-ASA swap (payment)
            {
                'name': 'algo_swap',
                'filter': {
                    'type': 'pay',
                    'min_amount': 1_000_000    # 1 ALGO
                }
            },
            # DEX application calls
            *[
                {
                    'name': f'{dex}_interaction',
                    'filter': {
                        'type': 'appl',
                        'app_id': app_id,
                        'app_on_complete': ['noop', 'optin']
                    }
                }
                for dex, app_id in self.dex_app_ids.items()
            ],
            # Note-based pool operations
            {
                'name': 'tinyman_operation',
                'filter': { 'note_prefix': 'tinyman' }
            },
            {
                'name': 'pact_operation',
                'filter': { 'note_prefix': 'pact' }
            },
            # Pool-token transfers
            {
                'name': 'pool_token_transfer',
                'filter': {
                    'type': 'axfer',
                    'min_amount': 1
                }
            }
        ]
        return filters

    def setup_subscriber(self):
        """Setup the AlgorandSubscriber with pool monitoring filters"""

        config = {
            'filters': self.create_pool_filters(),
            'sync_behaviour': 'skip-sync-newest',  # Start from current tip
            'wait_for_block_when_at_tip': True,    # Low latency monitoring
            'frequency_in_seconds': 2,             # Poll every 2 seconds when catching up
            'max_rounds_to_sync': 100,             # Process max 100 rounds at once
            'watermark_persistence': {
                'get': lambda: self.watermark,
                'set': lambda w: setattr(self, 'watermark', w)
            }
        }

        # Add indexer for fast catchup if available
        if self.indexer:
            config['sync_behaviour'] = 'catchup-with-indexer'

        return AlgorandSubscriber(config, self.algod, self.indexer)

    def handle_swap_transaction(self, transaction):
        """Handle detected swap transactions"""
        tx_type = transaction.get('tx-type')

        if tx_type == 'axfer':
            asset_id = transaction.get('asset-transfer-transaction', {}).get('asset-id', 0)
            amount = transaction.get('asset-transfer-transaction', {}).get('amount', 0)
            sender = transaction.get('sender', '')
            receiver = transaction.get('asset-transfer-transaction', {}).get('receiver', '')

            asset_name = self.get_asset_name(asset_id)
            amount_display = self.format_amount(amount, asset_id)

            logger.info(f"🔄 SWAP: {sender[:8]}... → {receiver[:8]}...")
            logger.info(f"   Asset: {asset_name} ({asset_id})")
            logger.info(f"   Amount: {amount_display}")
            logger.info(f"   Tx ID: {transaction['id']}")

        elif tx_type == 'pay':
            amount = transaction.get('payment-transaction', {}).get('amount', 0)
            sender = transaction.get('sender', '')
            receiver = transaction.get('payment-transaction', {}).get('receiver', '')

            algo_amount = amount / 1_000_000  # Convert microAlgos to Algos

            logger.info(f"💰 ALGO SWAP: {sender[:8]}... → {receiver[:8]}...")
            logger.info(f"   Amount: {algo_amount:.6f} ALGO")
            logger.info(f"   Tx ID: {transaction['id']}")

    def handle_dex_interaction(self, transaction):
        """Handle DEX smart contract interactions"""
        app_id = transaction.get('application-transaction', {}).get('application-id', 0)
        sender = transaction.get('sender', '')

        dex_name = 'Unknown'
        for name, id in self.dex_app_ids.items():
            if id == app_id:
                dex_name = name.upper()
                break

        logger.info(f"🏪 DEX INTERACTION: {dex_name}")
        logger.info(f"   User: {sender[:8]}...")
        logger.info(f"   App ID: {app_id}")
        logger.info(f"   Tx ID: {transaction['id']}")

        # Extract additional details from app call
        app_args = transaction.get('application-transaction', {}).get('application-args', [])
        if app_args:
            logger.info(f"   Method: {app_args[0] if app_args else 'Unknown'}")

    def handle_pool_operation(self, transaction):
        """Handle pool-specific operations identified by note prefix"""
        note = transaction.get('note', b'').decode('utf-8', errors='ignore')
        sender = transaction.get('sender', '')

        logger.info(f"🏊 POOL OPERATION")
        logger.info(f"   User: {sender[:8]}...")
        logger.info(f"   Note: {note[:50]}...")
        logger.info(f"   Tx ID: {transaction['id']}")

    def get_asset_name(self, asset_id):
        """Get human-readable asset name"""
        for name, id in self.major_assets.items():
            if id == asset_id:
                return name
        return f"ASA-{asset_id}"

    def format_amount(self, amount, asset_id):
        """Format amount based on asset decimals"""
        if asset_id == 31566704:  # USDC
            return f"{amount / 1_000_000:.6f}"
        elif asset_id == 312769:  # USDT
            return f"{amount / 1_000_000:.6f}"
        else:
            return str(amount)

    def start_monitoring(self):
        """Start the pool monitoring process"""
        logger.info("🚀 Starting Algorand Pool Transaction Monitor...")
        logger.info(f"Monitoring DEXs: {list(self.dex_app_ids.keys())}")
        logger.info(f"Watching assets: {list(self.major_assets.keys())}")

        subscriber = self.setup_subscriber()

        # Register event handlers
        subscriber.on('swap_in', self.handle_swap_transaction)
        subscriber.on('algo_swap', self.handle_swap_transaction)

        for dex_name in self.dex_app_ids.keys():
            subscriber.on(f'{dex_name}_interaction', self.handle_dex_interaction)

        subscriber.on('tinyman_operation', self.handle_pool_operation)
        subscriber.on('pact_operation', self.handle_pool_operation)
        subscriber.on('pool_token_transfer', self.handle_swap_transaction)

        # Start monitoring
        try:
            subscriber.start()
        except KeyboardInterrupt:
            logger.info("⏹️  Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Error during monitoring: {e}")

# Example usage
def main():
    """Main function to start pool monitoring"""

    # Configure Algorand clients
    # For MainNet monitoring
    algod_token = "your-algod-token-here"  # From AlgoNode, PureStake, etc.
    algod_server = "https://mainnet-api.algonode.cloud"
    indexer_server = "https://mainnet-idx.algonode.cloud"

    # Create clients
    algod_client = algod.AlgodClient(algod_token, algod_server)
    indexer_client = indexer.IndexerClient("", indexer_server)

    # Create and start monitor
    monitor = AlgorandPoolMonitor(algod_client, indexer_client)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
