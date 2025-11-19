# **Quick Start Guide**

## **Installation**

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **2. Configure Environment**

Create `.env` in project root:
```
DATABASE_URL=
DATABASE_CA_CERT_PATH=./certs/ca-certificate.crt
LOG_LEVEL=INFO
```

### **3. Verify PostgreSQL Connection**

```bash
python -c "from shared.data_module import DatabaseConnection; DatabaseConnection.get_engine(); print('✓ Connection successful')"
```

---

## **Basic Usage**

### **Import and Fetch Data**

```python
from shared.data_module import get_data
from datetime import datetime

# Fetch clean EURUSD hourly data
df = get_data(
    instrument='EURUSD',
    timeframe='H1',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 3, 31),
)

print(df.head())
#               open    high     low   close   volume
# timestamp
# 2024-01-01  1.0500  1.0520  1.0490  1.0515  150000
# 2024-01-02  1.0515  1.0535  1.0505  1.0530  160000
```

### **Convert to Local Time**

```python
df = get_data(
    instrument='SPY',
    timeframe='D1',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    local_time=True,  # Convert to America/New_York
)

print(df.index.tz)  # America/New_York
```

### **Exclude News Dates**

Create `news_calendar.csv`:
```csv
date,event,currency,impact
2024-01-10,Non-Farm Payroll,USD,High
2024-02-01,ECB Rate Decision,EUR,High
```

Then:
```python
df = get_data(
    instrument='EURUSD',
    timeframe='H1',
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    exclude_news=True,
)
```

---

## **Configuration**

### **Add New Instrument**

Edit `shared/config.py`:

```python
INSTRUMENT_TIMEZONES = {
    # ... existing instruments ...
    'NEW_SYMBOL': 'Timezone/Location',
}

MARKET_HOURS = {
    # ... existing hours ...
    'NEW_SYMBOL': (9, 0, 17, 0),  # Trading hours in local time
}
```

### **Adjust Imputation Settings**

Edit `shared/config.py`:

```python
MICE_CONFIG = {
    'max_iter': 15,          # More iterations for better convergence
    'random_state': 42,      # Keep fixed for reproducibility
    'estimator': None,       # Or specify custom estimator
}

OUTLIER_THRESHOLD_MAD = 3.5  # More strict outlier detection
```

---

## **Testing**

### **Run All Tests**

```bash
pytest tests/ -v
```

### **Run Specific Test Class**

```bash
pytest tests/test_data_module.py::TestTimezoneHandling -v
```

### **Run with Coverage**

```bash
pytest tests/ --cov=shared --cov-report=html
# Open htmlcov/index.html in browser
```

---

## **Logging**

### **Console Output**

```python
from shared.data_module import get_data
import logging

logger = logging.getLogger('shared.data_module')
logger.info("This prints to console and logs/data_module.log")
```

### **Check Logs**

```bash
tail -f logs/data_module.log
```

### **Change Log Level**

In `.env`:
```
LOG_LEVEL=DEBUG  # More verbose
LOG_LEVEL=INFO   # Standard
LOG_LEVEL=WARNING  # Errors only
```

---

## **Common Issues**

### **"No data found for EURUSD H1"**

**Problem:** Empty result from database
**Solution:**
1. Check database table exists: `EURUSD_H1`
2. Verify date range has data
3. Check PostgreSQL connection: `echo "SELECT 1" | psql $DATABASE_URL`

### **"Instrument 'EURUSD' not configured"**

**Problem:** Symbol not in `INSTRUMENT_TIMEZONES`
**Solution:**
1. Add to `shared/config.py`
2. Include timezone and market hours

### **"Database connection failed"**

**Problem:** Connection error
**Solution:**
1. Verify `.env` `DATABASE_URL` is correct
2. Check PostgreSQL is running
3. Test connection: `psql $DATABASE_URL -c "SELECT 1"`
4. If SSL: verify certificate path in `.env`

### **"> 30% missing" warning**

**Problem:** Too much missing data to impute reliably
**Solution:**
1. Review data quality in source
2. Use shorter date range
3. Check for market closures (weekends, holidays)

### **"news_calendar.csv not found"**

**Problem:** Trying to filter news but file missing
**Solution:**
1. Create file with format:
   ```csv
   date,event,currency,impact
   2024-01-10,NFP,USD,High
   ```
2. Or set `exclude_news=False`

---

## **Next Steps**

### **Sprint 2: Research**

Once data pipeline is working:

1. Create notebooks in `quant_lab/notebooks/`
2. Use `get_data()` to fetch instrument data
3. Analyze patterns and generate hypotheses

Example notebook setup:

```python
# In Jupyter notebook
import pandas as pd
from shared.data_module import get_data
from datetime import datetime

# Fetch data
df = get_data(
    instrument='DE40',
    timeframe='D1',
    start_date=datetime(2022, 1, 1),
    end_date=datetime(2024, 12, 31),
    local_time=True,
)

# Analyze
print(f"Data shape: {df.shape}")
print(f"Date range: {df.index.min()} to {df.index.max()}")
print(f"Returns: {(df['close'].pct_change()).describe()}")
```

### **Sprint 3: Backtester**

Build backtesting engine with:
- Position sizing (Fixed Fractional, Kelly Criterion)
- P&L calculation
- Performance metrics (Sharpe, Calmar, etc.)

### **Sprint 4: Optimization**

Portfolio simulations and parameter sweeps.

---

## **File Structure Reference**

```
project-root/
├── shared/                       # Shared modules
│   ├── config.py                # Configuration (instruments, costs, params)
│   ├── data_module.py           # Data fetching & cleaning
│   ├── engine.py                # (Backtest engine - Sprint 3)
│   └── reporting.py             # (Performance metrics - Sprint 3)
├── quant_lab/                    # Research
│   ├── notebooks/               # Jupyter notebooks
│   │   ├── CHAR_DE40_Trend_And_Range.ipynb
│   │   ├── PHENOM_EURUSD_IB_Stats.ipynb
│   │   └── ANALYSIS_LINEAR_REGRESSION.ipynb
│   └── research_index.md        # Index of research
├── vector_bt/                    # Backtesting
│   ├── strategies/              # Strategy implementations
│   │   ├── strategy_name.py
│   │   └── strategy_name.md
│   ├── main.py                  # Strategy runner
│   ├── sweep.py                 # (Parameter optimization - Sprint 4)
│   └── strategy_index.md        # Strategy index
├── tests/                        # Unit tests
│   └── test_*.py
├── docs/                         # Documentation
│   ├── DATA_CLEANING_PROCEDURE.md
│   ├── TIMEZONE_HANDLING.md
│   ├── NEWS_MANAGEMENT.md
│   └── MASTER_README.md         # (Main project docs)
├── logs/                         # (Auto-created) Logs
├── data/                         # (Auto-created) Data cache
├── cache/                        # (Auto-created) Temporary cache
├── results/                      # (Auto-created) Backtest results
├── .env                          # Environment config (local, not committed)
├── requirements.txt              # Dependencies
├── CLAUDE.md                     # Development instructions
├── CHECKLIST.md                  # Project progress tracker
└── QUICK_START.md                # This file
```

---

## **Key Documentation**

- **[CLAUDE.md](CLAUDE.md)** - Complete development plan
- **[CHECKLIST.md](CHECKLIST.md)** - Progress tracker
- **[SPRINT_1_SUMMARY.md](SPRINT_1_SUMMARY.md)** - Sprint 1 deliverables
- **[docs/DATA_CLEANING_PROCEDURE.md](docs/DATA_CLEANING_PROCEDURE.md)** - Detailed cleaning guide
- **[docs/TIMEZONE_HANDLING.md](docs/TIMEZONE_HANDLING.md)** - Timezone procedures
- **[docs/NEWS_MANAGEMENT.md](docs/NEWS_MANAGEMENT.md)** - News calendar filtering

---

**Ready to start?** Begin with Sprint 2: Research
