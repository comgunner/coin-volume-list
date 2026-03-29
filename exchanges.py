#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exchange Configuration and CCXT Client Manager

This module handles exchange configuration, credentials management,
and CCXT client initialization for the coin list generator.
"""

import os

import ccxt

# -------------------------------------------------
# EXCHANGE CONFIGURATION
# -------------------------------------------------

# Supported exchanges list
SUPPORTED_EXCHANGES = ["binance", "bybit", "bingx", "okx", "bitget"]

# Credentials environment variable mapping
CREDENTIALS_MAP = {
    "binance": {"apiKey": "BINANCE_API_KEY", "secret": "BINANCE_API_SECRET"},
    "bybit": {"apiKey": "BYBIT_API_KEY", "secret": "BYBIT_API_SECRET"},
    "bingx": {"apiKey": "BINGX_API_KEY", "secret": "BINGX_API_SECRET"},
    "okx": {
        "apiKey": "OKX_API_KEY",
        "secret": "OKX_API_SECRET",
        "password": "OKX_PASSWORD",
    },
    "bitget": {
        "apiKey": "BITGET_API_KEY",
        "secret": "BITGET_API_SECRET",
        "password": "BITGET_PASSWORD",
    },
}

# Exchange-specific type configurations
EXCHANGE_TYPE_MAP = {
    "binance": "future",
    "bybit": "linear",
    "bingx": "swap",
    "okx": "swap",
    "bitget": "swap",
}


# -------------------------------------------------
# CCXT CLIENT FUNCTIONS
# -------------------------------------------------


def create_ccxt_client(exchange_id=None):
    """Create CCXT client based on .env configuration (EXCHANGE_CCXT) or provided exchange_id.

    Args:
        exchange_id: Exchange identifier (binance, bybit, etc.) or None to use .env

    Returns:
        ccxt.Exchange: Configured CCXT exchange client, or None if initialization fails

    """
    if exchange_id is None:
        exchange_id = os.getenv("EXCHANGE_CCXT", "binance").strip().lower()

    print(f"[CCXT] Configuring client for: {exchange_id.upper()}...")

    try:
        # Validate exchange is supported by CCXT
        if not hasattr(ccxt, exchange_id):
            raise ValueError(f"Exchange '{exchange_id}' not supported by CCXT.")

        exchange_class = getattr(ccxt, exchange_id)

        # Build configuration
        config = build_exchange_config(exchange_id)

        # Load credentials if available
        load_credentials(config, exchange_id)

        # Initialize client
        client = exchange_class(config)

        # Load markets
        print(f"[CCXT] Loading markets for {exchange_id.upper()}...")
        client.load_markets()
        print(f"[CCXT] Markets loaded: {len(client.markets)}")

        return client
    except Exception as e:
        print(f"[ERROR] Error initializing CCXT: {e}")
        return None


def build_exchange_config(exchange_id):
    """Build CCXT configuration dictionary for a specific exchange.

    Args:
        exchange_id: Exchange identifier (binance, bybit, etc.)

    Returns:
        dict: CCXT configuration dictionary

    """
    # Common configuration
    config = {"enableRateLimit": True, "options": {"defaultType": "swap"}}

    # Exchange-specific adjustments
    exchange_type = EXCHANGE_TYPE_MAP.get(exchange_id, "swap")

    if exchange_id == "binance":
        config["options"]["defaultType"] = "future"
    elif exchange_id == "bybit":
        config["options"]["defaultType"] = "linear"
        config["options"]["adjustForTimeDifference"] = True
    elif exchange_id in ["bingx", "okx", "bitget"]:
        config["options"]["defaultType"] = exchange_type

    return config


def load_credentials(config, exchange_id):
    """Load API credentials from environment variables for a specific exchange.

    Args:
        config: CCXT configuration dictionary (modified in place)
        exchange_id: Exchange identifier (binance, bybit, etc.)

    """
    creds_keys = CREDENTIALS_MAP.get(exchange_id, {})
    api_key = os.getenv(creds_keys.get("apiKey", ""), "").strip()
    secret = os.getenv(creds_keys.get("secret", ""), "").strip()
    password = os.getenv(creds_keys.get("password", ""), "").strip()

    if api_key and secret:
        config["apiKey"] = api_key
        config["secret"] = secret
        if password:
            config["password"] = password
        print(f"[CCXT] Credentials loaded for {exchange_id.upper()}")
    else:
        print(f"[CCXT] {exchange_id.upper()} without credentials (public read-only)")


def get_exchange_display_name(exchange_id):
    """Get human-readable display name for an exchange.

    Args:
        exchange_id: Exchange identifier (binance, bybit, etc.)

    Returns:
        str: Display name in uppercase

    """
    return exchange_id.upper()


def is_exchange_supported(exchange_id):
    """Check if an exchange is supported.

    Args:
        exchange_id: Exchange identifier to check

    Returns:
        bool: True if exchange is supported, False otherwise

    """
    return exchange_id in SUPPORTED_EXCHANGES


def get_all_supported_exchanges():
    """Get list of all supported exchanges.

    Returns:
        list: List of supported exchange identifiers

    """
    return SUPPORTED_EXCHANGES.copy()


def get_credentials_for_exchange(exchange_id):
    """Get the credential keys required for a specific exchange.

    Args:
        exchange_id: Exchange identifier (binance, bybit, etc.)

    Returns:
        dict: Dictionary with credential key names

    """
    return CREDENTIALS_MAP.get(exchange_id, {}).copy()
