"""
Utility functions for the Algorand DEX Monitor
"""

import logging

logger = logging.getLogger(__name__)

# Watermark tracking to maintain monitoring state
watermark = 0

def get_watermark() -> int:
    """Get the current watermark value"""
    return watermark

def set_watermark(new_watermark: int) -> None:
    """Update the watermark value and log milestones"""
    global watermark  
    watermark = new_watermark
    if new_watermark % 100 == 0:
        logger.info(f"📍 Processed through round {new_watermark}")

def setup_logging():
    """Configure the logger for the application"""
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(message)s'
    )
    return logging.getLogger(__name__)
