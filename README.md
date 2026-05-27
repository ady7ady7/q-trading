# q-trading: Quantitative Research Lab

Statistical research on futures and equity index markets. Hypothesis generation and validation using clean data pipelines. Backtesting handled externally — see [q_trading_backtester](https://github.com/ady7ady7/q_trading_backtester) repo.

---

## Project Structure

```
.
├── shared/
│   ├── config.py               # Symbol configs, timezones, market hours
│   ├── database_connector.py   # PostgreSQL OHLCV fetching (DAX/FX/etc.)
│   ├── data_module.py          # Data processing: validate, clean, impute, load_from_csv()
│   └── data_handler.py         # High-level pipeline wrapper (fetch + process)
├── quant_lab/
│   └── notebooks/              # Research notebooks
│       ├── CHAR_DE40_*.ipynb   # DAX/DE40 studies
│       ├── CHAR_FDAX_*.ipynb   # FDAX (futures) studies
│       └── research_index.md   # All findings indexed here
├── data/                       # Local data files (gitignored)
│   ├── NQ_M1_OHLCV.csv/parquet
│   ├── NQ_M5_OHLCV.csv/parquet
│   ├── NQ_RTH_ValueArea.csv    # Per-session: POC, VAL, VAH, VWAP
│   └── NQ_RTH_VolumeProfile.csv # Per-price-level: bid/ask volume
├── tests/
│   └── test_data_module.py
├── certs/
│   └── ca-certificate.crt      # PostgreSQL SSL cert
├── devlog.md                   # Running research log and ideas
├── requirements.txt
└── .env                        # DB credentials (gitignored)
```

---

## Instruments

| Instrument | Data Source | Timezone | RTH |
|---|---|---|---|
| DAX (DE40/FDAX) | PostgreSQL (M5 OHLCV) / Databento EOBI tick data | Europe/Berlin | 09:00–17:30 |
| NQ (Nasdaq futures) | `data/` local files (Databento EOBI tick data) | America/New_York | 09:30–16:00 |

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

Create `.env`:
```
DATABASE_URL=postgresql://user:password@host:port/database_name
DATABASE_CA_CERT_PATH=./certs/ca-certificate.crt
LOG_LEVEL=INFO
```

---

## Data Access

### DAX / DB-backed instruments

```python
from shared.database_connector import fetch_ohlcv
from shared.data_module import process_data

df_raw = fetch_ohlcv('deuidxeur', 'm5', start_date, end_date)
df = process_data(df_raw, 'deuidxeur', 'm5', local_time=True)
# Index: Europe/Berlin, RTH only, validated and cleaned
```

### NQ (local files)

```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path('../../data')  # from quant_lab/notebooks/

# M5 bars
df = pd.read_parquet(DATA_DIR / 'NQ_M5_OHLCV.parquet')
df['candle_open'] = pd.to_datetime(df['candle_open'], utc=False)
df = df.set_index('candle_open').between_time('09:30', '16:00')

# Value area (daily)
va = pd.read_csv(DATA_DIR / 'NQ_RTH_ValueArea.csv', parse_dates=['session_date'])

# Volume profile (per price level per day)
vp = pd.read_csv(DATA_DIR / 'NQ_RTH_VolumeProfile.csv', parse_dates=['session_date'])
```

Or via `load_from_csv()` in `data_module.py` for auto timestamp detection and timezone conversion.

---

## Workflow

1. **Idea** — log in `devlog.md`
2. **Notebook** — `quant_lab/notebooks/[Category]_[Instrument]_[Topic].ipynb`
3. **Validate** — statistical tests, p-values, sample size check
4. **Document** — findings in a Markdown cell + `research_index.md`
5. **Backtest** — externally (separate engine / cTrader / Pinescript)

---

## Key Research Findings

From 11 completed DAX notebooks (M5, 09:00–17:30 Berlin, Jan 2023–Sep 2025):

**Confirmed edges:**
- Quiet (Q1) vol regime + strong UP first hour → **65% continuation** (intraday, 09–10 → rest of day)
- Early session range (09–11) predicts daily range magnitude: R²=0.53, Pearson r=0.728
- Open > standard PP → R1 hit probability ~79%
- Standard pivot conditional probabilities: promising scenarios identified, pending backtest
- Local pivot (first hour H/L/C) conditional probabilities: promising, potentially superior to standard pivots
- Local pivots by vol regime (Q1–Q4): positive delta scenarios in specific zone-condition combos

**Ruled out:**
- Day-to-day direction prediction (50/50 across all regimes)
- Volatility regime changes as direction signal
- Yesterday's return predicting today's direction

Full details: [quant_lab/research_index.md](quant_lab/research_index.md)

---

## Logging

Logs written to `logs/` (gitignored):
- `database_connector.log`
- `data_module.log`

Set verbosity in `.env`: `LOG_LEVEL=DEBUG / INFO / WARNING`
