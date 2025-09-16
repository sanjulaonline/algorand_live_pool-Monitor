"""
Handlers for different types of Algorand transactions
"""

from algokit_subscriber import SubscribedTransaction
import logging

logger = logging.getLogger(__name__)

def handle_tinyman_app(txn: SubscribedTransaction, _: str) -> None:
    """Handle Tinyman application calls"""
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
    """Handle Pact application calls"""
    app_id = txn.get('application-transaction', {}).get('application-id', 0) 
    logger.info(f"🔷 PACT APP CALL: {txn['sender'][:8]}... | App: {app_id}")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_asset_transfer(txn: SubscribedTransaction, _: str) -> None:
    """Handle asset transfers for tracked assets"""
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
    """Handle large ALGO transfers"""
    payment = txn.get('payment-transaction', {})
    amount = payment.get('amount', 0) 
    receiver = payment.get('receiver', '')
    algo_amount = amount / 1_000_000

    logger.info(f"💰 ALGO TRANSFER: {txn['sender'][:8]}... → {receiver[:8]}...")
    logger.info(f"   Amount: {algo_amount:.6f} ALGO")
    logger.info(f"   TX: {txn['id']} | Round: {txn['confirmed-round']}")

def handle_noted_transaction(txn: SubscribedTransaction, _: str) -> None:
    """Process transaction notes looking for DEX-related information"""
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

# Statistics tracking
transaction_count = 0
def track_stats(txn: SubscribedTransaction, _: str) -> None:
    """Track and log transaction statistics"""
    global transaction_count
    transaction_count += 1
    if transaction_count % 20 == 0:
        logger.info(f"📊 Processed {transaction_count} relevant transactions")
