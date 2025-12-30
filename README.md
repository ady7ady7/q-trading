# q-trading: Quantitative Research Lab

A Python framework for quantitative trading research. Currently focused on hypothesis generation and statistical validation using clean data pipelines. Backtesting is conducted externally (cTrader/Pinescript).

---

## **Quick Start**

### **1. Setup Virtual Environment**

```bash
# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate.bat
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configure Environment**

```bash
# Create .env file with your PostgreSQL credentials:
# DATABASE_URL=postgresql://user:password@host:port/db?sslmode=require
# DATABASE_CA_CERT_PATH=./certs/ca-certificate.crt
# LOG_LEVEL=INFO

# Test connection
python test_connection.py
```

### **3. Fetch and Process Data**

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
│   └── data_module.py             # Data processing (validate, clean, impute)
├── quant_lab/
│   └── notebooks/                 # Research Jupyter notebooks (14 completed)
│       ├── CHAR_DE40_*.ipynb      # DAX characteristics & patterns
│       └── research_index.md      # Research summary & findings
├── tests/
│   └── test_*.py                  # Unit tests
├── certs/
│   └── ca-certificate.crt         # PostgreSQL SSL certificate
├── devlog.md                      # Development log & ideas
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

**Note:** Backtesting modules (engine, strategies, optimization) will be added later. Current focus is research and validation.

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
2. Timezone conversion to market local time
3. Market hours filtering (RTH only)
4. OHLC consistency validation
5. Gap & outlier diagnostics
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

## **Current Development Stage**

### **Phase 1: Data Pipeline** ✓ COMPLETE
- PostgreSQL connection with SSL/TLS
- Raw OHLCV data fetching
- Timezone handling (UTC → Market local time)
- Market hours filtering (RTH only)
- Data validation & diagnostics
- News calendar filtering
- Comprehensive logging

### **Phase 2: Research** ✓ ONGOING (Current Focus)
- **14 research notebooks completed** analyzing DAX intraday patterns
- Key findings: 65% continuation edge (Quiet regime + Strong UP first hour)
- Pivot point conditional probability studies (standard & local)
- Regime-specific pattern analysis
- **See:** [quant_lab/notebooks/research_index.md](quant_lab/notebooks/research_index.md) for full research summary

### **Phase 3: Backtesting** (Future)
Currently backtesting hypotheses externally using:
- **cTrader** (live/demo execution)
- **Pinescript** (TradingView validation)

Python backtesting modules (vectorized engine, position sizing, optimization) will be added later if needed.

### **Workflow**
1. **Research (Python)**: Hypothesis generation, statistical validation, pattern discovery
2. **Backtest (External)**: Strategy validation in cTrader/Pinescript
3. **Live Trading (External)**: Execution on validated strategies

---

## **Configuration**

### **Environment Variables** (`.env`)

```bash
DATABASE_URL=postgresql://user:password@host:port/database_name
DATABASE_CA_CERT_PATH=./certs/ca-certificate.crt
LOG_LEVEL=INFO
```

### **Data Quality Settings** (`config.py`)

```python
# Outlier Detection Thresholds
OUTLIER_THRESHOLD_MAD = 3.0   # Median Absolute Deviation
OUTLIER_THRESHOLD_IQR = 1.5   # Interquartile Range

# Data Quality
GAP_TOLERANCE_PERCENT = 30.0  # Warn if > 30% missing
```

**Note:** MICE imputation is implemented but rarely used - DAX data is clean with no missing values.

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

## **Key Research Findings**

From 14 completed DAX research notebooks (Jan 2023 - Sept 2025, M5 data):

**What Works:**
- ✓ **Intraday momentum in quiet regimes** (65% continuation, first hour → rest of day)
- ✓ **Early volatility predicts daily regime** (R²=0.53, used for position sizing)
- ✓ **Pivot point conditional probabilities** (promising scenarios identified, to be backtested)
- ✓ **Local pivot points** (first hour H/L/C, potentially superior to standard pivots)

**What Doesn't Work:**
- ❌ Day-to-day direction prediction (50/50)
- ❌ Volatility regime changes affecting direction
- ❌ Yesterday's return predicting today

**Full details:** [quant_lab/notebooks/research_index.md](quant_lab/notebooks/research_index.md)

---

**Status:** Phase 1 Complete ✓ | Phase 2 Ongoing (Research Loop)
