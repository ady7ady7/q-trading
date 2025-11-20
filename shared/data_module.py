"""
Data processing module for OHLCV data cleaning and transformation.

This module handles:
  - Timezone conversion (UTC <-> local)
  - Data validation (OHLC consistency)
  - Gap and outlier diagnostics
  - Missing data imputation (MICE)
  - News calendar filtering

Raw data fetching is handled by database_connector.py.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
import pytz

from shared.config import (
    INSTRUMENT_TIMEZONES,
    OUTLIER_THRESHOLD_MAD,
    OUTLIER_THRESHOLD_IQR,
    GAP_TOLERANCE_PERCENT,
    MICE_CONFIG,
    DIAGNOSTIC_SEED,
    DIAGNOSTIC_TEST_MISSING_PERCENT,
    LOG_LEVEL,
    LOGS_DIR,
    MARKET_HOLIDAYS,
    get_symbol_info,
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, LOG_LEVEL))
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler
log_file = LOGS_DIR / 'data_module.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(getattr(logging, LOG_LEVEL))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ============================================================================
# DATA PROCESSING
# ============================================================================
def process_data(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    local_time: bool = False,
    exclude_news: bool = False,
) -> pd.DataFrame:
    """
    Process raw OHLCV data: validate, clean, impute, convert timezone.

    This is the main entry point for data processing.
    Raw data should be fetched using database_connector.fetch_ohlcv().

    Args:
        df (pd.DataFrame): Raw OHLCV data with 'timestamp' column
        symbol (str): Symbol name (for config lookup)
        timeframe (str): Timeframe
        local_time (bool): If True, convert to local timezone
        exclude_news (bool): If True, exclude news dates

    Returns:
        pd.DataFrame: Cleaned, indexed OHLCV data
                     Index: datetime (UTC or local depending on local_time)
                     Columns: [open, high, low, close, volume]

    Raises:
        ValueError: If symbol not configured or data invalid
    """
    logger.info(
        f"process_data(): symbol={symbol}, timeframe={timeframe}, "
        f"local_time={local_time}, exclude_news={exclude_news}"
    )

    if df.empty:
        logger.warning("Input DataFrame is empty")
        return df

    # Step 1: Ensure timestamp is the index (data from DB is already UTC)
    if 'timestamp' in df.columns:
        df = df.set_index('timestamp')

    # Step 2: Localize to UTC if naive (needed for proper timezone handling)
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')

    # Step 3: Convert to local timezone for analysis (market hours are in local time)
    target_tz = get_symbol_info(symbol)['timezone']
    df = _convert_to_local_time(df, target_tz)
    logger.info(f"Converted to local timezone: {target_tz}")

    # Step 4: Filter to market hours only
    df = _filter_to_market_hours(df, symbol)

    # Step 5: Validate OHLC consistency
    _validate_ohlc(df, symbol)

    # Step 6: Diagnostics (gaps, outliers, missing data) - now in local time, market hours only
    _run_diagnostics(df, symbol, timeframe)

    # Step 7: Data cleaning (imputation)
    df = _clean_data(df, symbol)

    # Step 8: News filtering (if requested)
    if exclude_news:
        df = _filter_news_dates(df, symbol)

    logger.info(
        f"[OK] Data processing complete: {len(df)} candles, "
        f"range {df.index.min()} to {df.index.max()}"
    )
    return df


# ============================================================================
# MARKET HOURS FILTERING
# ============================================================================
def _filter_to_market_hours(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Filter DataFrame to only include candles within market trading hours.

    ASSUMES: DataFrame is already in LOCAL timezone for the instrument.

    Removes:
      - Weekend candles
      - Holiday candles
      - Candles outside market hours (e.g., before 09:00 or after 17:30 for DAX)

    Returns:
        Filtered DataFrame with only market-hours candles.
    """
    try:
        symbol_info = get_symbol_info(symbol)
        market_open = symbol_info['market_open']
        market_close = symbol_info['market_close']
    except:
        # If symbol not found, return data as-is (24/7 markets like crypto)
        logger.info("Market hours not found for symbol, keeping all data")
        return df

    # Filter by weekday (0=Mon, 4=Fri, 5=Sat, 6=Sun)
    df_filtered = df[df.index.weekday < 5].copy()

    # Filter by holiday
    df_filtered = df_filtered[
        ~df_filtered.index.strftime('%Y-%m-%d').isin(MARKET_HOLIDAYS)
    ].copy()

    # Filter by market hours
    df_filtered = df_filtered[
        (df_filtered.index.time >= market_open) &
        (df_filtered.index.time <= market_close)
    ].copy()

    n_removed = len(df) - len(df_filtered)
    logger.info(
        f"[OK] Filtered to market hours: removed {n_removed} candles "
        f"({len(df_filtered)} remaining)"
    )

    return df_filtered


# ============================================================================
# TIMEZONE HANDLING
# ============================================================================
def _convert_to_local_time(df: pd.DataFrame, target_tz: str) -> pd.DataFrame:
    """
    Convert DataFrame index from UTC to target timezone.

    Args:
        df (pd.DataFrame): DataFrame with UTC timezone-aware index
        target_tz (str): Target timezone (pytz format)

    Returns:
        pd.DataFrame: DataFrame with local timezone index
    """
    if df.index.tz is None:
        raise ValueError("DataFrame index must be timezone-aware (UTC)")

    try:
        df.index = df.index.tz_convert(target_tz)
        logger.debug(f"Timezone converted to {target_tz}")
        return df
    except Exception as e:
        logger.error(f"Timezone conversion error: {e}")
        raise


# ============================================================================
# DATA VALIDATION
# ============================================================================
def _validate_ohlc(df: pd.DataFrame, symbol: str) -> None:
    """
    Validate OHLC consistency.

    Checks:
      - High >= Low
      - High >= Open, Close
      - Low <= Open, Close
      - All values are positive
      - No NaN in OHLCV

    Args:
        df (pd.DataFrame): DataFrame with OHLCV columns

    Raises:
        ValueError: If validation fails critically
    """
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    # Check for NaN (before imputation)
    nan_counts = df[required_cols].isna().sum()
    if nan_counts.any():
        logger.warning(
            f"NaN values found in {symbol}:\n{nan_counts[nan_counts > 0]}"
        )

    # High >= Low
    invalid_hl = df['high'] < df['low']
    if invalid_hl.any():
        n_invalid = invalid_hl.sum()
        logger.warning(f"{n_invalid} candles with High < Low")

    # High >= Open, Close
    invalid_ho = df['high'] < df['open']
    invalid_hc = df['high'] < df['close']
    if (invalid_ho | invalid_hc).any():
        n_invalid = (invalid_ho | invalid_hc).sum()
        logger.warning(f"{n_invalid} candles with High < Open or Close")

    # Low <= Open, Close
    invalid_lo = df['low'] > df['open']
    invalid_lc = df['low'] > df['close']
    if (invalid_lo | invalid_lc).any():
        n_invalid = (invalid_lo | invalid_lc).sum()
        logger.warning(f"{n_invalid} candles with Low > Open or Close")

    # Price columns should be positive
    price_cols = ['open', 'high', 'low', 'close']
    for col in price_cols:
        if (df[col] <= 0).any():
            n_invalid = (df[col] <= 0).sum()
            logger.warning(f"{n_invalid} candles with {col} <= 0")

    logger.info("[OK] OHLC validation complete")


# ============================================================================
# DIAGNOSTICS
# ============================================================================
def _run_diagnostics(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
) -> None:
    """
    Run comprehensive diagnostics on the data.

    Performs:
      - Gap analysis (missing candles, accounting for market hours/holidays)
      - Missing data analysis
      - Outlier detection

    Args:
        df (pd.DataFrame): OHLCV DataFrame
        symbol (str): Symbol name
        timeframe (str): Timeframe
    """
    logger.info(f"Running diagnostics for {symbol} {timeframe}...")

    _analyze_gaps(df, timeframe, symbol)
    _analyze_missing_data(df)
    _detect_outliers(df)

    logger.info("[OK] Diagnostics complete")


def _analyze_gaps(df: pd.DataFrame, timeframe: str, symbol: str = None) -> None:
    """
    Analyze missing candles in already-filtered data.

    ASSUMES: Data is already in LOCAL timezone and filtered to market hours.

    Simple analysis: Check for gaps between consecutive candles.
    No need to regenerate expected timestamps (avoids DST issues).

    Args:
        df (pd.DataFrame): Already filtered OHLCV data (market hours only)
        timeframe (str): Timeframe (m1, m5, h1, etc.)
        symbol (str): Symbol name (optional)
    """
    if len(df) < 2:
        logger.warning("Not enough data to analyze gaps")
        return

    freq_map = {
        'm1': 1,
        'm5': 5,
        'm15': 15,
        'h1': 60,
        'd1': 1440,
    }

    expected_minutes = freq_map.get(timeframe.lower())
    if expected_minutes is None:
        logger.warning(f"Unknown timeframe {timeframe}, skipping gap analysis")
        return

    # Calculate expected duration based on first and last timestamp
    total_duration = (df.index[-1] - df.index[0]).total_seconds() / 60  # in minutes
    expected_candles_theoretical = (total_duration / expected_minutes) + 1

    # Actual candles we have
    actual_candles = len(df)

    # Simple gap: difference between theoretical and actual
    missing_candles = expected_candles_theoretical - actual_candles
    gap_pct = (missing_candles / expected_candles_theoretical * 100) if expected_candles_theoretical > 0 else 0

    logger.info(f"Gap Analysis ({symbol or 'data'} {timeframe}):")
    logger.info(f"  Date range (local): {df.index.min()} to {df.index.max()}")
    logger.info(f"  Theoretical candles (continuous): {expected_candles_theoretical:.0f}")
    logger.info(f"  Actual candles: {actual_candles}")
    logger.info(f"  Missing: {missing_candles:.0f} ({gap_pct:.1f}%)")
    logger.info(f"  Note: Data already filtered to market hours (weekdays, trading hours, non-holidays)")

    if gap_pct > 5:
        logger.warning(f"  [WARNING] Gap rate {gap_pct:.1f}% exceeds 5% threshold")
    elif gap_pct == 0:
        logger.info("[OK] No missing candles")


def _analyze_missing_data(df: pd.DataFrame) -> None:
    """Analyze missing data (NaN) in OHLCV columns."""
    ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
    existing_cols = [c for c in ohlcv_cols if c in df.columns]

    missing_pct = (df[existing_cols].isna().sum() / len(df)) * 100

    if (missing_pct > 0).any():
        logger.warning("Missing data detected:")
        for col in existing_cols:
            if missing_pct[col] > 0:
                pct = missing_pct[col]
                logger.warning(f"  {col}: {pct:.2f}% missing")

                if pct > GAP_TOLERANCE_PERCENT:
                    logger.warning(
                        f"  [WARNING] {col} exceeds {GAP_TOLERANCE_PERCENT}% threshold"
                    )
    else:
        logger.info("[OK] No missing data")


def _detect_outliers(df: pd.DataFrame) -> None:
    """Detect outliers using MAD and IQR methods."""
    ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
    existing_cols = [c for c in ohlcv_cols if c in df.columns]

    outliers_found = False

    for col in existing_cols:
        data = df[col].dropna()
        if len(data) < 3:
            continue

        # MAD method
        median = data.median()
        mad = (data - median).abs().median()
        mad_outliers = (
            (data < median - OUTLIER_THRESHOLD_MAD * mad) |
            (data > median + OUTLIER_THRESHOLD_MAD * mad)
        )

        # IQR method
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        iqr_outliers = (
            (data < q1 - OUTLIER_THRESHOLD_IQR * iqr) |
            (data > q3 + OUTLIER_THRESHOLD_IQR * iqr)
        )

        n_outliers = (mad_outliers | iqr_outliers).sum()
        if n_outliers > 0:
            logger.warning(f"Detected {n_outliers} outliers in {col}")
            outliers_found = True

    if not outliers_found:
        logger.info("[OK] No outliers detected")


# ============================================================================
# DATA CLEANING
# ============================================================================
def _clean_data(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Clean and impute missing data using MICE.

    Steps:
      1. Standardize numeric columns
      2. MICE imputation
      3. Reverse standardization
      4. Enforce OHLC consistency

    Args:
        df (pd.DataFrame): OHLCV DataFrame with potential missing values

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    logger.info(f"Cleaning data for {symbol}...")

    ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
    existing_cols = [c for c in ohlcv_cols if c in df.columns]

    # Check if imputation is needed
    if df[existing_cols].isna().sum().sum() == 0:
        logger.info("No missing data - skipping imputation")
        return df

    # Step 1: Standardize
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    df_standardized = df[existing_cols].copy()
    df_standardized[existing_cols] = scaler.fit_transform(
        df[existing_cols]
    )

    # Step 2: MICE Imputation
    try:
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer

        enable_iterative_imputer()

        imputer = IterativeImputer(
            max_iter=MICE_CONFIG['max_iter'],
            random_state=MICE_CONFIG['random_state'],
            verbose=MICE_CONFIG['verbose'],
        )

        df_imputed_std = pd.DataFrame(
            imputer.fit_transform(df_standardized),
            index=df_standardized.index,
            columns=df_standardized.columns,
        )

        logger.info(
            f"MICE imputation complete (max_iter={MICE_CONFIG['max_iter']})"
        )

    except ImportError:
        logger.warning("sklearn.impute not available, using forward fill")
        df_imputed_std = df_standardized.fillna(method='ffill').fillna(
            method='bfill'
        )

    # Step 3: Reverse standardization
    df_imputed = df[existing_cols].copy()
    df_imputed[existing_cols] = scaler.inverse_transform(df_imputed_std)

    # Step 4: Ensure consistency
    df_imputed = _enforce_ohlc_consistency(df_imputed)

    # Preserve non-OHLCV columns
    for col in df.columns:
        if col not in existing_cols:
            df_imputed[col] = df[col]

    logger.info("[OK] Data cleaning complete")
    return df_imputed


def _enforce_ohlc_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce OHLC consistency post-imputation.

    Rules:
      - High = max(Open, Close, High)
      - Low = min(Open, Close, Low)
    """
    df = df.copy()

    # Ensure High >= all prices
    df['high'] = df[['high', 'open', 'close']].max(axis=1)

    # Ensure Low <= all prices
    df['low'] = df[['low', 'open', 'close']].min(axis=1)

    # Ensure volume >= 0
    if 'volume' in df.columns:
        df['volume'] = df['volume'].clip(lower=0)

    return df


# ============================================================================
# NEWS FILTERING
# ============================================================================
def _filter_news_dates(
    df: pd.DataFrame,
    symbol: str,
) -> pd.DataFrame:
    """
    Filter out data on major news/economic announcement dates.

    Requires news_calendar.csv in project root.

    Args:
        df (pd.DataFrame): OHLCV DataFrame
        symbol (str): Symbol name

    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    news_file = Path('news_calendar.csv')
    if not news_file.exists():
        logger.warning(
            "news_calendar.csv not found - skipping news filtering"
        )
        return df

    try:
        news_df = pd.read_csv(news_file)
        news_df['date'] = pd.to_datetime(news_df['date'])
        news_dates = set(news_df['date'].dt.date)

        # Filter
        df_filtered = df[~df.index.date.isin(news_dates)].copy()
        n_removed = len(df) - len(df_filtered)

        logger.info(f"Filtered out {n_removed} candles on news dates")
        return df_filtered

    except Exception as e:
        logger.error(f"Error filtering news dates: {e}")
        return df


if __name__ == '__main__':
    logger.info("Data module imported successfully")
