# q-trading: Quantitative Trading Hub

A production-ready Python framework for quantitative trading research and backtesting. Clean architecture, reproducible analysis, zero tolerance for bullshit.

---

## **Quick Start**

### **1. Setup**

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with your PostgreSQL credentials:
# DATABASE_URL=postgresql://user:password@host:port/db
# DATABASE_CA_CERT_PATH=./certs/ca-certificate.crt
# LOG_LEVEL=INFO
```

### **2. Fetch and Process Data**

```python
from shared.database_connector import fetch_ohlcv, check_symbol_availability
from shared.data_module import process_data
from datetime import datetime

# Check availability
if not check_symbol_availability('eurusd', 'h1'):
    print("Data not available")
    exit()

# Fetch raw data
df_raw = fetch_ohlcv(
    symbol='eurusd',
    timeframe='h1',
    start_date=datetime(2024, 11, 1),
    end_date=datetime(2024, 11, 30),
)

# Process (validate, clean, impute, convert timezone)
df_clean = process_data(
    df=df_raw,
    symbol='eurusd',
    timeframe='h1',
    local_time=True,        # Convert to Europe/London
    exclude_news=False,     # Don't filter news dates
)

# Ready for analysis
print(df_clean.head())
print(df_clean.index.tz)  # Europe/London
```

---

## **Project Structure**

```
.
├── shared/
│   ├── config.py                  # Configuration, symbols, timezones
│   ├── database_connector.py      # PostgreSQL operations
│   ├── data_module.py             # Data processing (validate, clean, impute)
│   ├── engine.py                  # Backtester (Sprint 3)
│   └── reporting.py               # Metrics & reporting (Sprint 3)
├── quant_lab/
│   └── notebooks/                 # Research Jupyter notebooks
│       ├── CHAR_DE40_Trend_And_Range.ipynb
│       ├── PHENOM_EURUSD_IB_Stats.ipynb
│       └── ANALYSIS_LINEAR_REGRESSION.ipynb
├── vector_bt/
│   ├── strategies/                # Strategy implementations
│   ├── main.py                    # Strategy runner
│   └── sweep.py                   # Parameter optimization
├── docs/
│   ├── DATA_PIPELINE.md           # Architecture & API reference
│   ├── DATA_CLEANING.md           # Data cleaning procedures
│   └── TIMEZONE.md                # Timezone handling details
├── tests/
│   └── test_*.py                  # Unit tests
├── certs/
│   └── ca-certificate.crt         # PostgreSQL SSL certificate
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## **Core Modules**

### **`shared/config.py`**
Centralized configuration for the entire project.

**Available Symbols (14):**

| TradFi (12) | Crypto (2) |
|---|---|
| `deuidxeur` (DAX) | `btcusdt` |
| `usa500idxusd` (S&P 500) | `ethusdt` |
| `usatechidxusd` (Nasdaq) |  |
| `usa30idxusd` (Dow Jones) |  |
| `eurusd`, `eurjpy`, `usdcad`, `nzdcad`, `gbpusd` (Forex) |  |
| `xauusd` (Gold), `xagusd` (Silver), `lightcmdusd` (Oil) |  |

**Available Timeframes:** `m1`, `m5`, `h1`

**Helper Functions:**
```python
from shared.config import (
    get_symbol_info,        # Get symbol metadata
    is_tradfi_symbol,       # Check if TradFi
    is_crypto_symbol,       # Check if Crypto
    get_table_name,         # Generate table name
)
```

### **`shared/database_connector.py`**
Raw data retrieval from PostgreSQL.

**Main Functions:**
```python
# Fetch OHLCV data
fetch_ohlcv(symbol, timeframe, start_date, end_date)

# Check if data exists
check_symbol_availability(symbol, timeframe)

# Query metadata
get_symbol_metadata(symbol)
get_date_range(symbol, timeframe)
get_available_tables()

# Connection management
DatabaseConnection.get_engine()    # Singleton with SSL support
DatabaseConnection.close()
```

### **`shared/data_module.py`**
Data processing: validation, cleaning, imputation, timezone conversion.

**Main Function:**
```python
# Complete data processing pipeline
process_data(df, symbol, timeframe, local_time=False, exclude_news=False)
```

**Processing Steps:**
1. Timezone localization (UTC)
2. OHLC consistency validation
3. Gap & outlier diagnostics
4. MICE imputation (if missing data exists)
5. Timezone conversion (if `local_time=True`)
6. News calendar filtering (if `exclude_news=True`)

---

## **Database Schema**

### **Table Naming Convention**

**TradFi:** `{symbol}_{timeframe}_tradfi_ohlcv`
```
Example: eurusd_h1_tradfi_ohlcv
```

**Crypto:** `{symbol}_{timeframe}_{exchange}_crypto_ohlcv`
```
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

### **Symbol Metadata Table**

```sql
CREATE TABLE symbol_metadata (
    symbol VARCHAR PRIMARY KEY,
    asset_type VARCHAR,           -- 'tradfi' or 'crypto'
    total_records BIGINT,
    last_available_timestamp TIMESTAMPTZ,
    can_update_from TIMESTAMPTZ
);
```

---

## **Development Sprints**

### **Sprint 1: Data Pipeline** ✓ COMPLETE
- PostgreSQL connection with SSL/TLS
- Raw OHLCV data fetching
- Data validation & diagnostics
- MICE imputation for missing data
- Timezone handling (UTC ↔ Local)
- News calendar filtering
- Comprehensive logging

### **Sprint 2: Research** (Next)
- quant-lab environment setup
- DE40 characteristics analysis
- EURUSD Initial Balance breakout study
- Linear regression analysis

### **Sprint 3: Backtester** (Planned)
- Vectorized backtesting engine
- Position sizing (Fixed Fractional, Kelly Criterion)
- Performance metrics & reporting
- First strategy implementation

### **Sprint 4: Optimization** (Planned)
- Portfolio simulation
- Parameter optimization
- Walk-Forward analysis

---

## **Configuration**

### **Environment Variables** (`.env`)

```bash
DATABASE_URL=postgresql://user:password@host:port/database_name
DATABASE_CA_CERT_PATH=./certs/ca-certificate.crt
LOG_LEVEL=INFO
```

### **Data Cleaning Settings** (`config.py`)

```python
# MICE Imputation
MICE_CONFIG = {
    'max_iter': 10,           # Convergence iterations
    'random_state': 42,       # Reproducible
}

# Outlier Detection Thresholds
OUTLIER_THRESHOLD_MAD = 3.0   # Median Absolute Deviation
OUTLIER_THRESHOLD_IQR = 1.5   # Interquartile Range

# Data Quality
GAP_TOLERANCE_PERCENT = 30.0  # Warn if > 30% missing
```

---

## **Logging**

Log files created in `logs/`:
- `database_connector.log` — Database operations
- `data_module.log` — Data processing operations

Set verbosity in `.env`:
```
LOG_LEVEL=DEBUG     # All details
LOG_LEVEL=INFO      # Standard (default)
LOG_LEVEL=WARNING   # Errors only
```

---

## **Common Tasks**

### **Check Data Availability**

```python
from shared.database_connector import get_date_range, check_symbol_availability

# Quick check
if check_symbol_availability('eurusd', 'h1'):
    print("Data is available")

# Get date range
range_dict = get_date_range('eurusd', 'h1')
print(f"Data from {range_dict['start']} to {range_dict['end']}")
```

### **Get Symbol Information**

```python
from shared.config import get_symbol_info

info = get_symbol_info('eurusd')
print(f"Timezone: {info['timezone']}")
print(f"Asset type: {info['asset_type']}")
print(f"Market hours: {info['market_open']} - {info['market_close']}")
```

### **List All Available Tables**

```python
from shared.database_connector import get_available_tables

tables = get_available_tables()
for table in sorted(tables):
    print(table)
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

---

## **Troubleshooting**

### **PostgreSQL Connection Fails**

Check:
1. `.env` file exists with `DATABASE_URL`
2. PostgreSQL server is running
3. Certificate path in `.env` → `DATABASE_CA_CERT_PATH`
4. Certificate file exists: `certs/ca-certificate.crt`

**Test connection:**
```bash
python -c "from shared.database_connector import DatabaseConnection; DatabaseConnection.get_engine(); print('✓ Connected')"
```

### **No Data Found**

Check:
1. Symbol is valid: `get_available_tables()`
2. Date range has data: `get_date_range(symbol, timeframe)`
3. Table exists: `check_symbol_availability(symbol, timeframe)`

### **Data Quality Issues**

Check logs:
```bash
tail -f logs/data_module.log
```

Look for:
- `% missing` — NaN percentage
- Outlier counts
- Gap sizes
- Imputation statistics

---

## **Code Quality Standards**

- ✓ PEP 8 compliant
- ✓ Type hints throughout
- ✓ Comprehensive docstrings
- ✓ Single Responsibility Principle
- ✓ No circular dependencies
- ✓ Error handling & logging
- ✓ Reproducible & deterministic

---

## **Contributing**

When adding features:

1. Follow the code structure (separate concerns)
2. Add type hints and docstrings
3. Include logging statements
4. Write tests
5. Update `docs/` files
6. Update relevant `CHECKLIST.md` entries

---

**Status:** Sprint 1 Complete ✓ | Ready for Sprint 2
