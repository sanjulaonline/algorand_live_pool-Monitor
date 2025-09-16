# Algorand DEX Transaction Monitor

A real-time monitoring tool for tracking Tinyman and Pact transactions on the Algorand blockchain.

## Project Structure

```
algorand_pool_monitor/
├── main.py               # Main entry point
├── src/                  # Source code
│   ├── config/           # Configuration settings
│   │   ├── __init__.py
│   │   └── settings.py   # Constants and filter configurations
│   ├── handlers/         # Transaction handlers
│   │   ├── __init__.py
│   │   └── transaction_handlers.py  # Handler functions for each filter
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   ├── clients.py    # Algorand client initialization
│   │   ├── subscriber.py # Subscriber setup and registration
│   │   └── watermark.py  # Progress tracking
│   └── __init__.py
└── README.md
```

## Features

- Multi-strategy monitoring of Algorand DEX transactions
- Application call filtering for Tinyman and Pact
- Asset transfer tracking for major trading pairs
- Large ALGO transfer detection
- Note field content analysis
- Transaction statistics collection

## Setup

1. Ensure Python 3.10+ is installed
2. Install dependencies:
   ```
   pip install algokit-subscriber algosdk
   ```
3. Run the monitor:
   ```
   python main.py
   ```

## How It Works

The application uses `algokit_subscriber` to monitor the Algorand blockchain in real-time. It applies multiple filtering strategies to identify DEX-related transactions:

1. **Application Calls**: Monitors specific app IDs for Tinyman and Pact
2. **Asset Transfers**: Tracks significant transfers of major assets (USDC, USDT, etc.)
3. **ALGO Transfers**: Detects large ALGO movements
4. **Transaction Notes**: Analyzes note fields for DEX-related information

## Extending

To add support for additional DEXes or monitoring strategies:

1. Add new filter definitions in `src/config/settings.py`
2. Create handler functions in `src/handlers/transaction_handlers.py`
3. Register handlers in `src/utils/subscriber.py`
