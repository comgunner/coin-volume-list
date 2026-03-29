# Adding New Exchanges to the Coin List Generator

**Last Updated:** March 29, 2026  
**Module:** `exchanges.py`

---

## Overview

This guide explains how to add support for new cryptocurrency exchanges to the coin list generator. The script is designed for **futures/derivatives markets** (USDT-margined swaps), so proper configuration is essential to avoid errors.

---

## Prerequisites

1. **CCXT Support**: The exchange must be supported by the [CCXT library](https://github.com/ccxt/ccxt)
2. **Futures/Swap Markets**: The exchange must offer USDT-margined perpetual swaps or futures
3. **Public API Access**: At least public market data access (authentication optional for higher rate limits)

---

## Step-by-Step Guide

### Step 1: Verify CCXT Support

Check if the exchange is supported by CCXT:

```python
import ccxt

# List all supported exchanges
print(ccxt.exchanges)

# Check specific exchange
if hasattr(ccxt, 'kucoin'):
    print("KuCoin is supported!")
```

### Step 2: Test Futures Markets

Verify the exchange has USDT futures/swaps:

```python
import ccxt

exchange = ccxt.kucoin()  # Replace with your exchange
exchange.load_markets()

# Check for swap/futures markets
swap_markets = [m for m in exchange.markets.values() 
                if m.get('swap') and m.get('quote') == 'USDT']

print(f"Found {len(swap_markets)} USDT swap markets")
```

### Step 3: Edit `exchanges.py`

Open `exchanges.py` and make the following changes:

#### 3.1 Add to `SUPPORTED_EXCHANGES`

```python
SUPPORTED_EXCHANGES = ["binance", "bybit", "bingx", "okx", "bitget", "kucoin"]
#                                                              ^^^^^^ Add here
```

#### 3.2 Add to `CREDENTIALS_MAP`

Add the API credential mapping (even if optional):

```python
CREDENTIALS_MAP = {
    "binance": {"apiKey": "BINANCE_API_KEY", "secret": "BINANCE_API_SECRET"},
    "bybit":   {"apiKey": "BYBIT_API_KEY",   "secret": "BYBIT_API_SECRET"},
    "bingx":   {"apiKey": "BINGX_API_KEY",   "secret": "BINGX_API_SECRET"},
    "okx":     {"apiKey": "OKX_API_KEY",     "secret": "OKX_API_SECRET", "password": "OKX_PASSWORD"},
    "bitget":  {"apiKey": "BITGET_API_KEY",  "secret": "BITGET_API_SECRET", "password": "BITGET_PASSWORD"},
    "kucoin":  {"apiKey": "KUCOIN_API_KEY",  "secret": "KUCOIN_API_SECRET", "password": "KUCOIN_PASSWORD"},
    #          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Add here
}
```

**Note**: Some exchanges require a passphrase (OKX, Bitget, KuCoin).

#### 3.3 Add to `EXCHANGE_TYPE_MAP`

Specify the correct market type for futures:

```python
EXCHANGE_TYPE_MAP = {
    "binance": "future",    # Binance Futures
    "bybit": "linear",      # Bybit Linear (USDT)
    "bingx": "swap",        # BingX Swaps
    "okx": "swap",          # OKX Swaps
    "bitget": "swap",       # Bitget Swaps
    "kucoin": "swap",       # KuCoin Swaps
    #         ^^^^^^ Add here with correct type
}
```

**Common Market Types:**
- `"future"` - Binance-style futures
- `"linear"` - Bybit-style linear contracts (USDT margined)
- `"swap"` - Perpetual swaps (most common)
- `"inverse"` - Inverse contracts (coin-margined, less common)

#### 3.4 Update `build_exchange_config()` (if needed)

Most exchanges work with the default configuration. Add special handling if required:

```python
def build_exchange_config(exchange_id):
    """Build CCXT configuration dictionary for a specific exchange."""
    config = {
        "enableRateLimit": True,
        "options": {"defaultType": "swap"}
    }

    exchange_type = EXCHANGE_TYPE_MAP.get(exchange_id, "swap")
    
    if exchange_id == "binance":
        config["options"]["defaultType"] = "future"
    elif exchange_id == "bybit":
        config["options"]["defaultType"] = "linear"
        config["options"]["adjustForTimeDifference"] = True  # Bybit needs time sync
    elif exchange_id == "kucoin":
        config["options"]["defaultType"] = "swap"
        # Add KuCoin-specific options here if needed
    elif exchange_id in ["bingx", "okx", "bitget"]:
        config["options"]["defaultType"] = exchange_type

    return config
```

### Step 4: Update `.env.example`

Add the new exchange credentials template:

```bash
# KuCoin
KUCOIN_API_KEY=
KUCOIN_API_SECRET=
KUCOIN_PASSWORD=
```

### Step 5: Test the New Exchange

```bash
# Test single exchange
EXCHANGE_CCXT=kucoin python volume_sorted_coin_list.py

# Test with --all-exchanges (includes new exchange)
python volume_sorted_coin_list.py --all-exchanges
```

---

## Common Issues & Solutions

### Issue 1: No Markets Found

**Problem:** Script reports "0 symbols obtained"

**Causes:**
1. Wrong market type configuration
2. Exchange doesn't have USDT futures
3. API endpoint changed

**Solution:**
```python
# Debug: Check what markets are available
import ccxt
exchange = ccxt.kucoin()
exchange.load_markets()

# Print market types
types = set(m.get('type') for m in exchange.markets.values())
print(f"Available market types: {types}")

# Check for USDT markets
usdt_markets = [m for m in exchange.markets.values() if m.get('quote') == 'USDT']
print(f"USDT markets: {len(usdt_markets)}")
```

### Issue 2: Authentication Errors

**Problem:** API errors even with credentials

**Solution:**
1. Verify credential names in `CREDENTIALS_MAP` match `.env` variables
2. Check if exchange requires passphrase
3. Ensure API keys have correct permissions (read-only is enough)

### Issue 3: Rate Limit Errors

**Problem:** "Rate limit exceeded" errors

**Solution:**
```python
# Add custom rate limit settings
if exchange_id == "kucoin":
    config["rateLimit"] = 1000  # Increase delay between requests
    config["enableRateLimit"] = True
```

### Issue 4: Wrong Contract Type

**Problem:** Script fetches spot markets instead of futures

**Solution:**
Verify `EXCHANGE_TYPE_MAP` is correct and `defaultType` is set properly:

```python
# For most USDT futures exchanges:
config["options"]["defaultType"] = "swap"  # or "future" or "linear"
```

---

## Exchange Configuration Reference

### Binance
```python
"binance": {
    "type": "future",
    "credentials": ["apiKey", "secret"],
    "notes": "Uses 'future' for USDⓈ-M futures"
}
```

### Bybit
```python
"bybit": {
    "type": "linear",
    "credentials": ["apiKey", "secret"],
    "notes": "Needs adjustForTimeDifference=True"
}
```

### OKX
```python
"okx": {
    "type": "swap",
    "credentials": ["apiKey", "secret", "password"],
    "notes": "Requires passphrase"
}
```

### Bitget
```python
"bitget": {
    "type": "swap",
    "credentials": ["apiKey", "secret", "password"],
    "notes": "Requires passphrase"
}
```

### BingX
```python
"bingx": {
    "type": "swap",
    "credentials": ["apiKey", "secret"],
    "notes": "Uses standard swap markets"
}
```

### KuCoin (Example)
```python
"kucoin": {
    "type": "swap",
    "credentials": ["apiKey", "secret", "password"],
    "notes": "Requires passphrase for futures"
}
```

---

## Testing Checklist

Before submitting a new exchange, verify:

- [ ] Exchange is supported by CCXT
- [ ] Exchange has USDT-margined futures/swaps
- [ ] `SUPPORTED_EXCHANGES` includes the exchange ID
- [ ] `CREDENTIALS_MAP` has correct credential names
- [ ] `EXCHANGE_TYPE_MAP` has correct market type
- [ ] Script runs without errors: `EXCHANGE_CCXT=xyz python script.py`
- [ ] Output file is generated with valid data
- [ ] Symbols are properly normalized (no dashes, etc.)
- [ ] Volume sorting works correctly

---

## Best Practices

1. **Test Without Credentials First**: Verify public API access works before adding credentials
2. **Use Conservative Rate Limits**: Start with `enableRateLimit=True`
3. **Document Special Requirements**: Add comments for exchanges with unique needs
4. **Keep Market Type Consistent**: Use "swap" for most perpetual futures
5. **Validate in `is_likely_crypto()`**: Ensure new exchange market format passes filters

---

## Example: Adding Gate.io

```python
# 1. Add to SUPPORTED_EXCHANGES
SUPPORTED_EXCHANGES = ["binance", "bybit", "bingx", "okx", "bitget", "gateio"]

# 2. Add to CREDENTIALS_MAP
CREDENTIALS_MAP = {
    # ... existing ...
    "gateio": {"apiKey": "GATEIO_API_KEY", "secret": "GATEIO_API_SECRET"},
}

# 3. Add to EXCHANGE_TYPE_MAP
EXCHANGE_TYPE_MAP = {
    # ... existing ...
    "gateio": "swap",
}

# 4. Test
EXCHANGE_CCXT=gateio python volume_sorted_coin_list.py
```

---

## Troubleshooting

### Exchange Uses Different Naming Convention

Some exchanges use different symbols (e.g., `BTC/USDT:USDT` instead of `BTC/USDT`).

**Solution:** Update `is_likely_crypto()` in `volume_sorted_coin_list.py` if needed.

### Exchange Has Both Spot and Futures

Ensure the script only fetches futures:

**Solution:** Verify `market.get('swap')` or `market.get('future')` check is in place.

### Exchange Requires Specific API Version

**Solution:** Add version configuration:
```python
if exchange_id == "gateio":
    config["options"]["version"] = "2"
```

---

## Additional Resources

- [CCXT Documentation](https://docs.ccxt.com/)
- [CCXT Exchange List](https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets)
- [CCXT Manual](https://github.com/ccxt/ccxt/wiki/Manual)

---

## Related Documentation

- [Symbol Normalization Guide](SYMBOL_NORMALIZATION.md) - How to normalize symbols for new exchanges
- [Symbol Normalization Guide (Spanish)](SYMBOL_NORMALIZATION.es.md) - Guía de normalización en español
- [Adding Exchanges (Spanish)](ADDING_EXCHANGES.es.md) - Esta guía en español
- [exchanges.py](../exchanges.py) - Exchange configuration module

---

**Questions?** Open an issue on GitHub or contact @comgunner
