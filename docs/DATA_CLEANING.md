# Data Cleaning & Timezone Handling

Practical guide to data cleaning, imputation, and timezone conversion.

---

## **Data Cleaning Pipeline**

The `process_data()` function implements a 6-step pipeline:

### **Step 1: Timezone Localization**

Raw data from database is in UTC (TIMESTAMPTZ). First step is to ensure timezone awareness:

```python
# Input: DataFrame with 'timestamp' column (naive or tz-aware)
# Process: Localize to UTC if naive, convert if different tz
# Output: DataFrame with UTC timezone-aware index
```

### **Step 2: OHLC Validation**

Checks logical consistency of OHLCV data:

**Checks performed:**
- `High ≥ Low` for every candle
- `High ≥ max(Open, Close)`
- `Low ≤ min(Open, Close)`
- All prices > 0
- No NaN in price columns (logged, not failed on)

**Violations are logged but processing continues.** Invalid candles are fixed in Step 4.

### **Step 3: Diagnostics**

#### **Gap Analysis**

Detects missing candles based on expected frequency:

```python
Timeframe  Expected Frequency
m1         1 minute
m5         5 minutes
h1         1 hour
d1         1 day
```

**Output:**
```
✓ No significant gaps detected
   OR
⚠ Detected 3 gaps. Largest: 2 days 03:00:00
```

#### **Missing Data Analysis**

Calculates % NaN per column:

```python
open: 0.00% missing
close: 0.00% missing
high: 0.00% missing
low: 0.00% missing
volume: 2.50% missing
```

**Warning threshold:** If any column > 30% missing, imputation reliability drops.

#### **Outlier Detection**

Uses two complementary methods:

**Method 1: Median Absolute Deviation (MAD)**
```python
median = data.median()
mad = (data - median).abs().median()
outliers = (data < median - 3*MAD) | (data > median + 3*MAD)
```
✓ Robust to extreme values
✓ Better for skewed distributions

**Method 2: Interquartile Range (IQR)**
```python
q1, q3 = data.quantile(0.25), data.quantile(0.75)
iqr = q3 - q1
outliers = (data < q1 - 1.5*iqr) | (data > q3 + 1.5*iqr)
```
✓ Standard Tukey method
✓ Good for normal distributions

**Output:**
```
✓ No outliers detected
   OR
⚠ Detected 7 outliers in high
⚠ Detected 12 outliers in volume
```

### **Step 4: Data Cleaning (MICE Imputation)**

If missing data exists, uses Multivariate Iterative Imputation by Chained Equations (MICE).

#### **Why MICE?**

- ✓ Accounts for relationships between OHLCV columns
- ✓ More accurate than simple forward-fill
- ✓ Produces reproducible results (fixed seed)
- ✓ Works with multiple missing columns

#### **Process**

1. **Standardize** — Convert to z-scores (mean=0, std=1)
   ```python
   from sklearn.preprocessing import StandardScaler
   scaler = StandardScaler()
   X_std = scaler.fit_transform(df[['open', 'high', 'low', 'close', 'volume']])
   ```

2. **Impute** — Fill missing values using MICE
   ```python
   from sklearn.impute import IterativeImputer
   imputer = IterativeImputer(max_iter=10, random_state=42)
   X_imputed_std = imputer.fit_transform(X_std)
   ```

3. **Reverse Standardize** — Return to original scale
   ```python
   X_imputed = scaler.inverse_transform(X_imputed_std)
   ```

4. **Enforce Consistency** — Correct OHLC violations from imputation
   ```python
   high = max(open, close, high)
   low = min(open, close, low)
   volume = max(volume, 0)
   ```

#### **Configuration** (in `config.py`)

```python
MICE_CONFIG = {
    'max_iter': 10,           # Iterations (convergence by 5-7)
    'random_state': 42,       # Fixed seed for reproducibility
    'verbose': 0,             # Logging verbosity
}
```

#### **Output**

```
No missing data - skipping imputation
   OR
MICE imputation complete (max_iter=10)
```

### **Step 5: Timezone Conversion** (if `local_time=True`)

Converts from UTC to instrument's local timezone.

**Configuration** (in `config.py`):

```python
SYMBOLS = {
    'eurusd': {
        'timezone': 'Europe/London',    # pytz format
        ...
    },
    'usa500idxusd': {
        'timezone': 'America/New_York',
        ...
    },
}
```

**Example:**

```python
# Input: UTC timezone-aware DataFrame
df_clean = process_data(df_raw, 'eurusd', 'h1', local_time=True)

# Output: DataFrame with Europe/London timezone
print(df_clean.index.tz)  # Europe/London
```

**DST Handling:**

Daylight Saving Time is automatically handled by `pytz`:

```python
# No need to manually adjust for DST
# pytz handles it transparently
df.index = df.index.tz_convert('Europe/London')
# 2024-03-31 02:00 UTC → 2024-03-31 03:00 BST (automatic)
```

### **Step 6: News Filtering** (if `exclude_news=True`)

Removes data on major economic announcement dates.

**Requirements:**

`news_calendar.csv` in project root with format:

```csv
date,event,currency,impact
2024-01-10,Non-Farm Payroll,USD,High
2024-01-11,ECB Interest Rate Decision,EUR,High
2024-02-01,CPI Data,USD,High
```

**Process:**

1. Read `news_calendar.csv`
2. Extract unique dates
3. Remove all candles where `timestamp.date()` matches a news date

**Output:**

```
Filtered out 42 candles on news dates
   OR
news_calendar.csv not found - skipping news filtering
```

---

## **Timezone Handling Details**

### **Core Principles**

1. **Source of Truth:** Database stores all data in UTC (TIMESTAMPTZ)
2. **Processing:** All operations use UTC timezone-aware objects
3. **Output:** Converted to local time on request

### **Supported Timezones**

Each symbol has a configured timezone in `config.py`:

```python
SYMBOLS = {
    # TradFi
    'deuidxeur': {'timezone': 'Europe/Berlin'},
    'usa500idxusd': {'timezone': 'America/New_York'},
    'usatechidxusd': {'timezone': 'America/New_York'},
    'usa30idxusd': {'timezone': 'America/New_York'},

    # Forex
    'eurusd': {'timezone': 'Europe/London'},
    'eurjpy': {'timezone': 'Europe/London'},
    'usdcad': {'timezone': 'America/Toronto'},
    'nzdcad': {'timezone': 'Pacific/Auckland'},
    'gbpusd': {'timezone': 'Europe/London'},

    # Commodities
    'xauusd': {'timezone': 'America/New_York'},
    'xagusd': {'timezone': 'America/New_York'},
    'lightcmdusd': {'timezone': 'America/New_York'},

    # Crypto (always UTC)
    'btcusdt': {'timezone': 'UTC'},
    'ethusdt': {'timezone': 'UTC'},
}
```

**Key:** Use pytz format (e.g., 'America/New_York'), not abbreviations (e.g., not 'EST')

### **Conversion Example**

```python
import pandas as pd
import pytz

# UTC data from database
df_utc = pd.DataFrame({
    'timestamp': pd.date_range('2024-01-01', periods=24, freq='h', tz='UTC'),
    'close': [100, 101, 102, ...],
})

# Convert to New York time
df_ny = df_utc.copy()
df_ny.index = df_utc.index.tz_convert('America/New_York')

# 2024-01-01 00:00 UTC → 2023-12-31 19:00 EST (automatic)
print(df_ny.index[0])  # 2023-12-31 19:00:00-05:00
```

### **DST Transitions**

`pytz` handles Daylight Saving Time automatically:

```python
# Before DST (EST = UTC-5)
print(df.index[0])  # 2024-01-15 12:00:00-05:00

# After DST (EDT = UTC-4)
print(df.index[100])  # 2024-04-01 12:00:00-04:00

# No manual adjustment needed!
```

---

## **Data Quality Thresholds**

Settings in `config.py`:

```python
# Outlier Detection
OUTLIER_THRESHOLD_MAD = 3.0      # Median ± 3×MAD (3-sigma equivalent)
OUTLIER_THRESHOLD_IQR = 1.5      # 1.5×IQR (standard Tukey)

# Missing Data Tolerance
GAP_TOLERANCE_PERCENT = 30.0     # Warn if > 30% NaN

# MICE Imputation
MICE_CONFIG = {
    'max_iter': 10,              # Iterations for convergence
    'random_state': 42,          # Reproducible seed
}
```

### **When to Adjust**

**More strict outlier detection:**
```python
OUTLIER_THRESHOLD_MAD = 2.0  # Median ± 2×MAD (2-sigma)
```

**More lenient (for volatile assets):**
```python
OUTLIER_THRESHOLD_MAD = 4.0  # Median ± 4×MAD
```

**Higher missing data tolerance:**
```python
GAP_TOLERANCE_PERCENT = 50.0  # Warn only if > 50% missing
```

---

## **Reproducibility**

All cleaning operations are deterministic:

```python
# Same input → Same output (guaranteed)
df1 = process_data(df_raw, 'eurusd', 'h1')
df2 = process_data(df_raw, 'eurusd', 'h1')
assert df1.equals(df2)  # Always True
```

**Why:**
- Fixed random seed (`random_state=42`)
- MICE uses consistent algorithm
- Timezone conversion is deterministic
- No randomness in diagnostics

---

## **Troubleshooting**

### **> 30% Missing Data**

**Problem:** Imputation reliability drops sharply.

**Solution:**
1. Check data quality at source
2. Use shorter date range
3. Check for market closures (weekends, holidays)
4. Adjust `GAP_TOLERANCE_PERCENT` if known good

### **Timezone Conversion Failed**

**Problem:** "Unknown timezone" error

**Solution:**
1. Verify timezone in `SYMBOLS` (use pytz name)
2. Check spelling (case-sensitive, use '/' not '-')
3. List valid timezones:
   ```python
   import pytz
   print(pytz.all_timezones)
   ```

### **OHLC Violations Post-Imputation**

**Problem:** High < Low after imputation

**Solution:**
1. Automatic: Post-imputation step corrects violations
2. Manual: Increase `OUTLIER_THRESHOLD_MAD` to skip those candles
3. Check source data quality

### **No Data After Filtering**

**Problem:** News filtering removed all candles

**Solution:**
1. Check `news_calendar.csv` for overlapping dates
2. Increase date range
3. Use `exclude_news=False`

