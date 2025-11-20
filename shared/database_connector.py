"""
Database connector module for fetching raw data from PostgreSQL.

This module handles:
  - Database connection management
  - Raw OHLCV data retrieval
  - Symbol metadata queries
  - Data availability checks

All data is retrieved as-is from the database (UTC timestamps).
Data processing (cleaning, timezone conversion) is handled separately.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List
import ssl

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import NullPool

from shared.config import (
    DATABASE_URL,
    DATABASE_CA_CERT_PATH,
    LOG_LEVEL,
    LOGS_DIR,
    get_table_name,
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
log_file = LOGS_DIR / 'database_connector.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(getattr(logging, LOG_LEVEL))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# ============================================================================
# DATABASE CONNECTION MANAGEMENT
# ============================================================================
class DatabaseConnection:
    """Manages PostgreSQL connection with SSL support."""

    _engine = None

    @classmethod
    def get_engine(cls):
        """
        Get or create SQLAlchemy engine with SSL configuration.

        Returns:
            sqlalchemy.engine.Engine: Database engine instance

        Raises:
            ValueError: If DATABASE_URL or cert path not set
            Exception: If connection fails
        """
        if cls._engine is None:
            logger.info("Initializing database connection...")

            # Prepare connection arguments
            connect_args = {}
            cert_path = Path(DATABASE_CA_CERT_PATH)

            # For psycopg2, CA certificate is passed via sslrootcert parameter
            if cert_path.exists():
                connect_args['sslrootcert'] = str(cert_path)
                logger.info(f"SSL configured with CA cert: {cert_path}")
            else:
                logger.warning(
                    f"CA certificate not found at {cert_path}. "
                    "Connecting without SSL verification."
                )

            try:
                cls._engine = create_engine(
                    DATABASE_URL,
                    connect_args=connect_args,
                    poolclass=NullPool,  # Avoid connection pooling issues
                    echo=False,
                )

                # Test connection
                with cls._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("[OK] Database connection successful")

            except Exception as e:
                logger.error(f"[ERROR] Database connection failed: {e}")
                raise

        return cls._engine

    @classmethod
    def close(cls):
        """Close the database connection."""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            logger.info("Database connection closed")


# ============================================================================
# DATA RETRIEVAL
# ============================================================================
def fetch_ohlcv(
    symbol: str,
    timeframe: str,
    start_date,
    end_date,
    exchange: str = None,
) -> pd.DataFrame:
    """
    Fetch raw OHLCV data from PostgreSQL.

    Data is returned exactly as stored in the database:
      - Timestamps in UTC (TIMESTAMPTZ)
      - No cleaning or transformation applied

    Args:
        symbol (str): Symbol name (e.g., 'eurusd', 'usa500idxusd')
        timeframe (str): Timeframe (m1, m5, h1)
        start_date: Start datetime (inclusive)
        end_date: End datetime (inclusive)
        exchange (str): Exchange for crypto (optional)

    Returns:
        pd.DataFrame: Raw OHLCV data with columns:
                     [timestamp, open, high, low, close, volume]
                     Sorted by timestamp (ascending)

    Raises:
        ValueError: If symbol/timeframe invalid or data not found
        Exception: If database query fails
    """
    logger.info(
        f"fetch_ohlcv(): symbol={symbol}, timeframe={timeframe}, "
        f"start={start_date}, end={end_date}"
    )

    # Get table name
    try:
        table_name = get_table_name(symbol, timeframe, exchange)
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise

    engine = DatabaseConnection.get_engine()

    # Build query
    query = f"""
        SELECT
            timestamp,
            open,
            high,
            low,
            close,
            volume
        FROM
            {table_name}
        WHERE
            timestamp >= %s
            AND timestamp <= %s
        ORDER BY
            timestamp ASC
    """

    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                query,
                conn,
                params=(start_date, end_date),
            )

        if df.empty:
            logger.warning(
                f"No data found for {symbol} {timeframe} "
                f"between {start_date} and {end_date}"
            )
            return pd.DataFrame(
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

        # Ensure timestamp is datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')

        logger.info(
            f"[OK] Fetched {len(df)} candles "
            f"({df.index.min()} to {df.index.max()})"
        )
        return df

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise


# ============================================================================
# SYMBOL METADATA
# ============================================================================
def get_symbol_metadata(symbol: str) -> Dict:
    """
    Fetch metadata for a symbol from symbol_metadata table.

    Args:
        symbol (str): Symbol name

    Returns:
        dict: Metadata with keys:
              - symbol
              - asset_type (crypto/tradfi)
              - total_records
              - last_available_timestamp
              - can_update_from

    Raises:
        ValueError: If symbol not found
        Exception: If query fails
    """
    logger.info(f"Fetching metadata for {symbol}...")

    engine = DatabaseConnection.get_engine()

    query = """
        SELECT
            symbol,
            asset_type,
            total_records,
            last_available_timestamp,
            can_update_from
        FROM
            symbol_metadata
        WHERE
            symbol = %s
    """

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(query),
                {"symbol": symbol.lower()}
            )
            row = result.fetchone()

        if not row:
            raise ValueError(f"Symbol '{symbol}' not found in metadata table")

        metadata = {
            'symbol': row[0],
            'asset_type': row[1],
            'total_records': row[2],
            'last_available_timestamp': row[3],
            'can_update_from': row[4],
        }

        logger.info(f"[OK] Metadata fetched: {metadata['total_records']} records")
        return metadata

    except Exception as e:
        logger.error(f"Error fetching metadata: {e}")
        raise


# ============================================================================
# AVAILABILITY CHECKS
# ============================================================================
def check_symbol_availability(symbol: str, timeframe: str) -> bool:
    """
    Check if data is available for a symbol/timeframe combination.

    Args:
        symbol (str): Symbol name
        timeframe (str): Timeframe

    Returns:
        bool: True if table exists and has data, False otherwise
    """
    engine = DatabaseConnection.get_engine()

    try:
        table_name = get_table_name(symbol, timeframe)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if table_name not in tables:
            logger.warning(f"Table not found: {table_name}")
            return False

        # Check if table has data
        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            )
            count = result.scalar()

        if count == 0:
            logger.warning(f"Table {table_name} is empty")
            return False

        logger.info(f"[OK] {table_name} available ({count} rows)")
        return True

    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return False


def get_available_tables() -> List[str]:
    """
    Get list of all available OHLCV tables in the database.

    Returns:
        list: Table names
    """
    engine = DatabaseConnection.get_engine()

    try:
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()

        # Filter for OHLCV tables (containing 'ohlcv' in name)
        ohlcv_tables = [t for t in all_tables if 'ohlcv' in t.lower()]

        logger.info(f"Found {len(ohlcv_tables)} OHLCV tables")
        return sorted(ohlcv_tables)

    except Exception as e:
        logger.error(f"Error getting available tables: {e}")
        return []


def get_date_range(symbol: str, timeframe: str) -> Dict:
    """
    Get available date range for a symbol/timeframe.

    Args:
        symbol (str): Symbol name
        timeframe (str): Timeframe

    Returns:
        dict: With keys 'start' and 'end' (datetime objects)

    Raises:
        ValueError: If symbol/timeframe not found
    """
    engine = DatabaseConnection.get_engine()

    try:
        table_name = get_table_name(symbol, timeframe)

        query = f"""
            SELECT
                MIN(timestamp) as start,
                MAX(timestamp) as end
            FROM
                {table_name}
        """

        with engine.connect() as conn:
            result = conn.execute(text(query))
            row = result.fetchone()

        if not row or row[0] is None:
            raise ValueError(f"No data found for {symbol} {timeframe}")

        date_range = {
            'start': pd.Timestamp(row[0]),
            'end': pd.Timestamp(row[1]),
        }

        logger.info(
            f"[OK] Date range for {symbol} {timeframe}: "
            f"{date_range['start']} to {date_range['end']}"
        )
        return date_range

    except Exception as e:
        logger.error(f"Error getting date range: {e}")
        raise


if __name__ == '__main__':
    logger.info("Database connector module imported successfully")
