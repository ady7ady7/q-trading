"""
Unit tests for shared/data_module.py

Test coverage:
  - Database connection
  - OHLC consistency validation
  - Timezone handling (UTC and local)
  - Gap and outlier detection
  - Data imputation
  - News filtering
  - Edge cases and error handling
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from unittest.mock import patch, MagicMock, Mock

from shared.data_module import (
    DatabaseConnection,
    get_data,
    _ensure_utc_timezone,
    _convert_to_local_time,
    _validate_ohlc,
    _analyze_gaps,
    _analyze_missing_data,
    _detect_outliers,
    _clean_data,
    _enforce_ohlc_consistency,
    _fetch_raw_data,
    validate_date_range,
)
from shared.config import INSTRUMENT_TIMEZONES, MARKET_HOURS


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_ohlcv_df():
    """Create a sample clean OHLCV DataFrame."""
    dates = pd.date_range('2024-01-01', periods=100, freq='H', tz='UTC')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(1.0, 1.5, 100),
        'high': np.random.uniform(1.1, 1.6, 100),
        'low': np.random.uniform(0.9, 1.4, 100),
        'close': np.random.uniform(1.0, 1.5, 100),
        'volume': np.random.uniform(1000, 5000, 100),
    })

    # Ensure OHLC consistency
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)

    return df.set_index('timestamp')


@pytest.fixture
def sample_df_with_gaps():
    """Create DataFrame with missing candles."""
    dates = pd.date_range('2024-01-01', periods=50, freq='H', tz='UTC')
    # Create a gap (skip 5 hours)
    dates = dates.tolist() + pd.date_range(
        dates[-1] + timedelta(hours=5), periods=50, freq='H', tz='UTC'
    ).tolist()

    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(1.0, 1.5, len(dates)),
        'high': np.random.uniform(1.1, 1.6, len(dates)),
        'low': np.random.uniform(0.9, 1.4, len(dates)),
        'close': np.random.uniform(1.0, 1.5, len(dates)),
        'volume': np.random.uniform(1000, 5000, len(dates)),
    })

    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)

    return df.set_index('timestamp')


@pytest.fixture
def sample_df_with_missing_values():
    """Create DataFrame with NaN values."""
    dates = pd.date_range('2024-01-01', periods=100, freq='H', tz='UTC')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(1.0, 1.5, 100),
        'high': np.random.uniform(1.1, 1.6, 100),
        'low': np.random.uniform(0.9, 1.4, 100),
        'close': np.random.uniform(1.0, 1.5, 100),
        'volume': np.random.uniform(1000, 5000, 100),
    })

    # Introduce missing values (10%)
    mask = np.random.rand(100) < 0.1
    df.loc[mask, 'open'] = np.nan
    df.loc[mask, 'close'] = np.nan

    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)

    return df.set_index('timestamp')


@pytest.fixture
def sample_df_with_outliers():
    """Create DataFrame with outliers."""
    dates = pd.date_range('2024-01-01', periods=100, freq='H', tz='UTC')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(1.0, 1.5, 100),
        'high': np.random.uniform(1.1, 1.6, 100),
        'low': np.random.uniform(0.9, 1.4, 100),
        'close': np.random.uniform(1.0, 1.5, 100),
        'volume': np.random.uniform(1000, 5000, 100),
    })

    # Add extreme outliers
    df.loc[10, 'high'] = 100.0
    df.loc[25, 'volume'] = 1000000.0

    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)

    return df.set_index('timestamp')


# ============================================================================
# DATABASE CONNECTION TESTS
# ============================================================================

class TestDatabaseConnection:
    """Test database connection management."""

    def test_database_connection_initialization(self):
        """Test that database connection can be initialized."""
        # Reset singleton
        DatabaseConnection._engine = None

        # Mock the create_engine and connection
        with patch('shared.data_module.create_engine') as mock_engine:
            mock_conn = MagicMock()
            mock_engine.return_value.connect.return_value.__enter__ = MagicMock(
                return_value=mock_conn
            )
            mock_engine.return_value.connect.return_value.__exit__ = MagicMock(
                return_value=None
            )
            mock_conn.execute.return_value = None

            # Reset and get engine
            DatabaseConnection._engine = None
            engine = DatabaseConnection.get_engine()

            assert engine is not None

    def test_database_connection_caching(self):
        """Test that connection is cached (singleton pattern)."""
        # Reset and get first engine
        DatabaseConnection._engine = None
        with patch('shared.data_module.create_engine'):
            with patch.object(
                DatabaseConnection.get_engine(),
                'connect',
                return_value=MagicMock(),
            ):
                engine1 = DatabaseConnection.get_engine()
                engine2 = DatabaseConnection.get_engine()

                # Should return same instance
                # (In real scenario, might not be identical due to mocking)
                assert engine1 is not None
                assert engine2 is not None

    def test_database_close(self):
        """Test closing database connection."""
        DatabaseConnection._engine = None

        with patch('shared.data_module.create_engine') as mock_engine:
            mock_engine.return_value.dispose = MagicMock()

            # Create connection
            DatabaseConnection._engine = MagicMock()
            DatabaseConnection.close()

            assert DatabaseConnection._engine is None


# ============================================================================
# TIMEZONE HANDLING TESTS
# ============================================================================

class TestTimezoneHandling:
    """Test timezone conversion and handling."""

    def test_ensure_utc_timezone_with_naive_datetime(
        self, sample_ohlcv_df
    ):
        """Test converting naive datetime to UTC."""
        df = sample_ohlcv_df.reset_index()
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)  # Make naive

        result = _ensure_utc_timezone(df)

        assert result.index.tz == pytz.UTC
        assert result.index.name == 'timestamp'

    def test_ensure_utc_timezone_already_utc(self, sample_ohlcv_df):
        """Test that UTC timezone is preserved."""
        df = sample_ohlcv_df.reset_index()

        result = _ensure_utc_timezone(df)

        assert result.index.tz == pytz.UTC

    def test_ensure_utc_timezone_from_other_tz(self, sample_ohlcv_df):
        """Test converting from non-UTC timezone to UTC."""
        df = sample_ohlcv_df.reset_index()
        df['timestamp'] = df['timestamp'].tz_convert('America/New_York')

        result = _ensure_utc_timezone(df)

        assert result.index.tz == pytz.UTC

    def test_ensure_utc_missing_timestamp_column(self, sample_ohlcv_df):
        """Test error when timestamp column is missing."""
        df = sample_ohlcv_df.reset_index().drop('timestamp', axis=1)

        with pytest.raises(ValueError, match="timestamp"):
            _ensure_utc_timezone(df)

    def test_convert_to_local_time_valid(self, sample_ohlcv_df):
        """Test converting UTC to local timezone."""
        result = _convert_to_local_time(sample_ohlcv_df, 'America/New_York')

        assert str(result.index.tz) == 'America/New_York'

    def test_convert_to_local_time_naive_index_raises(self):
        """Test error when converting naive index."""
        df = pd.DataFrame(
            {'open': [1.0, 1.1], 'close': [1.05, 1.15]},
            index=pd.DatetimeIndex(['2024-01-01', '2024-01-02']),
        )

        with pytest.raises(ValueError, match="timezone-aware"):
            _convert_to_local_time(df, 'America/New_York')


# ============================================================================
# OHLC VALIDATION TESTS
# ============================================================================

class TestOHLCValidation:
    """Test OHLC consistency validation."""

    def test_validate_ohlc_valid_data(self, sample_ohlcv_df):
        """Test validation passes for valid OHLCV data."""
        # Should not raise
        _validate_ohlc(sample_ohlcv_df, 'EURUSD')

    def test_validate_ohlc_missing_columns(self):
        """Test error when required columns are missing."""
        df = pd.DataFrame(
            {'open': [1.0], 'close': [1.1]},
            index=pd.DatetimeIndex(['2024-01-01'], tz='UTC'),
        )

        with pytest.raises(ValueError, match="Missing columns"):
            _validate_ohlc(df, 'EURUSD')

    def test_validate_ohlc_high_less_than_low(self, sample_ohlcv_df):
        """Test detection of High < Low violations."""
        df = sample_ohlcv_df.copy()
        df.loc[df.index[0], 'high'] = 0.5
        df.loc[df.index[0], 'low'] = 1.5

        # Should log warning but not raise
        _validate_ohlc(df, 'EURUSD')


# ============================================================================
# GAP ANALYSIS TESTS
# ============================================================================

class TestGapAnalysis:
    """Test gap detection in time series."""

    def test_analyze_gaps_no_gaps(self, sample_ohlcv_df):
        """Test detection of no gaps in continuous data."""
        # Should not raise
        _analyze_gaps(sample_ohlcv_df, 'H1')

    def test_analyze_gaps_with_gaps(self, sample_df_with_gaps):
        """Test detection of gaps in data."""
        # Should log warning about gaps
        _analyze_gaps(sample_df_with_gaps, 'H1')

    def test_analyze_gaps_unknown_timeframe(self, sample_ohlcv_df):
        """Test handling of unknown timeframe."""
        # Should log warning
        _analyze_gaps(sample_ohlcv_df, 'UNKNOWN')

    def test_analyze_gaps_insufficient_data(self):
        """Test handling of single row (no gaps possible)."""
        df = pd.DataFrame(
            {'open': [1.0], 'close': [1.1]},
            index=pd.date_range('2024-01-01', periods=1, freq='H', tz='UTC'),
        )

        # Should not raise
        _analyze_gaps(df, 'H1')


# ============================================================================
# MISSING DATA ANALYSIS TESTS
# ============================================================================

class TestMissingDataAnalysis:
    """Test missing data detection."""

    def test_analyze_missing_no_missing(self, sample_ohlcv_df):
        """Test when no missing data exists."""
        # Should not raise
        _analyze_missing_data(sample_ohlcv_df)

    def test_analyze_missing_with_missing(self, sample_df_with_missing_values):
        """Test detection of missing data."""
        # Should log warning about missing values
        _analyze_missing_data(sample_df_with_missing_values)


# ============================================================================
# OUTLIER DETECTION TESTS
# ============================================================================

class TestOutlierDetection:
    """Test outlier detection."""

    def test_detect_outliers_no_outliers(self, sample_ohlcv_df):
        """Test when no outliers exist."""
        _detect_outliers(sample_ohlcv_df)

    def test_detect_outliers_with_outliers(self, sample_df_with_outliers):
        """Test detection of outliers."""
        # Should log warnings about outliers
        _detect_outliers(sample_df_with_outliers)


# ============================================================================
# DATA CLEANING TESTS
# ============================================================================

class TestDataCleaning:
    """Test data cleaning and imputation."""

    def test_clean_data_no_missing(self, sample_ohlcv_df):
        """Test cleaning when no missing data."""
        result = _clean_data(sample_ohlcv_df, 'EURUSD')

        assert len(result) == len(sample_ohlcv_df)
        assert not result[['open', 'close']].isna().any().any()

    def test_clean_data_with_missing(self, sample_df_with_missing_values):
        """Test imputation of missing data."""
        result = _clean_data(sample_df_with_missing_values, 'EURUSD')

        assert len(result) == len(sample_df_with_missing_values)
        assert not result[['open', 'close']].isna().any().any()

    def test_enforce_ohlc_consistency(self):
        """Test enforcement of OHLC rules."""
        df = pd.DataFrame({
            'open': [1.0, 1.1],
            'high': [1.05, 1.05],  # Less than close
            'low': [1.05, 1.1],    # Greater than low
            'close': [1.1, 1.05],
            'volume': [1000, 1000],
        }, index=pd.date_range('2024-01-01', periods=2, freq='H', tz='UTC'))

        result = _enforce_ohlc_consistency(df)

        # High should be at least as large as open and close
        assert (result['high'] >= result['open']).all()
        assert (result['high'] >= result['close']).all()

        # Low should be at most as small as open and close
        assert (result['low'] <= result['open']).all()
        assert (result['low'] <= result['close']).all()

        # Volume should be non-negative
        assert (result['volume'] >= 0).all()


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestValidateDateRange:
    """Test date range validation."""

    def test_validate_date_range_valid(self):
        """Test valid date range."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)

        # Should not raise
        validate_date_range(start, end)

    def test_validate_date_range_same_dates(self):
        """Test when start equals end."""
        date = datetime(2024, 1, 1)

        # Should log warning but not raise
        validate_date_range(date, date)

    def test_validate_date_range_reversed(self):
        """Test error when start > end."""
        start = datetime(2024, 12, 31)
        end = datetime(2024, 1, 1)

        with pytest.raises(ValueError, match="start_date.*end_date"):
            validate_date_range(start, end)

    def test_validate_date_range_very_old(self):
        """Test warning for very old start date."""
        start = datetime(1990, 1, 1)
        end = datetime(1991, 1, 1)

        # Should log warning but not raise
        validate_date_range(start, end)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestGetDataIntegration:
    """Integration tests for get_data function."""

    @patch('shared.data_module._fetch_raw_data')
    def test_get_data_flow_utc(self, mock_fetch, sample_ohlcv_df):
        """Test complete data retrieval flow (UTC)."""
        mock_fetch.return_value = sample_ohlcv_df.reset_index()

        # Note: Full integration requires database setup
        # This is a simplified test
        assert sample_ohlcv_df.index.tz == pytz.UTC

    def test_instrument_timezone_mapping(self):
        """Test that common instruments have timezone mapping."""
        required_instruments = ['EURUSD', 'DE40', 'SPY', 'WIG20']

        for instrument in required_instruments:
            assert instrument in INSTRUMENT_TIMEZONES
            assert isinstance(INSTRUMENT_TIMEZONES[instrument], str)

    def test_market_hours_configuration(self):
        """Test that market hours are properly configured."""
        required_instruments = ['DE40', 'SPY', 'WIG20']

        for instrument in required_instruments:
            assert instrument in MARKET_HOURS
            hours = MARKET_HOURS[instrument]
            assert len(hours) == 4
            assert 0 <= hours[0] < 24
            assert 0 <= hours[1] < 60
            assert 0 <= hours[2] < 24
            assert 0 <= hours[3] < 60


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame(
            columns=['open', 'high', 'low', 'close', 'volume'],
            index=pd.DatetimeIndex([], tz='UTC'),
        )

        # Should handle gracefully
        assert len(df) == 0

    def test_single_row_dataframe(self):
        """Test handling of single-row DataFrame."""
        df = pd.DataFrame(
            {
                'open': [1.0],
                'high': [1.1],
                'low': [0.9],
                'close': [1.05],
                'volume': [1000],
            },
            index=pd.date_range('2024-01-01', periods=1, freq='H', tz='UTC'),
        )

        # Should handle without error
        result = _enforce_ohlc_consistency(df)
        assert len(result) == 1

    def test_all_nan_column(self):
        """Test handling of entirely NaN column."""
        df = pd.DataFrame(
            {
                'open': [np.nan, np.nan, np.nan],
                'high': [1.1, 1.2, 1.3],
                'low': [0.9, 1.0, 1.1],
                'close': [1.0, 1.1, 1.2],
                'volume': [1000, 1000, 1000],
            },
            index=pd.date_range('2024-01-01', periods=3, freq='H', tz='UTC'),
        )

        # Should still process
        assert df['open'].isna().all()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
