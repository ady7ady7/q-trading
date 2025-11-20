"""
Data Handler Module

Handles complete data pipeline:
- Fetch raw data from database
- Process and clean data
- Analyze and handle gaps
- Return analysis-ready data

All data quality checks happen here.
Notebooks receive clean, validated data only.
"""

import logging
from typing import Tuple
import pandas as pd
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data
from shared.config import LOG_LEVEL, LOGS_DIR

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))

console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

log_file = LOGS_DIR / 'data_handler.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(getattr(logging, LOG_LEVEL))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ============================================================================
# MAIN DATA HANDLER
# ============================================================================
def get_clean_market_data(
    symbol: str,
    timeframe: str,
    start_date,
    end_date,
    local_time: bool = True,
    exclude_news: bool = False,
) -> Tuple[pd.DataFrame, dict]:
    """
    Complete data pipeline: fetch -> process -> validate -> return clean data.

    All data quality checks and gap handling happen here.
    Notebooks receive analysis-ready data only.

    Args:
        symbol (str): Symbol name (e.g., 'deuidxeur', 'usa500idxusd')
        timeframe (str): Timeframe (m1, m5, h1)
        start_date: Start datetime
        end_date: End datetime
        local_time (bool): Convert to local timezone (default: True)
        exclude_news (bool): Filter out news dates (default: False)

    Returns:
        tuple: (df_clean, metadata_dict)
            - df_clean: Clean, validated DataFrame ready for analysis
            - metadata_dict: Contains gap analysis, data quality metrics
    """
    logger.info(
        f"get_clean_market_data(): symbol={symbol}, timeframe={timeframe}, "
        f"start={start_date}, end={end_date}"
    )

    # Step 1: Fetch raw data
    logger.info("Step 1: Fetching raw data from database...")
    df_raw = fetch_ohlcv(symbol, timeframe, start_date, end_date)
    logger.info(f"[OK] Fetched {len(df_raw)} candles (raw, all hours)")

    # Step 2: Process data (timezone conversion, filtering, cleaning)
    logger.info("Step 2: Processing data (timezone, filtering, cleaning)...")
    df_clean = process_data(
        df=df_raw,
        symbol=symbol,
        timeframe=timeframe,
        local_time=local_time,
        exclude_news=exclude_news
    )
    logger.info(f"[OK] Processed to {len(df_clean)} candles (market hours only)")

    # Step 3: Analyze gaps and data quality
    logger.info("Step 3: Analyzing data quality...")
    metadata = _analyze_data_quality(df_raw, df_clean, symbol, timeframe)
    logger.info(f"[OK] Data quality: {metadata['data_quality']:.1f}%")

    # Step 4: Validate no NaN values
    logger.info("Step 4: Validating no missing values...")
    missing_counts = df_clean.isnull().sum()
    if missing_counts.sum() > 0:
        logger.warning(f"Found {missing_counts.sum()} NaN values after cleaning")
        logger.warning(f"Missing by column:\n{missing_counts[missing_counts > 0]}")
    else:
        logger.info("[OK] No missing values in clean data")

    logger.info(
        f"[OK] Data handler complete: {len(df_clean)} analysis-ready candles"
    )

    return df_clean, metadata


# ============================================================================
# INTERNAL FUNCTIONS
# ============================================================================
def _analyze_data_quality(
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
    symbol: str,
    timeframe: str,
) -> dict:
    """
    Analyze gap rates and data quality metrics.

    Args:
        df_raw: Raw data (all hours)
        df_clean: Clean data (market hours only)
        symbol: Symbol name
        timeframe: Timeframe

    Returns:
        dict: Metadata with gap analysis
    """
    # Raw data gap analysis (context only)
    expected_raw = (df_raw.index[-1] - df_raw.index[0]).total_seconds() / 60
    freq_map = {'m1': 1, 'm5': 5, 'm15': 15, 'h1': 60, 'd1': 1440}
    expected_minutes = freq_map.get(timeframe.lower(), 60)
    expected_raw_candles = (expected_raw / expected_minutes) + 1
    actual_raw = len(df_raw)
    gap_raw = ((expected_raw_candles - actual_raw) / expected_raw_candles * 100)

    # Clean data gap analysis (meaningful metric)
    expected_clean = (df_clean.index[-1] - df_clean.index[0]).total_seconds() / 60
    expected_clean_candles = (expected_clean / expected_minutes) + 1
    actual_clean = len(df_clean)
    gap_clean = (
        ((expected_clean_candles - actual_clean) / expected_clean_candles * 100)
        if expected_clean_candles > 0
        else 0
    )
    data_quality = 100 - gap_clean

    logger.info(f"Gap Analysis ({symbol} {timeframe}):")
    logger.info(f"  Raw data: {actual_raw} candles, gap {gap_raw:.1f}%")
    logger.info(f"  Clean data: {actual_clean} candles, gap {gap_clean:.1f}%")
    logger.info(f"  Data quality: {data_quality:.1f}%")

    metadata = {
        'symbol': symbol,
        'timeframe': timeframe,
        'raw_candles': actual_raw,
        'clean_candles': actual_clean,
        'gap_raw_percent': gap_raw,
        'gap_clean_percent': gap_clean,
        'data_quality': data_quality,
        'date_range_start': df_clean.index.min(),
        'date_range_end': df_clean.index.max(),
        'timezone': str(df_clean.index.tz),
    }

    return metadata


if __name__ == '__main__':
    logger.info("Data handler module imported successfully")
