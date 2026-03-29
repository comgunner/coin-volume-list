# 2026 Binance Coin List Generator
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import json
import os
import socket
import time
import warnings

# CCXT Import
import pytz

# Suppress MacOS/LibreSSL warning
try:
    from urllib3.exceptions import NotOpenSSLWarning

    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except ImportError:
    pass

from dotenv import load_dotenv

# Import exchange configuration
from exchanges import (
    SUPPORTED_EXCHANGES,
    create_ccxt_client,
    get_exchange_display_name,
)

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

load_dotenv()  # Load .env like main bot

USE_VOLUME_FILTER = False  # Disabled by request
MIN_VOLUME_USDT = 0.0  # 0 by request

# Manual exclusion list path used in main bot
EXCLUDE_FILE = "./exclude_coins.txt"

# Label used in logs
UPDATE_FREQUENCY_LABEL = "30M"

# CDMX timezone
CDMX = pytz.timezone("America/Mexico_City")

# Output directory for JSON files
OUTPUT_DIR = "output"

# Output filename pattern (will include exchange name)
OUTPUT_FILE_PATTERN = os.path.join(OUTPUT_DIR, "{exchange}_active_coins_list.json")

# Output format options
OUTPUT_FORMATS = [
    "json",
    "toon",
    "txn",
    "csv",
    "txt",
    "all",
]  # all = generate all formats


# -------------------------------------------------
# HELPERS
# -------------------------------------------------


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Created output directory: {OUTPUT_DIR}/")


def _now_cdmx_str():
    """Get current time in CDMX timezone as formatted string."""
    now = datetime.datetime.now(CDMX)
    return now.strftime("%Y-%m-%d %H:%M")


def has_internet(host="8.8.8.8", port=53, timeout=3):
    """Check internet connectivity."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


def load_excluded(path=EXCLUDE_FILE):
    """Read exclude_coins.txt to manually exclude symbols."""
    excluded = set()
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                coin = line.strip().upper()
                if coin:
                    excluded.add(coin)
    return excluded


def is_likely_crypto(market):
    """Filter out non-cryptocurrency assets (Forex, Commodities, Indices).
    Heuristic rules based on ID/Symbol and Base asset.
    """
    base = market.get("base", "").upper()
    symbol = market.get("symbol", "").upper()
    m_id = market.get("id", "").upper()
    info = market.get("info", {})
    display_name = info.get("displayName", "").upper()

    # 1. Blocklist keywords in ID/DisplayName (Commodities/Indices)
    BLOCKLIST = [
        "ALUMINIUM",
        "ALUM",
        "COPPER",
        "ZINC",
        "NICKEL",
        "LEAD",
        "TIN",
        "GOLD",
        "SILVER",
        "PLATINUM",
        "PALLADIUM",
        "OIL",
        "GAS",
        "BRENT",
        "WTI",
        "CORN",
        "WHEAT",
        "SOYBEAN",
        "SUGAR",
        "COFFEE",
        "COTTON",
        "SPX500",
        "NAS100",
        "US30",
        "DAX",
        "FTSE",
        "CAC40",
        "NIKKEI",
        "HSI",
        "ESTX50",
        "FOREX",
        "INDEX",
    ]

    # Check Display Name
    for kw in BLOCKLIST:
        if kw in display_name:
            return False
        if kw in m_id:
            return False

    # 2. Blocklist base currencies (Forex Fiat Majors)
    # Exclude pairs where base is a fiat currency
    FIAT_BLOCKLIST = {
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "AUD",
        "CAD",
        "CHF",
        "NZD",
        "HKD",
        "SEK",
        "NOK",
        "TRY",
        "MXN",
        "BRL",
        "ZAR",
        "CNH",
        "SGD",
    }

    # 2.1 Exception: USDC, USDD, USDE, TUSD, BUSD, FDUSD are Valid Cryptos
    # If base is exactly "USD", it's usually Forex "USD/JPY" reversed or similar weirdness like "USD/USDT"
    if base in FIAT_BLOCKLIST:
        return False

    # 3. Pattern: Symbols ending in 'USD' that are NOT stablecoins (e.g. NCCOALUMINIUM2USD)
    # Crypto pairs are usually XXX/USDT.
    # If the BASE ends in 'USD' (e.g. market['base'] == 'EURUSD'), it's a forex pair traded as a unit.
    if base.endswith("USD") and base not in [
        "TUSD",
        "BUSD",
        "FDUSD",
        "USDD",
        "CUSD",
        "SUSD",
        "OUSD",
    ]:
        # Be careful not to exclude unknown stablecoins, but "2USD" suffixes are suspicious.
        if "2USD" in base:
            return False

    return True


def get_ccxt_symbols_by_volume(exchange_id=None):
    """Get symbol list and 24h volume using CCXT.
    Applies contract, quote currency, and status filters.
    """
    client = create_ccxt_client(exchange_id)
    if not client:
        return [], {}, []

    print("[CCXT] Fetching 24h tickers...")
    # fetch_tickers() returns a dict: {symbol: ticker_data}
    try:
        tickers = client.fetch_tickers()
    except Exception as e:
        print(f"[ERROR] fetch_tickers failed: {e}")
        return [], {}, []

    final_list = []  # Clean ID for final list
    vol_map = {}  # Clean ID -> volume
    base_candidates = []  # All candidates (clean IDs) that met technical requirements

    count_processed = 0

    for symbol, ticker in tickers.items():
        market = client.markets.get(symbol)
        if not market:
            continue

        # --- MARKET FILTERS ---
        # 1. Contract (Derivative)
        if not market.get("contract"):
            continue

        # 2. USDT Margin (Linear)
        # Robust simplification like in the bot:
        is_linear = market.get("linear", False) is True
        is_usdt = market.get("quote") == "USDT"
        is_active = market.get("active", True)

        # Additional check for BingX/others where 'linear' may not be explicit but type=swap
        if not is_linear:
            if market.get("type") == "swap" and market.get("quote") == "USDT":
                is_linear = True

        if not (is_linear and is_usdt and is_active):
            continue

        # --- NON-CRYPTO FILTER (COMMODITIES/FOREX) ---
        if not is_likely_crypto(market):
            # print(f"[DEBUG] Skipping non-crypto: {market['id']}")
            continue

        count_processed += 1

        # --- VOLUME ---
        quote_vol = float(ticker.get("quoteVolume", 0) or 0)

        # --- ID NORMALIZATION ---
        # Get clean ID (e.g. BTCUSDT)
        raw_id = market["id"]

        clean_id = raw_id

        # OKX case: BTC-USDT-SWAP -> BTCUSDT
        if clean_id.endswith("-SWAP"):
            clean_id = clean_id.replace("-SWAP", "").replace("-", "")
        # BingX case: BTC-USDT -> BTCUSDT
        elif "-" in clean_id and clean_id.endswith("-USDT"):
            clean_id = clean_id.replace("-", "")

        base_candidates.append(clean_id)

        # Volume Filter
        if USE_VOLUME_FILTER:
            if quote_vol < MIN_VOLUME_USDT:
                continue

        # If it passes, save it
        # Store in vol_map using clean_id
        if clean_id not in vol_map:
            final_list.append(clean_id)
            vol_map[clean_id] = quote_vol

    # Sort by volume descending
    final_list.sort(key=lambda x: vol_map.get(x, 0), reverse=True)

    print(f"[CCXT] Processed {count_processed} valid markets (USDT/Linear/Active).")

    return final_list, vol_map, base_candidates


def generate_list_for_exchange(exchange_id, excluded_manual, output_format="json"):
    """Generate coin list for a specific exchange.

    Args:
        exchange_id: Exchange identifier (binance, bybit, etc.)
        excluded_manual: Set of manually excluded symbols
        output_format: Output format - "json", "toon", "txn", "csv", "txt", or "all" for all formats

    Returns:
        tuple: (exchange_name, output_filename, total_symbols, success)

    """
    exchange_name = get_exchange_display_name(exchange_id)
    output_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower())

    print(f"\n{'=' * 60}")
    print(f"[INFO] Processing exchange: {exchange_name}")
    print(f"[INFO] Output file: {output_filename}")
    print(f"{'=' * 60}")

    # Get candidates from CCXT
    final_symbols_ccxt, vol_map, base_candidates = get_ccxt_symbols_by_volume(
        exchange_id
    )

    if not final_symbols_ccxt and not base_candidates:
        print(f"[ERROR] No symbols obtained for {exchange_name}. Skipping.")
        return exchange_name, output_filename, 0, False

    # Filter excluded
    final_symbols_ready = [s for s in final_symbols_ccxt if s not in excluded_manual]

    # Statistics
    total_base = len(base_candidates)
    total_final = len(final_symbols_ready)
    examples_top5 = final_symbols_ready[:5]

    # LOG
    if USE_VOLUME_FILTER:
        volume_line = (
            f"📊 Volume filter active: {total_final} symbols >= {MIN_VOLUME_USDT}\n"
            f"🪙 Examples: {', '.join(examples_top5)}"
        )
    else:
        volume_line = (
            f"📈 Volume filter disabled. Base: {total_base} symbols.\n"
            f"🪙 Examples: {', '.join(examples_top5)}"
        )

    summary = (
        f"♻️ Coin list update ({UPDATE_FREQUENCY_LABEL}) {_now_cdmx_str()}\n"
        f"{volume_line}\n"
        f"🔍 Total final symbols: {total_final}\n"
        f"📛 Manually excluded: {len([s for s in final_symbols_ccxt if s in excluded_manual])}"
    )

    print(summary)

    # Generate output based on format
    if output_format == "all":
        # Generate ALL formats
        generated_files = []

        # 1. JSON format
        output_data = {
            "metadata": {
                "generated_at": _now_cdmx_str(),
                "timezone": "America/Mexico_City",
                "update_frequency": UPDATE_FREQUENCY_LABEL,
                "exchange": exchange_name,
                "volume_filter_active": USE_VOLUME_FILTER,
                "min_volume_usdt": MIN_VOLUME_USDT if USE_VOLUME_FILTER else None,
                "total_symbols": total_final,
                "manually_excluded_count": len(
                    [s for s in final_symbols_ccxt if s in excluded_manual]
                ),
            },
            "symbols": [
                {
                    "rank": idx + 1,
                    "symbol": symbol,
                    "volume_24h_usdt": vol_map.get(symbol, 0),
                }
                for idx, symbol in enumerate(final_symbols_ready)
            ],
            "excluded_symbols": list(excluded_manual & set(final_symbols_ccxt)),
        }
        json_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower())
        with open(json_filename, "w") as f:
            f.write(json.dumps(output_data, indent=2))
        generated_files.append(json_filename)

        # 2. TOON format
        toon_lines = []
        for idx, symbol in enumerate(final_symbols_ready):
            volume = vol_map.get(symbol, 0)
            toon_lines.append(f"#{idx + 1} {symbol} - ${volume:,.2f}")
        toon_content = "\n".join(toon_lines)
        toon_filename = OUTPUT_FILE_PATTERN.format(
            exchange=exchange_id.lower()
        ).replace(".json", ".toon")
        with open(toon_filename, "w") as f:
            f.write(toon_content)
        generated_files.append(toon_filename)

        # 3. CSV format
        csv_content = ",".join(final_symbols_ready)
        csv_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower()).replace(
            ".json", ".csv"
        )
        with open(csv_filename, "w") as f:
            f.write(csv_content)
        generated_files.append(csv_filename)

        # 4. TXT format
        txt_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower()).replace(
            ".json", ".txt"
        )
        with open(txt_filename, "w") as f:
            f.write(csv_content)
        generated_files.append(txt_filename)

        print(f"📝 Output format: ALL (generated {len(generated_files)} files)")
        for gf in generated_files:
            print(f"   ✓ {gf}")
        output_filename = ", ".join(generated_files)

    elif output_format in ["toon", "txn"]:
        # TOON/TXN format: Token-Oriented Object Notation - Full data in readable format
        lines = []
        for idx, symbol in enumerate(final_symbols_ready):
            volume = vol_map.get(symbol, 0)
            lines.append(f"#{idx + 1} {symbol} - ${volume:,.2f}")
        output_content = "\n".join(lines)
        output_filename = OUTPUT_FILE_PATTERN.format(
            exchange=exchange_id.lower()
        ).replace(".json", ".toon")
        print("📝 Output format: TOON (full data - rank, symbol, volume)")
    elif output_format in ["csv", "txt"]:
        # CSV/TXT format: Comma-separated symbol list (sorted by volume, no volume displayed)
        output_content = ",".join(final_symbols_ready)
        output_filename = OUTPUT_FILE_PATTERN.format(
            exchange=exchange_id.lower()
        ).replace(".json", f".{output_format}")
        print(f"📝 Output format: {output_format.upper()} (comma-separated)")
    else:
        # JSON format: Full metadata with symbols and volumes
        output_data = {
            "metadata": {
                "generated_at": _now_cdmx_str(),
                "timezone": "America/Mexico_City",
                "update_frequency": UPDATE_FREQUENCY_LABEL,
                "exchange": exchange_name,
                "volume_filter_active": USE_VOLUME_FILTER,
                "min_volume_usdt": MIN_VOLUME_USDT if USE_VOLUME_FILTER else None,
                "total_symbols": total_final,
                "manually_excluded_count": len(
                    [s for s in final_symbols_ccxt if s in excluded_manual]
                ),
            },
            "symbols": [
                {
                    "rank": idx + 1,
                    "symbol": symbol,
                    "volume_24h_usdt": vol_map.get(symbol, 0),
                }
                for idx, symbol in enumerate(final_symbols_ready)
            ],
            "excluded_symbols": list(excluded_manual & set(final_symbols_ccxt)),
        }
        output_content = json.dumps(output_data, indent=2)
        output_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower())
        print("📝 Output format: JSON (full metadata)")

    # Write output file (only if not "all" format - that writes its own files)
    if output_format != "all":
        with open(output_filename, "w") as f:
            f.write(output_content)

    print(
        f"[OK] List generated: {output_filename} ({total_final} symbols sorted by volume)"
    )

    return exchange_name, output_filename, total_final, True


def main():
    """Main entry point for the coin list generator."""
    # Ensure output directory exists
    ensure_output_dir()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate cryptocurrency coin lists from exchange data"
    )
    parser.add_argument(
        "--all-exchanges",
        action="store_true",
        help="Generate coin lists for all supported exchanges (binance, bybit, bingx, okx, bitget)",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["json", "toon", "txn", "csv", "txt", "all"],
        default="json",
        help="Output format: 'json' for full JSON, 'toon'/'txn' for readable format with volumes, 'csv'/'txt' for comma-separated list, 'all' for all formats (default: json)",
    )
    args = parser.parse_args()

    now_label = _now_cdmx_str()

    # Load manual exclusions (shared across all exchanges)
    excluded_manual = load_excluded()

    if args.all_exchanges:
        # Generate lists for all supported exchanges
        print(f"{'=' * 60}")
        print("🚀 Starting Multi-Exchange Coin List Generation")
        print(f"📅 {now_label}")
        print(f"📛 Manually excluded coins: {len(excluded_manual)}")
        print(f"📝 Output format: {args.output_format.upper()}")
        print(f"{'=' * 60}")

        results = []
        successful = 0
        failed = 0

        for exchange_id in SUPPORTED_EXCHANGES:
            exchange_name, output_filename, total_symbols, success = (
                generate_list_for_exchange(
                    exchange_id, excluded_manual, output_format=args.output_format
                )
            )
            results.append((exchange_name, output_filename, total_symbols, success))

            if success:
                successful += 1
            else:
                failed += 1

            # Small delay between exchanges to respect rate limits
            if exchange_id != SUPPORTED_EXCHANGES[-1]:
                print("\n⏳ Waiting 2 seconds before next exchange...")
                time.sleep(2)

        # Summary
        print(f"\n{'=' * 60}")
        print("✅ Multi-Exchange Generation Complete!")
        print(f"{'=' * 60}")
        print("📊 Results:")
        for exchange_name, output_filename, total_symbols, success in results:
            status = "✅" if success else "❌"
            print(
                f"  {status} {exchange_name:10} → {output_filename:35} ({total_symbols} symbols)"
            )
        print(f"\n📈 Summary: {successful} successful, {failed} failed")
        print(f"{'=' * 60}")

    else:
        # Single exchange mode (existing behavior)
        exchange_id = os.getenv("EXCHANGE_CCXT", "binance").strip().lower()
        exchange_name = get_exchange_display_name(exchange_id)

        print(f"--- Starting List Generation ({now_label}) ---")
        print(f"[INFO] Exchange: {exchange_name}")
        print(f"📝 Output format: {args.output_format.upper()}")

        # Get candidates from CCXT
        final_symbols_ccxt, vol_map, base_candidates = get_ccxt_symbols_by_volume(
            exchange_id
        )

        if not final_symbols_ccxt and not base_candidates:
            print("[ERROR] No symbols obtained. Aborting.")
            return

        # Filter excluded
        final_symbols_ready = [
            s for s in final_symbols_ccxt if s not in excluded_manual
        ]

        # Statistics
        total_base = len(base_candidates)
        total_final = len(final_symbols_ready)

        # Examples
        examples_top5 = final_symbols_ready[:5]

        # LOG
        if USE_VOLUME_FILTER:
            volume_line = (
                f"📊 Volume filter active: {total_final} symbols >= {MIN_VOLUME_USDT}\n"
                f"🪙 Examples: {', '.join(examples_top5)}"
            )
        else:
            volume_line = (
                f"📈 Volume filter disabled. Base: {total_base} symbols.\n"
                f"🪙 Examples: {', '.join(examples_top5)}"
            )

        summary = (
            f"♻️ Coin list update ({UPDATE_FREQUENCY_LABEL}) {now_label}\n"
            f"{volume_line}\n"
            f"🔍 Total final symbols: {total_final}\n"
            f"📛 Manually excluded: {len([s for s in final_symbols_ccxt if s in excluded_manual])}"
        )

        print(summary)

        # Generate output based on format
        if args.output_format == "all":
            # Generate ALL formats
            generated_files = []

            # 1. JSON format
            output_data = {
                "metadata": {
                    "generated_at": now_label,
                    "timezone": "America/Mexico_City",
                    "update_frequency": UPDATE_FREQUENCY_LABEL,
                    "exchange": exchange_name,
                    "volume_filter_active": USE_VOLUME_FILTER,
                    "min_volume_usdt": MIN_VOLUME_USDT if USE_VOLUME_FILTER else None,
                    "total_symbols": total_final,
                    "manually_excluded_count": len(
                        [s for s in final_symbols_ccxt if s in excluded_manual]
                    ),
                },
                "symbols": [
                    {
                        "rank": idx + 1,
                        "symbol": symbol,
                        "volume_24h_usdt": vol_map.get(symbol, 0),
                    }
                    for idx, symbol in enumerate(final_symbols_ready)
                ],
                "excluded_symbols": list(excluded_manual & set(final_symbols_ccxt)),
            }
            json_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower())
            with open(json_filename, "w") as f:
                f.write(json.dumps(output_data, indent=2))
            generated_files.append(json_filename)

            # 2. TOON format
            toon_lines = []
            for idx, symbol in enumerate(final_symbols_ready):
                volume = vol_map.get(symbol, 0)
                toon_lines.append(f"#{idx + 1} {symbol} - ${volume:,.2f}")
            toon_content = "\n".join(toon_lines)
            toon_filename = OUTPUT_FILE_PATTERN.format(
                exchange=exchange_id.lower()
            ).replace(".json", ".toon")
            with open(toon_filename, "w") as f:
                f.write(toon_content)
            generated_files.append(toon_filename)

            # 3. CSV format
            csv_content = ",".join(final_symbols_ready)
            csv_filename = OUTPUT_FILE_PATTERN.format(
                exchange=exchange_id.lower()
            ).replace(".json", ".csv")
            with open(csv_filename, "w") as f:
                f.write(csv_content)
            generated_files.append(csv_filename)

            # 4. TXT format
            txt_filename = OUTPUT_FILE_PATTERN.format(
                exchange=exchange_id.lower()
            ).replace(".json", ".txt")
            with open(txt_filename, "w") as f:
                f.write(csv_content)
            generated_files.append(txt_filename)

            print(f"📝 Output format: ALL (generated {len(generated_files)} files)")
            for gf in generated_files:
                print(f"   ✓ {gf}")
            output_filename = ", ".join(generated_files)

        elif args.output_format in ["toon", "txn"]:
            # TOON/TXN format: Token-Oriented Object Notation - Full data in readable format
            lines = []
            for idx, symbol in enumerate(final_symbols_ready):
                volume = vol_map.get(symbol, 0)
                lines.append(f"#{idx + 1} {symbol} - ${volume:,.2f}")
            output_content = "\n".join(lines)
            output_filename = OUTPUT_FILE_PATTERN.format(
                exchange=exchange_id.lower()
            ).replace(".json", ".toon")
            print("📝 Output format: TOON (full data - rank, symbol, volume)")
        elif args.output_format in ["csv", "txt"]:
            # CSV/TXT format: Comma-separated symbol list (sorted by volume, no volume displayed)
            output_content = ",".join(final_symbols_ready)
            output_filename = OUTPUT_FILE_PATTERN.format(
                exchange=exchange_id.lower()
            ).replace(".json", f".{args.output_format}")
            print(f"📝 Output format: {args.output_format.upper()} (comma-separated)")
        else:
            # JSON format: Full metadata with symbols and volumes
            output_data = {
                "metadata": {
                    "generated_at": now_label,
                    "timezone": "America/Mexico_City",
                    "update_frequency": UPDATE_FREQUENCY_LABEL,
                    "exchange": exchange_name,
                    "volume_filter_active": USE_VOLUME_FILTER,
                    "min_volume_usdt": MIN_VOLUME_USDT if USE_VOLUME_FILTER else None,
                    "total_symbols": total_final,
                    "manually_excluded_count": len(
                        [s for s in final_symbols_ccxt if s in excluded_manual]
                    ),
                },
                "symbols": [
                    {
                        "rank": idx + 1,
                        "symbol": symbol,
                        "volume_24h_usdt": vol_map.get(symbol, 0),
                    }
                    for idx, symbol in enumerate(final_symbols_ready)
                ],
                "excluded_symbols": list(excluded_manual & set(final_symbols_ccxt)),
            }
            output_content = json.dumps(output_data, indent=2)
            output_filename = OUTPUT_FILE_PATTERN.format(exchange=exchange_id.lower())
            print("📝 Output format: JSON (full metadata)")

        # Write output file (only if not "all" format - that writes its own files)
        if args.output_format != "all":
            with open(output_filename, "w") as f:
                f.write(output_content)

        print(
            f"[OK] List generated: {output_filename} ({total_final} symbols sorted by volume)"
        )


if __name__ == "__main__":
    main()
