# Data Pipeline Architecture

Complete technical reference for the data pipeline modules.

---

## **Overview**

The data pipeline has two separate, focused modules:

1. **`database_connector.py`** — PostgreSQL operations
2. **`data_module.py`** — Data processing

This separation ensures clean architecture, testability, and flexibility.

---

## **database_connector.py**

Handles all PostgreSQL communication and raw data retrieval.

### **DatabaseConnection Class**

Singleton connection manager with SSL/TLS support.

```python
from shared.database_connector import DatabaseConnection

# Get or create engine (cached)
engine = DatabaseConnection.get_engine()

# Close connection
DatabaseConnection.close()
```

### **fetch_ohlcv()**

Fetch raw OHLCV data from database.

```python
from shared.database_connector import fetch_ohlcv
from datetime import datetime

df = fetch_ohlcv(
    symbol='eurusd',
    timeframe='h1',
    start_date=datetime(2024, 11, 1),
    end_date=datetime(2024, 11, 30),
    exchange=None,  # Optional for crypto (defaults to binance)
)

# Returns:
#   DataFrame with columns: [timestamp, open, high, low, close, volume]
#   Timestamp: UTC (TIMESTAMPTZ)
#   No cleaning, no transformation — raw data only
```

### **check_symbol_availability()**

Quick check if data exists for a symbol/timeframe.

```python
from shared.database_connector import check_symbol_availability

available = check_symbol_availability('eurusd', 'h1')
# Returns: True/False
```

### **get_symbol_metadata()**

Query symbol_metadata table.

```python
from shared.database_connector import get_symbol_metadata

metadata = get_symbol_metadata('eurusd')

# Returns dict:
# {
#   'symbol': 'eurusd',
#   'asset_type': 'tradfi',
#   'total_records': 50000,
#   'last_available_timestamp': datetime(...),
#   'can_update_from': datetime(...)
# }
```

### **get_date_range()**

Get min/max timestamp available for a symbol/timeframe.

```python
from shared.database_connector import get_date_range

date_range = get_date_range('eurusd', 'h1')

# Returns dict:
# {
#   'start': datetime(2024, 1, 1, 0, 0, ...),
#   'end': datetime(2024, 11, 30, 23, 0, ...)
# }
```

### **get_available_tables()**

List all OHLCV tables in the database.

```python
from shared.database_connector import get_available_tables

tables = get_available_tables()

# Returns: ['eurusd_m1_tradfi_ohlcv', 'eurusd_h1_tradfi_ohlcv', ...]
```

---

## **data_module.py**

Handles data processing: validation, cleaning, imputation, timezone conversion.

### **process_data()**

Main entry point. Complete processing pipeline in one function.

```python
from shared.data_module import process_data

df_clean = process_data(
    df=df_raw,                  # Input: raw OHLCV DataFrame
    symbol='eurusd',            # Symbol name (for config lookup)
    timeframe='h1',             # Timeframe
    local_time=False,           # Convert to local timezone
    exclude_news=False,         # Filter news dates
)

# Returns:
#   Clean DataFrame with:
#   - UTC or local timezone-aware index (depending on local_time)
#   - Columns: [open, high, low, close, volume]
#   - No missing data (imputed if necessary)
#   - Valid OHLC structure
```

### **Processing Pipeline**

1. **Timezone Localization**
   - Ensures index is UTC timezone-aware
   - Converts if needed

2. **OHLC Validation**
   - Checks High ≥ Low, High ≥ Open/Close, Low ≤ Open/Close
   - Warns on negative prices or NaN values
   - Logs violations but continues

3. **Diagnostics**
   - **Gap Analysis**: Detects missing candles
   - **Missing Data**: Calculates % NaN per column
   - **Outlier Detection**: Uses MAD (Median Absolute Deviation) and IQR (Interquartile Range) methods

4. **Data Cleaning (MICE)**
   - Standardizes numeric columns (z-score)
   - Uses Multivariate Iterative Imputation by Chained Equations (MICE)
   - Reverses standardization
   - Enforces OHLC consistency post-imputation

5. **Timezone Conversion** (if `local_time=True`)
   - Converts from UTC to instrument's local timezone
   - Uses configuration from `shared/config.py`
   - Automatically handles DST

6. **News Filtering** (if `exclude_news=True`)
   - Reads `news_calendar.csv` from project root
   - Removes entire days with major news events
   - Requires file format: date,event,currency,impact

---

## **Important: Timezone Offset for DAX Data**

### **Context**

Database stores all timestamps in UTC (TIMESTAMPTZ). For DAX (deuidxeur):
- **Database**: Stores timestamps in UTC format
- **TradingView FDAX**: Shows prices with wall-clock times (Berlin local time)
- **Offset discovered**: Database UTC times correspond to TradingView times **2 hours ahead**

**Example:**
- Database UTC: `13:00:00 UTC`
- Converted to Berlin: `15:00:00 CEST` (during summer) / `15:00:00 CET` (during winter... wait, that's wrong)

Actually, let me correct this:
- Database UTC: `13:00:00 UTC`
- Convert to Berlin (+02:00 in October): `15:00:00 CEST`
- This matches TradingView FDAX display at 15:00

**Why the offset?**
- DAX Spot Index (deuidxeur) and DAX Futures (FDAX) have different trading characteristics
- Our data represents the spot index, which has different price levels than FDAX
- When comparing against TradingView FDAX candles, remember this is a different instrument

### **Practical Usage**

When performing research:
1. **M1 data with early hours**: If you want to include pre-market or early session hours, fetch from 07:00 UTC onwards
   - 07:00 UTC = 09:00 CEST/CET (Berlin local) = 09:00 on TradingView FDAX display
2. **For spot-checking candles**: Remember the 2-hour wall-clock offset between our UTC timestamps and TradingView FDAX display
3. **For internal analysis**: No adjustment needed—data is internally consistent and properly sequenced

### **Configuration**

Market hours for DAX (deuidxeur) in `config.py`:
```python
'deuidxeur': {
    'timezone': 'Europe/Berlin',
    'market_open': time(9, 0),      # 09:00 Berlin local
    'market_close': time(17, 30),   # 17:30 Berlin local
}
```

This is 07:00-15:30 UTC (accounting for +02:00 summer offset) or 08:00-16:30 UTC (with +01:00 winter offset).

---

## **config.py**

Centralized configuration.

### **Symbol Configuration**

Each symbol defined with:

```python
SYMBOLS = {
    'eurusd': {
        'name': 'Euro/US Dollar',
        'asset_type': 'tradfi',           # 'tradfi' or 'crypto'
        'timezone': 'Europe/London',      # pytz format
        'market_open': time(0, 0),        # datetime.time object
        'market_close': time(23, 59),
    },
    ...
}
```

### **Helper Functions**

```python
from shared.config import (
    get_symbol_info,          # Get symbol metadata
    is_tradfi_symbol,         # Check if TradFi
    is_crypto_symbol,         # Check if Crypto
    get_table_name,           # Generate table name
)

# Examples:
info = get_symbol_info('eurusd')
# Returns: {'name': '...', 'asset_type': 'tradfi', 'timezone': '...', ...}

table = get_table_name('eurusd', 'h1')
# Returns: 'eurusd_h1_tradfi_ohlcv'

table = get_table_name('btcusdt', 'h1')
# Returns: 'btcusdt_h1_binance_crypto_ohlcv'

is_tradfi = is_tradfi_symbol('eurusd')   # True
is_crypto = is_crypto_symbol('btcusdt')  # True
```

### **Imputation Configuration**

```python
MICE_CONFIG = {
    'max_iter': 10,           # Iterations for convergence
    'random_state': 42,       # Fixed seed for reproducibility
    'verbose': 0,             # Logging verbosity
}

OUTLIER_THRESHOLD_MAD = 3.0   # Median Absolute Deviation (3σ)
OUTLIER_THRESHOLD_IQR = 1.5   # Interquartile Range (Tukey method)
GAP_TOLERANCE_PERCENT = 30.0  # Warn if > 30% missing
```

---

## **Database Schema**

### **Table Naming**

**TradFi:**
```
{symbol}_{timeframe}_tradfi_ohlcv
Example: eurusd_h1_tradfi_ohlcv
```

**Crypto:**
```
{symbol}_{timeframe}_{exchange}_crypto_ohlcv
Example: btcusdt_h1_binance_crypto_ohlcv
```

### **OHLCV Table Structure**

```sql
CREATE TABLE eurusd_h1_tradfi_ohlcv (
    timestamp TIMESTAMPTZ PRIMARY KEY,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);
```

**Constraints:**
- `timestamp`: TIMESTAMPTZ (UTC, not NULL)
- `open, high, low, close`: NUMERIC (positive)
- `volume`: BIGINT (non-negative)
- High ≥ max(Open, Close)
- Low ≤ min(Open, Close)

### **Symbol Metadata Table**

```sql
CREATE TABLE symbol_metadata (
    symbol VARCHAR PRIMARY KEY,
    asset_type VARCHAR,              -- 'tradfi' or 'crypto'
    total_records BIGINT,
    last_available_timestamp TIMESTAMPTZ,
    can_update_from TIMESTAMPTZ
);
```

---

## **Common Workflows**

### **Fetch and Process Single Symbol**

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data
from datetime import datetime

# Fetch
df_raw = fetch_ohlcv('eurusd', 'h1', datetime(2024, 11, 1), datetime(2024, 11, 30))

# Process
df_clean = process_data(df_raw, 'eurusd', 'h1', local_time=True)

# Use
print(df_clean.head())
```

### **Process Multiple Symbols**

```python
from shared.database_connector import fetch_ohlcv, check_symbol_availability
from shared.data_module import process_data
from datetime import datetime

symbols = ['eurusd', 'usa500idxusd', 'btcusdt']
start = datetime(2024, 11, 1)
end = datetime(2024, 11, 30)

for symbol in symbols:
    if not check_symbol_availability(symbol, 'h1'):
        print(f"Skip {symbol}: Not available")
        continue

    df_raw = fetch_ohlcv(symbol, 'h1', start, end)
    df_clean = process_data(df_raw, symbol, 'h1', local_time=True)

    print(f"{symbol}: Processed {len(df_clean)} candles")
```

### **With Availability Check**

```python
from shared.database_connector import get_date_range, fetch_ohlcv
from shared.data_module import process_data

symbol = 'eurusd'
timeframe = 'h1'

# Check availability
date_range = get_date_range(symbol, timeframe)
print(f"Available: {date_range['start']} to {date_range['end']}")

# Fetch and process
df_raw = fetch_ohlcv(symbol, timeframe, date_range['start'], date_range['end'])
df_clean = process_data(df_raw, symbol, timeframe, local_time=True)
```

---

## **Error Handling**

### **Database Connection Errors**

```python
from shared.database_connector import DatabaseConnection

try:
    engine = DatabaseConnection.get_engine()
except ValueError as e:
    print(f"Configuration error: {e}")  # DATABASE_URL not set
except Exception as e:
    print(f"Connection failed: {e}")    # Network, auth, etc.
```

### **Data Fetching Errors**

```python
from shared.database_connector import fetch_ohlcv

try:
    df = fetch_ohlcv('invalid_symbol', 'h1', ...)
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Query failed: {e}")
```

### **Processing Errors**

```python
from shared.data_module import process_data

try:
    df_clean = process_data(df_raw, 'unknown_symbol', 'h1')
except ValueError as e:
    print(f"Symbol not configured: {e}")
```

---

## **Logging**

### **Log Files**

- `logs/database_connector.log` — All database operations
- `logs/data_module.log` — All data processing operations

### **Log Levels** (set in `.env`)

```
LOG_LEVEL=DEBUG     # All details (verbose)
LOG_LEVEL=INFO      # Standard (default)
LOG_LEVEL=WARNING   # Errors and warnings only
```

### **Example Output**

```
2024-11-19 12:34:56,789 - shared.database_connector - INFO - ✓ Database connection successful
2024-11-19 12:34:57,012 - shared.database_connector - INFO - ✓ Fetched 744 candles
2024-11-19 12:34:57,100 - shared.data_module - INFO - process_data(): symbol=eurusd, timeframe=h1...
2024-11-19 12:34:57,102 - shared.data_module - INFO - ✓ OHLC validation complete
2024-11-19 12:34:57,104 - shared.data_module - INFO - ✓ No gaps detected
2024-11-19 12:34:57,106 - shared.data_module - INFO - ✓ No missing data
2024-11-19 12:34:57,110 - shared.data_module - INFO - Converted to local timezone: Europe/London
2024-11-19 12:34:57,111 - shared.data_module - INFO - ✓ Data processing complete: 744 candles
```

---

## **Reproducibility**

All operations are deterministic and reproducible:

- ✓ Fixed random seeds (`random_state=42`)
- ✓ Logged parameters (max_iter, estimator type, thresholds)
- ✓ MICE imputation is deterministic with fixed seed
- ✓ Timezone conversion handles DST correctly
- ✓ All diagnostics logged

**Running the same code with same inputs → identical output every time.**

