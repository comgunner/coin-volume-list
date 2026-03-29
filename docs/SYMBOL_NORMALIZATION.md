# Symbol Normalization Guide

**Last Updated:** March 29, 2026  
**Module:** `volume_sorted_coin_list.py`

---

## Overview

Different exchanges use different symbol naming conventions. This guide explains how symbol normalization works and how to fix issues when adding new exchanges.

---

## Exchange Symbol Formats

| Exchange | Format | Example | Normalized |
|----------|--------|---------|------------|
| **Binance** | `BTCUSDT` | `BTCUSDT` | `BTCUSDT` |
| **Bybit** | `BTCUSDT` | `BTCUSDT` | `BTCUSDT` |
| **OKX** | `BTC-USDT-SWAP` | `BTC-USDT-SWAP` | `BTCUSDT` |
| **Bitget** | `BTCUSDT` | `BTCUSDT` | `BTCUSDT` |
| **BingX** | `BTC-USDT` | `BTC-USDT` | `BTCUSDT` |
| **KuCoin** | `XBTUSDTM` | `XBTUSDTM` | `XBTUSDTM` |

---

## Current Normalization Logic

Located in `get_ccxt_symbols_by_volume()` function:

```python
# --- ID NORMALIZATION ---
raw_id = market['id']
clean_id = raw_id

# OKX case: BTC-USDT-SWAP -> BTCUSDT
if clean_id.endswith('-SWAP'):
    clean_id = clean_id.replace('-SWAP', '').replace('-', '')
# BingX case: BTC-USDT -> BTCUSDT
elif '-' in clean_id and clean_id.endswith('-USDT'):
    clean_id = clean_id.replace('-', '')

base_candidates.append(clean_id)
```

---

## Adding Normalization for New Exchanges

### Step 1: Identify the Pattern

Check what format the exchange uses:

```python
import ccxt

exchange = ccxt.kucoin()
exchange.load_markets()

# Print first 10 swap market IDs
swap_markets = [m for m in exchange.markets.values() 
                if m.get('swap') and m.get('quote') == 'USDT']

for m in swap_markets[:10]:
    print(f"ID: {m['id']} | Symbol: {m['symbol']}")
```

### Step 2: Add Normalization Rule

Add the rule in the correct order (most specific first):

```python
# --- ID NORMALIZATION ---
raw_id = market['id']
clean_id = raw_id

# OKX case: BTC-USDT-SWAP -> BTCUSDT
if clean_id.endswith('-SWAP'):
    clean_id = clean_id.replace('-SWAP', '').replace('-', '')

# Gate.io case: BTC_USDT -> BTCUSDT
elif '_' in clean_id and clean_id.endswith('_USDT'):
    clean_id = clean_id.replace('_', '')

# BingX case: BTC-USDT -> BTCUSDT
elif '-' in clean_id and clean_id.endswith('-USDT'):
    clean_id = clean_id.replace('-', '')

# Default: already clean (Binance, Bybit, Bitget)
# clean_id remains unchanged

base_candidates.append(clean_id)
```

---

## Common Patterns & Solutions

### Pattern 1: Underscore Separator

**Exchange:** Gate.io, some others  
**Format:** `BTC_USDT`  
**Solution:**
```python
if '_' in clean_id and clean_id.endswith('_USDT'):
    clean_id = clean_id.replace('_', '')
```

### Pattern 2: Slash Separator

**Exchange:** Some exchanges use `BTC/USDT`  
**Format:** `BTC/USDT`  
**Solution:**
```python
if '/' in clean_id:
    clean_id = clean_id.replace('/', '')
```

### Pattern 3: Suffix Variations

**Exchange:** Some use `PERP` suffix  
**Format:** `BTCUSDT-PERP`  
**Solution:**
```python
if clean_id.endswith('-PERP'):
    clean_id = clean_id.replace('-PERP', '')
```

### Pattern 4: Different Quote Currency

**Exchange:** Some use `USD` instead of `USDT`  
**Format:** `BTCUSD`  
**Solution:** Update the filter logic, not just normalization

---

## Filter Logic

The script filters markets before normalization:

```python
# --- MARKET FILTERS ---
# 1. Contract (Derivative)
if not market.get('contract'):
    continue

# 2. USDT Margin (Linear)
is_linear = market.get('linear', False) is True
is_usdt = market.get('quote') == 'USDT'
is_active = market.get('active', True)

# Additional check for BingX/others where 'linear' may not be explicit
if not is_linear:
    if market.get('type') == 'swap' and market.get('quote') == 'USDT':
        is_linear = True

if not (is_linear and is_usdt and is_active):
    continue
```

### Adding New Filter Conditions

If a new exchange needs special filtering:

```python
# Gate.io example: uses 'settle' field
if exchange_id == "gateio":
    is_usdt = market.get('settle') == 'usdt'
else:
    is_usdt = market.get('quote') == 'USDT'
```

---

## Testing Normalization

### Test Script

```python
import ccxt
from exchanges import create_ccxt_client

# Test with new exchange
exchange_id = "kucoin"
client = create_ccxt_client(exchange_id)

tickers = client.fetch_tickers()

for symbol, ticker in list(tickers.items())[:5]:
    market = client.markets.get(symbol)
    if not market:
        continue
    
    # Apply your normalization logic
    raw_id = market['id']
    clean_id = raw_id
    
    # Add your rules here
    if '-' in raw_id:
        clean_id = raw_id.replace('-', '')
    
    print(f"Raw: {raw_id:20} -> Clean: {clean_id}")
```

### Expected Output

```
Raw: BTC-USDT-SWAP       -> Clean: BTCUSDT
Raw: ETH-USDT-SWAP       -> Clean: ETHUSDT
Raw: SOL-USDT-SWAP       -> Clean: SOLUSDT
```

---

## Common Issues

### Issue 1: Duplicate Symbols

**Problem:** Same coin appears twice after normalization

**Cause:** Different market types normalize to same ID

**Solution:** Use volume-based deduplication (already implemented):
```python
if clean_id not in vol_map:
    final_list.append(clean_id)
    vol_map[clean_id] = quote_vol
```

### Issue 2: Wrong Symbols Included

**Problem:** Non-crypto assets pass through

**Cause:** `is_likely_crypto()` filter not catching new patterns

**Solution:** Update the blocklist in `is_likely_crypto()`:
```python
BLOCKLIST = [
    "ALUMINIUM", "ALUM", "COPPER", "ZINC",  # Metals
    "GOLD", "SILVER", "PLATINUM",           # Precious metals
    "OIL", "GAS", "BRENT", "WTI",           # Energy
    "SPX500", "NAS100", "US30",             # Indices
    "FOREX", "INDEX"                        # Types
]
```

### Issue 3: Symbols Not Normalized

**Problem:** Output file contains dashes or underscores

**Cause:** Normalization rule not matching the pattern

**Solution:** Check the exact format and add correct rule:
```python
# Debug: print raw IDs
print(f"Raw ID sample: {market['id']}")
# Then add matching rule
```

---

## Exchange-Specific Notes

### OKX
- Format: `BTC-USDT-SWAP`
- Rule: Remove `-SWAP` then remove `-`
- Already supported ✓

### BingX
- Format: `BTC-USDT`
- Rule: Remove `-`
- Already supported ✓

### Gate.io
- Format: `BTC_USDT` (underscore)
- Rule: Remove `_`
- **Needs to be added**

### KuCoin
- Format: `XBTUSDTM` (already clean)
- Rule: No normalization needed
- Uses `XBT` instead of `BTC`

### Bybit
- Format: `BTCUSDT` (already clean)
- Rule: No normalization needed
- Already supported ✓

### Binance
- Format: `BTCUSDT` (already clean)
- Rule: No normalization needed
- Already supported ✓

---

## Best Practices

1. **Most Specific First**: Check for `-SWAP` before checking for `-`
2. **Preserve Original**: Always start with `clean_id = raw_id`
3. **Test Extensively**: Verify with multiple symbols from the exchange
4. **Document Changes**: Add comments explaining each rule
5. **Validate Output**: Check generated files for correct formatting

---

## Validation Checklist

After adding normalization for a new exchange:

- [ ] Run script with new exchange
- [ ] Check output file for correct symbol format
- [ ] Verify no dashes/underscores in symbols
- [ ] Confirm volume sorting works
- [ ] Check for duplicate symbols
- [ ] Ensure non-crypto assets are filtered
- [ ] Test with `--output-format toon` for readability
- [ ] Test with `--output-format csv` for clean list

---

## Example: Adding Gate.io Normalization

```python
# In get_ccxt_symbols_by_volume()

# --- ID NORMALIZATION ---
raw_id = market['id']
clean_id = raw_id

# OKX case: BTC-USDT-SWAP -> BTCUSDT
if clean_id.endswith('-SWAP'):
    clean_id = clean_id.replace('-SWAP', '').replace('-', '')

# Gate.io case: BTC_USDT -> BTCUSDT
elif '_' in clean_id and clean_id.endswith('_USDT'):
    clean_id = clean_id.replace('_', '')

# BingX case: BTC-USDT -> BTCUSDT
elif '-' in clean_id and clean_id.endswith('-USDT'):
    clean_id = clean_id.replace('-', '')

base_candidates.append(clean_id)
```

---

**Related Documentation:**
- [Adding Exchanges](ADDING_EXCHANGES.md) - Complete guide for adding new exchanges
- [Adding Exchanges (Spanish)](ADDING_EXCHANGES.es.md) - Guía completa en español
- [Symbol Normalization (Spanish)](SYMBOL_NORMALIZATION.es.md) - Esta guía en español
- [exchanges.py](../exchanges.py) - Exchange configuration module

---

**Related Documentation:**
- [Adding Exchanges Guide](ADDING_EXCHANGES.md) - Complete guide for adding new exchanges
- [Adding Exchanges Guide (Spanish)](ADDING_EXCHANGES.es.md) - Guía completa en español
- [exchanges.py](../exchanges.py) - Exchange configuration module
- [README.md](../README.md) - Main documentation
- [README.es.md](../README.es.md) - Documentación principal en español

---

**Questions?** Contact @comgunner on GitHub
