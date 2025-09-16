from src.utils.clients import create_clients
from src.utils.subscriber import setup_subscriber
from src.utils.watermark import setup_logging

# Setup logging
logger = setup_logging()

def main():
    """Main entry point for the application"""
    logger.info("🚀 Starting Enhanced DEX Monitor...")
    logger.info("📡 Monitoring Tinyman & Pact via multiple strategies:")
    logger.info("   • Application call filtering") 
    logger.info("   • Asset transfer filtering")
    logger.info("   • Large ALGO transfer filtering")
    logger.info("   • Transaction note inspection")

    try:
        # Initialize clients
        algod_client, indexer_client = create_clients()
        
        # Test connection
        status = algod_client.status()
        logger.info(f"✅ Connected to MainNet | Current round: {status['last-round']}")
        
        # Setup and start subscriber
        subscriber = setup_subscriber(algod_client, indexer_client)
        subscriber.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
