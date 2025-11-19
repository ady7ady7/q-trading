"""
Shared configuration module for the quant trading project.

Contains constants, paths, timezone mappings, and default parameters.
All configuration should be centralized here to avoid hardcoding values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import time

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

DATABASE_CA_CERT_PATH = os.getenv('DATABASE_CA_CERT_PATH')
if not DATABASE_CA_CERT_PATH:
    raise ValueError("DATABASE_CA_CERT_PATH not set in .env file")


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# SYMBOL AND ASSET CONFIGURATION
# ============================================================================
# All symbols available in the database (as per symbol_metadata table)
SYMBOLS = {
    # TradFi - Indices
    'deuidxeur': {
        'name': 'DAX Index',
        'asset_type': 'tradfi',
        'timezone': 'Europe/Berlin',
        'market_open': time(9, 0),
        'market_close': time(17, 30),
    },
    'usa500idxusd': {
        'name': 'S&P 500',
        'asset_type': 'tradfi',
        'timezone': 'America/New_York',
        'market_open': time(9, 30),
        'market_close': time(16, 0),
    },
    'usatechidxusd': {
        'name': 'Nasdaq 100',
        'asset_type': 'tradfi',
        'timezone': 'America/New_York',
        'market_open': time(9, 30),
        'market_close': time(16, 0),
    },
    'usa30idxusd': {
        'name': 'Dow Jones 30',
        'asset_type': 'tradfi',
        'timezone': 'America/New_York',
        'market_open': time(9, 30),
        'market_close': time(16, 0),
    },

    # TradFi - Forex
    'eurusd': {
        'name': 'Euro/US Dollar',
        'asset_type': 'tradfi',
        'timezone': 'Europe/London',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'eurjpy': {
        'name': 'Euro/Japanese Yen',
        'asset_type': 'tradfi',
        'timezone': 'Europe/London',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'usdcad': {
        'name': 'US Dollar/Canadian Dollar',
        'asset_type': 'tradfi',
        'timezone': 'America/Toronto',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'nzdcad': {
        'name': 'New Zealand Dollar/Canadian Dollar',
        'asset_type': 'tradfi',
        'timezone': 'Pacific/Auckland',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'gbpusd': {
        'name': 'British Pound/US Dollar',
        'asset_type': 'tradfi',
        'timezone': 'Europe/London',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },

    # TradFi - Commodities
    'xauusd': {
        'name': 'Spot Gold',
        'asset_type': 'tradfi',
        'timezone': 'America/New_York',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'xagusd': {
        'name': 'Spot Silver',
        'asset_type': 'tradfi',
        'timezone': 'America/New_York',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'lightcmdusd': {
        'name': 'Light Crude Oil (WTI)',
        'asset_type': 'tradfi',
        'timezone': 'America/New_York',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },

    # Crypto
    'ethusdt': {
        'name': 'Ethereum/Tether',
        'asset_type': 'crypto',
        'timezone': 'UTC',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
    'btcusdt': {
        'name': 'Bitcoin/Tether',
        'asset_type': 'crypto',
        'timezone': 'UTC',
        'market_open': time(0, 0),
        'market_close': time(23, 59),
    },
}

# ============================================================================
# TABLE NAMING CONVENTIONS
# ============================================================================
# Database table naming follows these patterns:
#   TradFi:  {symbol}_{timeframe}_tradfi_ohlcv
#   Crypto:  {symbol}_{timeframe}_{exchange}_crypto_ohlcv
#
# Available timeframes: m1, m5, h1

TRADFI_SYMBOLS = {
    'deuidxeur', 'usa500idxusd', 'usatechidxusd', 'usa30idxusd',
    'eurusd', 'eurjpy', 'usdcad', 'nzdcad', 'gbpusd',
    'xauusd', 'xagusd', 'lightcmdusd'
}

CRYPTO_SYMBOLS = {'ethusdt', 'btcusdt'}

AVAILABLE_TIMEFRAMES = ['m1', 'm5', 'h1']

# ============================================================================
# TIMEZONE MAPPING (for convenience)
# ============================================================================
INSTRUMENT_TIMEZONES = {
    symbol: SYMBOLS[symbol]['timezone']
    for symbol in SYMBOLS
}

# ============================================================================
# MARKET HOURS MAPPING (for convenience)
# ============================================================================
MARKET_HOURS = {
    symbol: {
        'open': SYMBOLS[symbol]['market_open'],
        'close': SYMBOLS[symbol]['market_close'],
    }
    for symbol in SYMBOLS
}

# ============================================================================
# DATA RETRIEVAL DEFAULTS
# ============================================================================
DEFAULT_DATA_CONFIG = {
    'exclude_news': False,
    'local_time': False,
}

# ============================================================================
# DATA CLEANING CONFIGURATION
# ============================================================================
# Outlier detection thresholds
OUTLIER_THRESHOLD_MAD = 3.0  # Median Absolute Deviation multiplier (e.g., median ± 3*MAD)
OUTLIER_THRESHOLD_IQR = 1.5  # Interquartile Range multiplier (e.g., 1.5*IQR)

# MICE Imputation configuration
MICE_CONFIG = {
    'max_iter': 10,
    'random_state': 42,
    'verbose': 0,
    'estimator': None,  # Uses default BayesianRidge
}

# Gap tolerance for imputation
# Warn if missing data exceeds this percentage
GAP_TOLERANCE_PERCENT = 30.0

# Random seed for reproducibility of diagnostic benchmark
DIAGNOSTIC_SEED = 42
DIAGNOSTIC_TEST_MISSING_PERCENT = 7.5  # Mask 7.5% of clean data for testing

# ============================================================================
# COST CONFIGURATION (for backtesting)
# ============================================================================
DEFAULT_COSTS = {
    'commission_bps': 1.0,        # Basis points (0.01% = 1 bp)
    'slippage_bps': 0.5,          # Basis points
    'spread_bps': 0.5,            # Bid-ask spread
}

# ============================================================================
# POSITION SIZING CONFIGURATION
# ============================================================================
POSITION_SIZING = {
    'default_method': 'fixed_fractional',  # 'fixed_fractional' or 'kelly'
    'fixed_fractional_pct': 2.0,           # Risk 2% per trade
    'kelly_fraction': 0.25,                # Use 0.25 Kelly for safety
}

# ============================================================================
# DATA PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
CACHE_DIR = PROJECT_ROOT / 'cache'
RESULTS_DIR = PROJECT_ROOT / 'results'

# Create directories if they don't exist
for directory in [DATA_DIR, CACHE_DIR, RESULTS_DIR]:
    directory.mkdir(exist_ok=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_symbol_info(symbol: str) -> dict:
    """
    Get metadata for a symbol.

    Args:
        symbol (str): Symbol name (lowercase)

    Returns:
        dict: Symbol metadata

    Raises:
        ValueError: If symbol not found
    """
    symbol_lower = symbol.lower()
    if symbol_lower not in SYMBOLS:
        available = ', '.join(sorted(SYMBOLS.keys()))
        raise ValueError(
            f"Symbol '{symbol}' not found. "
            f"Available symbols: {available}"
        )
    return SYMBOLS[symbol_lower]


def is_tradfi_symbol(symbol: str) -> bool:
    """Check if symbol is TradFi (not crypto)."""
    return symbol.lower() in TRADFI_SYMBOLS


def is_crypto_symbol(symbol: str) -> bool:
    """Check if symbol is cryptocurrency."""
    return symbol.lower() in CRYPTO_SYMBOLS


def get_table_name(symbol: str, timeframe: str, exchange: str = None) -> str:
    """
    Generate table name from symbol and timeframe.

    Args:
        symbol (str): Symbol name
        timeframe (str): Timeframe (m1, m5, h1)
        exchange (str): Exchange for crypto (optional, defaults to binance)

    Returns:
        str: Table name

    Raises:
        ValueError: If symbol or timeframe invalid
    """
    symbol_lower = symbol.lower()
    timeframe_lower = timeframe.lower()

    if symbol_lower not in SYMBOLS:
        raise ValueError(f"Unknown symbol: {symbol}")

    if timeframe_lower not in AVAILABLE_TIMEFRAMES:
        raise ValueError(
            f"Unknown timeframe: {timeframe}. "
            f"Available: {', '.join(AVAILABLE_TIMEFRAMES)}"
        )

    if is_tradfi_symbol(symbol_lower):
        return f"{symbol_lower}_{timeframe_lower}_tradfi_ohlcv"
    elif is_crypto_symbol(symbol_lower):
        if not exchange:
            exchange = 'binance'  # Default exchange for crypto
        return f"{symbol_lower}_{timeframe_lower}_{exchange}_crypto_ohlcv"
    else:
        raise ValueError(f"Symbol type unknown: {symbol}")
