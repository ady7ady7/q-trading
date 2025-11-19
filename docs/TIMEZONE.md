# Timezone Handling

Quick reference for timezone operations.

---

## **Quick Start**

```python
from shared.data_module import process_data

# UTC (default)
df_utc = process_data(df, symbol='eurusd', timeframe='h1', local_time=False)

# Local time (automatically uses symbol's configured timezone)
df_local = process_data(df, symbol='eurusd', timeframe='h1', local_time=True)
```

---

## **Symbol Timezones**

Each symbol has a configured timezone in `config.py`:

| Symbol | Timezone | Asset Type |
|--------|----------|-----------|
| `deuidxeur` | Europe/Berlin | TradFi |
| `usa500idxusd` | America/New_York | TradFi |
| `usatechidxusd` | America/New_York | TradFi |
| `usa30idxusd` | America/New_York | TradFi |
| `eurusd` | Europe/London | Forex |
| `eurjpy` | Europe/London | Forex |
| `usdcad` | America/Toronto | Forex |
| `nzdcad` | Pacific/Auckland | Forex |
| `gbpusd` | Europe/London | Forex |
| `xauusd` | America/New_York | Commodity |
| `xagusd` | America/New_York | Commodity |
| `lightcmdusd` | America/New_York | Commodity |
| `btcusdt` | UTC | Crypto |
| `ethusdt` | UTC | Crypto |

---

## **Concept**

### **Database Storage**

All data stored in PostgreSQL as `TIMESTAMPTZ` (UTC):

```sql
CREATE TABLE eurusd_h1_tradfi_ohlcv (
    timestamp TIMESTAMPTZ,  -- Always UTC
    ...
);
```

### **Processing**

All operations use UTC timezone-aware datetimes:

```python
# Fetch from database (UTC)
df_raw = fetch_ohlcv('eurusd', 'h1', start, end)
# Index: UTC

# Process (stays in UTC internally)
df_clean = process_data(df_raw, 'eurusd', 'h1', local_time=False)
# Index: UTC

# Convert on output (if requested)
df_local = process_data(df_raw, 'eurusd', 'h1', local_time=True)
# Index: Europe/London (EURUSD's timezone)
```

---

## **Common Conversions**

### **UTC to New York (USA equities)**

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data

df = fetch_ohlcv('usa500idxusd', 'h1', start, end)
df_ny = process_data(df, 'usa500idxusd', 'h1', local_time=True)

# Index is now in America/New_York
print(df_ny.index.tz)  # America/New_York
```

### **UTC to London (Forex)**

```python
df = fetch_ohlcv('eurusd', 'h1', start, end)
df_london = process_data(df, 'eurusd', 'h1', local_time=True)

# Index is now in Europe/London
print(df_london.index.tz)  # Europe/London
```

### **Keep UTC (default)**

```python
df = fetch_ohlcv('eurusd', 'h1', start, end)
df_utc = process_data(df, 'eurusd', 'h1', local_time=False)

# Index remains in UTC
print(df_utc.index.tz)  # UTC
```

---

## **DST (Daylight Saving Time)**

Automatically handled by `pytz`:

```python
import pandas as pd

# January (EST = UTC-5)
ts_jan = pd.Timestamp('2024-01-15 12:00', tz='UTC').tz_convert('America/New_York')
print(ts_jan)  # 2024-01-15 07:00:00-05:00

# April (EDT = UTC-4)
ts_apr = pd.Timestamp('2024-04-15 12:00', tz='UTC').tz_convert('America/New_York')
print(ts_apr)  # 2024-04-15 08:00:00-04:00
```

**No manual adjustment needed!** `pytz` handles DST automatically.

---

## **Example: Market Hours Analysis**

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data
from shared.config import get_symbol_info

# Get market hours for US equities
info = get_symbol_info('usa500idxusd')
print(f"Market: {info['market_open']} - {info['market_close']}")
# Output: Market: 09:30:00 - 16:00:00

# Fetch data
df = fetch_ohlcv('usa500idxusd', 'h1', start, end)

# Convert to local time (NY)
df_ny = process_data(df, 'usa500idxusd', 'h1', local_time=True)

# Filter market hours
market_open = info['market_open']   # 09:30
market_close = info['market_close']  # 16:00

df_market = df_ny[
    (df_ny.index.time >= market_open) &
    (df_ny.index.time <= market_close)
]

print(f"Market hours data: {len(df_market)} candles")
```

---

## **Handling Multiple Timezones**

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data
from datetime import datetime

symbols = ['eurusd', 'usa500idxusd', 'deuidxeur']
start = datetime(2024, 11, 1)
end = datetime(2024, 11, 30)

results = {}

for symbol in symbols:
    df_raw = fetch_ohlcv(symbol, 'h1', start, end)
    df_clean = process_data(df_raw, symbol, 'h1', local_time=True)
    results[symbol] = df_clean

    # Each has its own timezone!
    print(f"{symbol}: {df_clean.index.tz}")

# Output:
# eurusd: Europe/London
# usa500idxusd: America/New_York
# deuidxeur: Europe/Berlin
```

---

## **UTC vs Local Trade Timing**

Different markets open/close at different UTC times:

```python
import pandas as pd

# S&P 500 opens 09:30 EST (New York)
# EST = UTC-5, so 09:30 EST = 14:30 UTC
sp500_open_ny = pd.Timestamp('2024-01-15 09:30', tz='America/New_York')
sp500_open_utc = sp500_open_ny.tz_convert('UTC')
print(sp500_open_utc)  # 2024-01-15 14:30:00+00:00

# DAX opens 09:00 CET (Berlin)
# CET = UTC+1, so 09:00 CET = 08:00 UTC
dax_open_tz = pd.Timestamp('2024-01-15 09:00', tz='Europe/Berlin')
dax_open_utc = dax_open_tz.tz_convert('UTC')
print(dax_open_utc)  # 2024-01-15 08:00:00+00:00
```

**Why this matters:**
- Analysis in UTC: Compare across global markets easily
- Analysis in local time: Analyze market behavior from trader's perspective

---

## **Custom Timezone (Advanced)**

To analyze in a non-standard timezone:

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import _ensure_utc_timezone, _convert_to_local_time

# Fetch (UTC)
df = fetch_ohlcv('eurusd', 'h1', start, end)

# Ensure UTC
df_utc = _ensure_utc_timezone(df)

# Convert to custom timezone
df_tokyo = _convert_to_local_time(df_utc, 'Asia/Tokyo')

print(df_tokyo.index.tz)  # Asia/Tokyo
```

---

## **Verification**

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data

# Fetch
df_raw = fetch_ohlcv('eurusd', 'h1', start, end)

# Process (UTC)
df_utc = process_data(df_raw, 'eurusd', 'h1', local_time=False)
print(f"UTC: {df_utc.index.tz}")  # UTC

# Process (Local)
df_local = process_data(df_raw, 'eurusd', 'h1', local_time=True)
print(f"Local: {df_local.index.tz}")  # Europe/London

# Same number of candles
assert len(df_utc) == len(df_local)

# Same values, different index
assert (df_utc['close'] == df_local['close']).all()
```

---

## **Troubleshooting**

### **"Unknown timezone" error**

**Problem:**
```
ValueError: Unknown timezone
```

**Solution:**
1. Check spelling: `Europe/London` (case-sensitive)
2. Use `/` not `-`: `America/New_York` (not `America-New-York`)
3. List valid timezones:
   ```python
   import pytz
   print([tz for tz in pytz.all_timezones if 'New' in tz])
   ```

### **Index timezone is None**

**Problem:** Index lost timezone information

**Solution:**
```python
# Don't do this
df.index = df.index  # Removes timezone!

# Do this
df.index = df.index.tz_convert('America/New_York')
```

### **DST Shift Creates Gap**

**Problem:** March/April shows time jump

**Solution:** This is correct behavior. DST shifts are automatic:
```python
# No action needed - pytz handles it
```

