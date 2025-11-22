# DST Validation Protocol (Simplified)

**Purpose:** Quickly verify timezone offset is correct for current and previous DST regime.

**Context:**
- Database stores all timestamps in UTC
- DAX trades 09:00-17:30 Berlin time
- Berlin uses: CET (UTC+1, winter) and CEST (UTC+2, summer)
- DST changes: Last Sunday of March (spring) and October (fall)

---

## Current Status Check

**Run this to understand current state:**

```python
import sys
sys.path.insert(0, '../../')

from shared.database_connector import fetch_ohlcv
from datetime import datetime
import pytz

print('[CURRENT DST STATUS]')
print('='*80)

berlin_tz = pytz.timezone('Europe/Berlin')
today = datetime.now()

# Current time in Berlin
berlin_now = berlin_tz.localize(datetime.now().replace(hour=12, minute=0, second=0, microsecond=0))
print(f'Today in Berlin: {berlin_now.strftime("%Y-%m-%d %H:%M %Z (UTC%z)")}')
print(f'Current offset: UTC+{int(berlin_now.utcoffset().total_seconds() / 3600)}')

if 'CEST' in berlin_now.strftime('%Z'):
    print(f'Status: SUMMER TIME (CEST, UTC+2)')
    current_regime = 'SUMMER'
elif 'CET' in berlin_now.strftime('%Z'):
    print(f'Status: WINTER TIME (CET, UTC+1)')
    current_regime = 'WINTER'

# Fetch recent candle to verify
print(f'\n[VERIFY WITH RECENT DATA]')

# Get today's candles in M5 (easier to spot-check)
df = fetch_ohlcv(
    symbol='deuidxeur',
    timeframe='m5',
    start_date=(datetime.now() - timedelta(days=1)).isoformat(),
    end_date=datetime.now().isoformat()
)

if len(df) > 0:
    # Show a candle around 10:00 Berlin time
    df_berlin = df.copy()
    df_berlin.index = df_berlin.index.tz_convert('Europe/Berlin')

    # Find candle closest to 10:00
    target = berlin_tz.localize(df_berlin.index[0].replace(hour=10, minute=0))
    closest_idx = (df_berlin.index - target).abs().argmin()

    sample = df_berlin.iloc[closest_idx]
    print(f'Sample candle from our database:')
    print(f'  Time (Berlin): {df_berlin.index[closest_idx].strftime("%Y-%m-%d %H:%M %Z")}')
    print(f'  Time (UTC): {df.index[closest_idx].strftime("%Y-%m-%d %H:%M UTC")}')
    print(f'  OHLC: {sample["open"]:.0f} / {sample["high"]:.0f} / {sample["low"]:.0f} / {sample["close"]:.0f}')
else:
    print('No recent data found')

print(f'\n[NEXT STEPS]')
print(f'1. Copy the time from above: {df_berlin.index[closest_idx].strftime("%Y-%m-%d %H:%M %Z")}')
print(f'2. Open TradingView FDAX (M5 chart)')
print(f'3. Navigate to this exact time')
print(f'4. Compare OHLC values')
print(f'5. Do they match? -> Timezone is CORRECT')
print(f'6. If they don\'t match, offset is wrong by N hours')
```

---

## Manual Cross-Check: 2 Data Points

### Point 1: Current Regime (Today/This Week)

**Pick a random candle this week:**
```
Date: [Your choice, recent]
Time in Berlin: 10:00 or 14:00 (easy times to find)
Interval: M5 or M1 (your choice)
```

**Extract the candle:**
```python
from shared.database_connector import fetch_ohlcv
from datetime import datetime
import pytz

berlin_tz = pytz.timezone('Europe/Berlin')

# Define the time you want to check (in Berlin local time)
berlin_time = berlin_tz.localize(datetime(2025, 11, 21, 10, 0))  # Example
utc_time = berlin_time.astimezone(pytz.UTC)

print(f'Berlin: {berlin_time.strftime("%Y-%m-%d %H:%M %Z")}')
print(f'UTC: {utc_time.strftime("%Y-%m-%d %H:%M UTC")}')

# Fetch this candle
df = fetch_ohlcv(
    symbol='deuidxeur',
    timeframe='m5',
    start_date=utc_time - timedelta(minutes=10),
    end_date=utc_time + timedelta(minutes=10)
)

print(f'Candle in our DB:')
print(df[['open', 'high', 'low', 'close']].iloc[0])
```

**Cross-check on TradingView:**
1. Open TradingView FDAX M5
2. Go to date from output above
3. Find candle at time shown
4. Compare OHLC

**Result:**
- [ ] Match exactly → Timezone is correct ✓
- [ ] Off by 1 hour → Summer/Winter offset is wrong (UTC offset issue)
- [ ] Off by different amount → Something else is broken

---

### Point 2: Previous Regime (Before Last DST Change)

**When was the last DST change?**
```python
import pytz
from datetime import datetime

berlin_tz = pytz.timezone('Europe/Berlin')

# Today
today = datetime.now()

# Last DST transition
# Spring: Last Sunday of March
# Fall: Last Sunday of October

# For November 2025 (winter time):
# Last fall change was October 26, 2025 (CEST -> CET)
# Previous spring change was March 30, 2025 (CET -> CEST)

# Pick a date from PREVIOUS regime (before October 26, 2025)
prev_regime_date = '2025-10-20'  # 6 days before DST change (still CEST)

print(f'Last DST change: [see above]')
print(f'Check data from previous regime: {prev_regime_date}')
```

**Extract a candle from previous regime:**
```python
from shared.database_connector import fetch_ohlcv
from datetime import datetime, timedelta
import pytz

berlin_tz = pytz.timezone('Europe/Berlin')

# Pick a date from previous DST regime
berlin_time = berlin_tz.localize(datetime(2025, 10, 20, 10, 0))  # Before DST change
utc_time = berlin_time.astimezone(pytz.UTC)

print(f'Berlin: {berlin_time.strftime("%Y-%m-%d %H:%M %Z (offset: UTC%z)")}')
print(f'UTC: {utc_time.strftime("%Y-%m-%d %H:%M UTC")}')

# Fetch candle
df = fetch_ohlcv(
    symbol='deuidxeur',
    timeframe='m5',
    start_date=utc_time - timedelta(minutes=10),
    end_date=utc_time + timedelta(minutes=10)
)

print(f'Candle from DB:')
print(df[['open', 'high', 'low', 'close']].iloc[0])
```

**Cross-check on TradingView:**
- Same process as Point 1
- Find candle at time shown
- Compare OHLC

**Result:**
- [ ] Matches → DST handling is working for both regimes ✓
- [ ] Different offset → Timezone library is correctly using DST

---

## What the Offset Difference Tells You

```
If Point 1 (current regime) shows UTC+1 and Point 2 shows UTC+2:
  → Timezone handling is CORRECT (DST is being respected)

If both show UTC+1 or both show UTC+2:
  → Timezone handling is BROKEN (DST not being applied)

If Point 1 time is 1 hour off from TradingView:
  → Offset for current regime is wrong

If Point 2 time is 1 hour off from TradingView:
  → Offset for previous regime is wrong

If different number of hours off:
  → Database query/storage issue, not just DST
```

---

## How to Document This Check

**Create a simple record:**

```markdown
# DST Validation - [Today's Date]

## Current Regime Check
Date checked: 2025-11-21
Time: 10:00 Berlin
Our offset: UTC+1 (CET, winter)
Our OHLC: 18123 / 18145 / 18100 / 18142
TradingView OHLC: 18123 / 18145 / 18100 / 18142
Match: ✓ YES

## Previous Regime Check
Date checked: 2025-10-20 (before Oct 26 DST change)
Time: 10:00 Berlin
Our offset: UTC+2 (CEST, summer)
Our OHLC: 18456 / 18478 / 18450 / 18470
TradingView OHLC: 18456 / 18478 / 18450 / 18470
Match: ✓ YES

## Conclusion
✓ Timezone handling is CORRECT
✓ Safe to use this data for analysis
```

---

## When to Re-Check

Re-run this simple 2-point check:
- Before starting major analysis
- After updating timezone handling code
- Once per quarter (to catch any database issues)

**Do NOT** over-validate. These 2 checks catch 99% of DST issues. You don't need to check every transition—once you confirm both regimes work, the pattern is confirmed.

---

## Quick Reference: Current Offset

```
November 2025: CET (UTC+1, winter)
Next change: March 30, 2026 (spring to CEST)

If you see UTC+2 in winter → Problem
If you see UTC+1 in summer → Problem
If you see UTC+1 in winter and UTC+2 in summer → Correct ✓
```
