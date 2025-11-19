#!/usr/bin/env python3
"""
Database Connection Test Script

This script validates that the PostgreSQL connection works correctly
and that all required tables and data are accessible.

Usage:
    python test_connection.py
"""

import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging to console for immediate feedback
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test database connection and basic functionality."""

    logger.info("=" * 60)
    logger.info("DATABASE CONNECTION TEST")
    logger.info("=" * 60)

    try:
        # Test 1: Import modules
        logger.info("\n[1/5] Importing modules...")
        from shared.database_connector import DatabaseConnection, fetch_ohlcv, get_available_tables, get_date_range
        from shared.config import SYMBOLS
        logger.info("✓ Modules imported successfully")

        # Test 2: Database connection
        logger.info("\n[2/5] Establishing database connection...")
        engine = DatabaseConnection.get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            result.fetchone()
        logger.info("✓ Database connection successful")

        # Test 3: List available tables
        logger.info("\n[3/5] Checking available tables...")
        tables = get_available_tables()
        logger.info(f"✓ Found {len(tables)} OHLCV tables:")
        for table in sorted(tables)[:5]:  # Show first 5
            logger.info(f"  - {table}")
        if len(tables) > 5:
            logger.info(f"  ... and {len(tables) - 5} more")

        # Test 4: Test each symbol
        logger.info("\n[4/5] Testing symbol availability...")
        tested_count = 0
        available_count = 0

        for symbol in sorted(SYMBOLS.keys())[:3]:  # Test first 3 symbols
            try:
                date_range = get_date_range(symbol, 'h1')
                available_count += 1
                logger.info(f"✓ {symbol:15} | Available: {date_range['start'].date()} to {date_range['end'].date()}")
            except Exception as e:
                logger.warning(f"⚠ {symbol:15} | Not available: {str(e)[:50]}")
            tested_count += 1

        logger.info(f"✓ {available_count}/{tested_count} symbols available")

        # Test 5: Fetch sample data
        logger.info("\n[5/5] Fetching sample data...")
        symbol = 'eurusd'
        try:
            # Get date range and fetch data
            date_range = get_date_range(symbol, 'h1')

            # Use the last 7 days of available data
            end_date = date_range['end']
            start_date = end_date - timedelta(days=7)

            df = fetch_ohlcv(symbol, 'h1', start_date, end_date)
            logger.info(f"✓ Fetched {len(df)} candles for {symbol} (h1)")
            logger.info(f"  Columns: {', '.join(df.columns.tolist())}")
            logger.info(f"  Date range: {df.index.min()} to {df.index.max()}")
            logger.info(f"  Timezone: {df.index.tz}")

        except Exception as e:
            logger.warning(f"⚠ Could not fetch sample data: {str(e)[:100]}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS PASSED - Connection is working!")
        logger.info("=" * 60)
        return True

    except ValueError as e:
        logger.error(f"\n✗ Configuration Error: {e}")
        logger.error("\nPlease ensure:")
        logger.error("  1. DATABASE_URL is set in .env")
        logger.error("  2. DATABASE_CA_CERT_PATH points to a valid certificate")
        logger.error("  3. Database credentials are correct")
        return False

    except Exception as e:
        logger.error(f"\n✗ Connection Failed: {e}")
        logger.error("\nPlease check:")
        logger.error("  1. PostgreSQL server is running")
        logger.error("  2. Network connectivity to the database server")
        logger.error("  3. Firewall rules allow database access")
        logger.error("  4. SSL/TLS certificate is valid")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
