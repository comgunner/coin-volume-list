# 📊 Volume Sorted Coin List Generator

**Author:** @comgunner  
**Version:** v0.0.1  
**License:** Attribution License (see [LICENSE](LICENSE))

> **💡 What is this?** This script helps you get **active cryptocurrency coins in futures/spot markets** in a simple way. If you want to know which coins are currently active on an exchange, this tool fetches the data automatically and generates a ranked list by trading volume.

**Quick Download:** [📦 Download v0.0.1 Release (ZIP)](https://github.com/comgunner/coin-volume-list/releases/download/v0.0.1/coin-volume-list-v0.0.1.zip)

Cryptocurrency coin list generator that fetches active trading pairs from multiple exchanges using **CCXT** and generates sorted lists based on **24-hour trading volume**.

---

## 🚀 Features

- ✅ **Multi-Exchange Support:** Binance, Bybit, BingX, OKX, Bitget
- ✅ **Volume-Based Ranking:** Sorted by 24h quote volume (USDT)
- ✅ **Smart Filtering:**
  - Automatic exclusion of non-crypto assets (Forex, Commodities, Indices)
  - Manual exclusion list support (`exclude_coins.txt`)
  - USDT linear contracts only
  - Active markets filter
- ✅ **Rate Limit Handling:** Built-in via CCXT
- ✅ **JSON Output:** Structured data with metadata
- ✅ **Timezone Support:** America/Mexico City (CDMX)
- ✅ **Flexible Execution:** Single exchange or all at once

---

## 📋 Requirements

- Python 3.8+
- CCXT library
- Environment variables configured

---

## 🛠️ Installation

### 1. Clone or Download

```bash
cd coin-volume-list
```

### 2. Setup Virtual Environment

#### Linux / macOS

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify Python version
python -V

# Upgrade pip
python -m pip install -U pip
```

#### Windows (10/11)

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Verify Python version
python -V

# Upgrade pip
python -m pip install -U pip
```

### 3. Install Dependencies

```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Install requirements
pip install -r requirements.txt
```

**Dependencies:**
- `ccxt>=4.4.0` - Cryptocurrency exchange library
- `python-dotenv>=1.0.0` - Environment variable management
- `pytz>=2024.1` - Timezone support

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your configuration
# Linux/macOS: Use nano, vim, or any text editor
nano .env

# Windows: Use Notepad or any text editor
notepad .env
```

**.env Configuration:**

```bash
# Exchange selection (binance, bybit, bingx, okx, bitget)
EXCHANGE_CCXT=binance

# Optional: API credentials for higher rate limits
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_secret
```

---

## 📖 Usage

### Single Exchange (from .env)

```bash
# Default JSON output
python3 volume_sorted_coin_list.py

# Simple symbol list (TOON/TXN format - one per line)
python3 volume_sorted_coin_list.py --output-format toon
python3 volume_sorted_coin_list.py --output-format txn

# Comma-separated list (CSV format)
python3 volume_sorted_coin_list.py --output-format csv
```

### All Exchanges at Once

```bash
# Default JSON output
python3 volume_sorted_coin_list.py --all-exchanges

# Simple symbol list (TOON/TXN format - one per line)
python3 volume_sorted_coin_list.py --all-exchanges --output-format toon
python3 volume_sorted_coin_list.py --all-exchanges --output-format txn

# Comma-separated list (CSV format)
python3 volume_sorted_coin_list.py --all-exchanges --output-format csv
```

### Command Line Options

```bash
# Show help
python3 volume_sorted_coin_list.py --help

# Generate for all exchanges (JSON format - default)
python3 volume_sorted_coin_list.py --all-exchanges

# Generate for all exchanges (TOON format - symbol list only)
python3 volume_sorted_coin_list.py --all-exchanges --output-format toon

# Generate for all exchanges (TXN format - same as TOON)
python3 volume_sorted_coin_list.py --all-exchanges --output-format txn

# Generate for all exchanges (CSV format - comma-separated)
python3 volume_sorted_coin_list.py --all-exchanges --output-format csv

# Generate for all exchanges (ALL formats - generate all at once)
python3 volume_sorted_coin_list.py --all-exchanges --output-format all

# Single exchange with JSON format (default)
python3 volume_sorted_coin_list.py --output-format json

# Single exchange with TOON/TXN format (simple list)
python3 volume_sorted_coin_list.py --output-format toon
python3 volume_sorted_coin_list.py --output-format txn

# Single exchange with CSV format (comma-separated)
python3 volume_sorted_coin_list.py --output-format csv

# Single exchange with ALL formats (generate all at once)
python3 volume_sorted_coin_list.py --output-format all
```

### Output Format Options

| Format | Flag | Description | File Extension | Example |
|--------|------|-------------|----------------|---------|
| **JSON** | `--output-format json` | Full metadata with symbols, volumes, and rankings (default) | `.json` | `{"symbols": [...]}` |
| **TOON** | `--output-format toon` | Token-Oriented Object Notation - Full data (rank, symbol, volume) | `.toon` | `#1 BTCUSDT - $1,234,567.89` |
| **TXN** | `--output-format txn` | Token-Oriented Object Notation (alias) - Same as TOON | `.toon` | `#1 BTCUSDT - $1,234,567.89` |
| **CSV** | `--output-format csv` | Comma-separated values - Symbols sorted by volume | `.csv` | `BTCUSDT,ETHUSDT,SOLUSDT` |
| **TXT** | `--output-format txt` | Text file - Comma-separated list (same as CSV) | `.txt` | `BTCUSDT,ETHUSDT,SOLUSDT` |
| **ALL** | `--output-format all` | Generate ALL formats at once (JSON + TOON + CSV + TXT) | Multiple | All of the above |

---

## 📁 Output

Generated files are stored in the `output/` directory:

### JSON Format (Default)

```
output/
├── binance_active_coins_list.json
├── bybit_active_coins_list.json
├── bingx_active_coins_list.json
├── okx_active_coins_list.json
└── bitget_active_coins_list.json
```

### CSV/TXT Format (Comma-Separated Values)

```
output/
├── binance_active_coins_list.csv
├── binance_active_coins_list.txt
├── bybit_active_coins_list.csv
├── bybit_active_coins_list.txt
├── bingx_active_coins_list.csv
├── bingx_active_coins_list.txt
├── okx_active_coins_list.csv
├── okx_active_coins_list.txt
├── bitget_active_coins_list.csv
└── bitget_active_coins_list.txt
```

**Example content (both CSV and TXT):**
```
BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT,DOGEUSDT,ADAUSDT...
```

### JSON Structure

```json
{
  "metadata": {
    "generated_at": "2026-03-29 12:00",
    "timezone": "America/Mexico_City",
    "update_frequency": "30M",
    "exchange": "BINANCE",
    "volume_filter_active": false,
    "min_volume_usdt": null,
    "total_symbols": 150,
    "manually_excluded_count": 5
  },
  "symbols": [
    {
      "rank": 1,
      "symbol": "BTCUSDT",
      "volume_24h_usdt": 1234567890.50
    },
    {
      "rank": 2,
      "symbol": "ETHUSDT",
      "volume_24h_usdt": 987654321.25
    }
  ],
  "excluded_symbols": ["EXCLUDED1USDT", "EXCLUDED2USDT"]
}
```

### TOON/TXN Format (Token-Oriented Object Notation)

```
#1 BTCUSDT - $1,234,567,890.50
#2 ETHUSDT - $987,654,321.25
#3 SOLUSDT - $456,789,012.75
#4 BNBUSDT - $234,567,890.00
#5 XRPUSDT - $123,456,789.50
```

---

## ⚙️ Configuration

### Volume Filter

Edit `volume_sorted_coin_list.py` to enable volume filtering:

```python
USE_VOLUME_FILTER = True   # Enable volume filter
MIN_VOLUME_USDT = 100000   # Minimum 24h volume in USDT
```

### Manual Exclusion List

Create `exclude_coins.txt` in the project root:

```
BADCOINUSDT
SCAMCOINUSDT
LOWLIQUIDITYUSDT
```

These symbols will be automatically excluded from all generated lists.

---

## 🔧 Supported Exchanges

| Exchange | CCXT ID | Credentials Required |
|----------|---------|---------------------|
| Binance | `binance` | Optional (higher limits) |
| Bybit | `bybit` | Optional (higher limits) |
| BingX | `bingx` | Optional (higher limits) |
| OKX | `okx` | Optional (higher limits) |
| Bitget | `bitget` | Optional (higher limits) |

---

## 🏗️ Architecture

### Key Components

1. **CCXT Integration:** Unified API for multiple exchanges
2. **Smart Filtering:**
   - `is_likely_crypto()` - Filters out Forex, Commodities, Indices
   - Contract type validation (linear/swap only)
   - Quote currency filter (USDT only)
3. **Volume Ranking:** Sorted by 24h quote volume (descending)
4. **Output Generator:** JSON with metadata and symbol rankings

### Filtering Logic

```
All Markets
    ↓
[Filter] Contract/Derivative only
    ↓
[Filter] USDT Linear (quote=USDT)
    ↓
[Filter] Active markets
    ↓
[Filter] Crypto assets (no Forex/Commodities/Indices)
    ↓
[Filter] Manual exclusion list
    ↓
[Sort] By 24h volume (descending)
    ↓
Final List
```

---

## 🧪 Testing

```bash
# Test with Binance (default)
python3 volume_sorted_coin_list.py

# Test with specific exchange
EXCHANGE_CCXT=bybit python3 volume_sorted_coin_list.py

# Test all exchanges
python3 volume_sorted_coin_list.py --all-exchanges
```

---

## 📝 Examples

### Example Output (Console)

```
============================================================
🚀 Starting Multi-Exchange Coin List Generation
📅 2026-03-29 12:00
📛 Manually excluded coins: 5
============================================================

============================================================
[INFO] Processing exchange: BINANCE
[INFO] Output file: output/binance_active_coins_list.json
============================================================
[CCXT] Configuring client for: BINANCE...
[CCXT] Markets loaded: 2500
[CCXT] Fetching 24h tickers...
[CCXT] Processed 180 valid markets (USDT/Linear/Active).
♻️ Coin list update (30M) 2026-03-29 12:00
📈 Volume filter disabled. Base: 180 symbols.
🪙 Examples: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT
🔍 Total final symbols: 175
📛 Manually excluded: 5
[OK] List generated: output/binance_active_coins_list.json (175 symbols sorted by volume)
```

---

## 🔐 Security Notes

- API credentials are stored locally in `.env` (not committed to Git)
- Credentials are optional - public read-only access works without them
- Rate limits are automatically handled by CCXT
- No sensitive data is logged or stored in output files

---

## 🤝 Contributing

This is a **personal project** by @comgunner. For questions or collaboration requests, please contact the author.

---

## 📄 License

This project is licensed under the **Attribution License** - see the [LICENSE](LICENSE) file for details.

**Key Requirements:**
- ✅ Free to use for personal and commercial purposes
- ✅ Free to modify and distribute
- ⚠️ **Must give appropriate credit to the author (@comgunner)**
- ⚠️ **Must include a copy of the license**

---

## 📦 Distribution ZIP

### Download Latest Release

**📦 [Download v0.0.1 Release (ZIP)](https://github.com/comgunner/coin-volume-list/releases/download/v0.0.1/coin-volume-list-v0.0.1.zip)**

Or visit the [Releases page](https://github.com/comgunner/coin-volume-list/releases) for all versions:

```bash
# Download v0.0.1 release
wget https://github.com/comgunner/coin-volume-list/releases/download/v0.0.1/coin-volume-list-v0.0.1.zip

# Extract
unzip coin-volume-list-v0.0.1.zip
cd coin-volume-list

# Install dependencies
pip install -r requirements.txt
```

### Create ZIP Manually

```bash
# Using the script (Linux/macOS)
./scripts/create-release-zip.sh v1.0.0

# Or manually
mkdir dist
cp volume_sorted_coin_list.py exchanges.py requirements.txt LICENSE README.md README.es.md dist/
cd dist && zip -r ../coin-volume-list.zip ./* && cd ..
```

### GitHub Actions (Automatic)

The ZIP is automatically generated on:
- ✅ Release published
- ✅ Manual trigger from Actions tab

---

## 📞 Support

- **GitHub:** [@comgunner](https://github.com/comgunner)
- **Repository:** https://github.com/comgunner/GIT_CLONE

---

## 🙏 Acknowledgments

- **CCXT Team:** For the excellent cryptocurrency exchange library
- **Exchange APIs:** Binance, Bybit, BingX, OKX, Bitget for public API access

---

*Last Updated: March 29, 2026*
