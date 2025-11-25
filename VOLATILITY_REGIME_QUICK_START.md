# DAX Volatility Regime Analysis - Quick Start Guide

## What You Just Created

A complete analytical notebook (`CHAR_DE40_Volatility_Regime_Analysis.ipynb`) that investigates:

**Can early-session volatility (first 60 minutes) predict full-day volatility regimes on DAX?**

---

## Quick Summary

### The Question
At 10:00 AM Berlin time (after 1 hour of trading), can we predict whether today will be a "quiet," "normal," or "very active" trading day?

### The Data
- **Source:** M5 (5-minute) OHLCV bars from DAX index
- **Period:** Jan 2023 – Sept 2025 (~680 trading days)
- **Timezone:** UTC → Europe/Berlin (pytz handles DST automatically, no manual adjustment needed)
- **Trading Hours:** 09:00-17:30 Berlin local time only (RTH)

### The Method

**Step 1: Measure Daily Volatility**
- Calculate True Range (TR) for each 5-minute bar
- Sum all TRs for the trading day
- Convert to percentage: ATRP = (Daily_TR_Sum / Close) × 100
- Label regime based on rolling 60-day percentile rank:
  - Low Vol: Bottom 33%
  - Normal Vol: Middle 33%
  - High Vol: Top 33%

**Step 2: Measure Early Morning Volatility**
- Calculate True Range for first 12 bars (09:00-10:00 = 1 hour)
- Convert to percentage: Early_TRP = (Early_TR_Sum / Open) × 100
- Compare to recent 20-day average: Early_Ratio = Early_TRP / Avg_20d

**Step 3: Test the Correlation**
- Pearson & Spearman correlation: Early volatility vs Full-day volatility
- Conditional probability: P(High Vol Day | Spicy Morning)
- Success: Does top quartile morning predict >50% chance of high vol day?

**Step 4: Create Regime Heatmap**
- Visualize: Early strength quartiles → Full-day regimes
- Quantify: Percentage of top quartile mornings that lead to high vol days

---

## How to Run the Notebook

### Prerequisites
```bash
pip install pandas numpy scipy matplotlib seaborn scikit-learn
```

### Execution
1. Open `quant_lab/notebooks/CHAR_DE40_Volatility_Regime_Analysis.ipynb` in Jupyter
2. Run cells in order (dependencies managed internally)
3. Notebook will:
   - Fetch M5 data from database
   - Verify timezone offsets (DST check)
   - Calculate all metrics
   - Generate visualizations
   - Print final edge assessment

### Expected Output
- **Console output:** Correlation metrics, regime distributions, conditional probabilities
- **Visualizations:** 4 scatter/box plots + 1 heatmap
- **Interpretation:** Actionable edge assessment at the end

---

## Key Metrics to Look For

### 1. Correlation Strength
```
IF Pearson r > 0.6 and p-value < 0.05:
   → Signal exists, proceed to next metric

IF Pearson r < 0.4 or p-value > 0.05:
   → Signal is weak or non-existent
```

### 2. Predictive Power (Conditional Probability)
```
Baseline: P(High Regime) ≈ 33% (by definition)

IF P(High | Q4 Spicy morning) > 50%:
   → STRONG EDGE: Top quartile predicts high vol >50% of time

IF P(High | Q4 Spicy morning) > 40%:
   → MODERATE EDGE: Can use for position sizing

IF P(High | Q4 Spicy morning) < 35%:
   → NO EDGE: Don't use this signal
```

### 3. Regime Separation (Heatmap Check)
```
Look for clear diagonal pattern:
- Q1 Quiet → Low Vol days
- Q4 Spicy → High Vol days

If all quartiles show ~33% for all regimes:
   → No useful pattern
```

---

## Expected Results (Based on Previous Research)

### Most Likely Outcome A: POSITIVE SIGNAL (R² > 0.30, P(High|Q4) > 45%)

**Interpretation:**
- Early morning volatility predicts daily volatility
- Can use for position sizing and risk management
- Combine with other signals for full strategy

**Action:**
```
At 10:00 AM, measure first hour volatility:

If Q4 Spicy morning (top 25%):
   → Expect high vol rest-of-day
   → Use 1.5x position size for afternoon trading
   → Widen stop losses
   → Expect larger price swings

If Q1 Quiet morning (bottom 25%):
   → Expect quiet rest-of-day
   → Use 0.75x position size for afternoon trading
   → Tighter stops acceptable
   → Small moves likely
```

### Most Likely Outcome B: WEAK SIGNAL (0.20 < R² < 0.30, 35% < P(High|Q4) < 40%)

**Interpretation:**
- Signal exists but noisy
- Only 20-30% of daily volatility explained
- Autocorrelation from yesterday confounds the edge

**Action:**
```
Use only as a weak filter, not primary signal

If Q4 Spicy morning AND yesterday was quiet:
   → Signal is stronger (regime change)
   → Use for position sizing

If Q4 Spicy morning BUT yesterday was very active:
   → Signal is weak (might just be carry-over)
   → Ignore or use smaller position multiplier
```

### Unlikely Outcome C: NO SIGNAL (R² < 0.15, P(High|Q4) ≈ 33%)

**Interpretation:**
- Early hours don't predict later hours
- Daily volatility is random/independent
- Other factors matter more than opening volatility

**Action:**
```
Don't use this approach. Research alternatives:

Option 1: Look at direction, not magnitude
   Does opening move direction predict rest-of-day direction?

Option 2: Look at intra-hour patterns
   Is there a mean-reversion signal within the first hour?

Option 3: Look at support/resistance
   Do opening highs/lows act as pivots?
```

---

## Practical Trading Application (If Signal Is Strong)

### Position Sizing Decision Point: 10:00 AM Berlin

At 10:00 AM, measure first hour (09:00-10:00):

```python
early_tr_sum = sum of all true ranges from 09:00-10:00
early_trp = early_tr_sum / open_price * 100

early_ratio = early_trp / avg_early_trp_last_20_days

# Assign volatility quartile (can pre-calculate thresholds)
if early_ratio < 0.80:
    quartile = "Q1_Quiet"
    position_multiplier = 0.75

elif early_ratio < 1.00:
    quartile = "Q2_Normal"
    position_multiplier = 1.00

elif early_ratio < 1.30:
    quartile = "Q3_Active"
    position_multiplier = 1.25

else:
    quartile = "Q4_Spicy"
    position_multiplier = 1.50

# Apply to rest-of-day trading (10:00-17:30)
today_position_size = base_size * position_multiplier
today_stop_loss_width = expected_range * position_multiplier
```

### Stop Loss Calculation

```python
daily_expected_range = daily_atrp × 0.01 × current_price

# Conservative (70% of expected range)
sl_width_conservative = daily_expected_range * 0.70

# Normal (1.0x expected range)
sl_width_normal = daily_expected_range * 1.00

# Aggressive (150% expected range)
sl_width_aggressive = daily_expected_range * 1.50

# Example on DAX at 19,000 with 1.2% ATRP expected
# SL_normal = 0.012 × 19000 = 228 points
```

---

## File Structure

```
q-trading/
├── quant_lab/
│   └── notebooks/
│       └── CHAR_DE40_Volatility_Regime_Analysis.ipynb ← RUN THIS
│
├── docs/
│   └── VOLATILITY_REGIME_METHODOLOGY.md ← Read for deep dive
│
└── quant_lab/
    └── research_index.md ← Index of all research
```

---

## Next Steps After Running Notebook

### Step 1: Evaluate Results
- Check correlation strength (R² and p-value)
- Check conditional probability heatmap
- Decide: "Is this signal worth trading?"

### Step 2: Understand Confounds
- If autocorrelation is high (yesterday matters), filter for regime changes
- If noise is high, combine with direction or support/resistance
- If signal is weak, look for interaction effects

### Step 3: Backtest Trading Rules
- Test position sizing rules on out-of-sample data
- Measure Sharpe ratio, win rate, drawdown
- Compare to baseline "always 1.0x size" strategy

### Step 4: Forward Test
- Paper trade in September 2025+
- Track position sizes and actual returns
- Verify correlation holds in live market

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'shared'"
**Solution:** Run from correct directory
```bash
cd c:/Users/HARDPC/Desktop/AL/projekty/q-trading
jupyter notebook quant_lab/notebooks/CHAR_DE40_Volatility_Regime_Analysis.ipynb
```

### Issue: Timezone shows "Unknown" offset
**Solution:** Data might have DST transition. Check:
- Date range includes DST dates? (March 30, October 26, 2025)
- UTC conversion happening before filtering?
- See docs/DST_VALIDATION_PROTOCOL.md

### Issue: "Too few samples for percentile rank"
**Solution:** First 60 days of data will show "Unknown" regime (expected)
- Code automatically filters to valid regimes
- You'll have ~2 years of valid data (680 days total)

### Issue: "Heatmap shows equal distribution (33/33/33)"
**Solution:** This means NO EDGE - no pattern between early strength and regime
- Proceed to next research hypothesis
- Try direction analysis instead

---

## Document References

| Document | Purpose |
|----------|---------|
| [VOLATILITY_REGIME_METHODOLOGY.md](docs/VOLATILITY_REGIME_METHODOLOGY.md) | Full technical methodology (formulas, explanations) |
| [research_index.md](quant_lab/research_index.md) | Index of all research in the project |
| [DST_VALIDATION_PROTOCOL.md](docs/DST_VALIDATION_PROTOCOL.md) | Timezone verification procedure |
| [WINDOW_RANKING_SUMMARY.md](WINDOW_RANKING_SUMMARY.md) | Results from early session range analysis |

---

## Key Takeaways

✓ **What you're testing:** Does opening volatility predict daily volatility?

✓ **Why it matters:** Position sizing/risk management based on early signals

✓ **Decision point:** 10:00 AM Berlin time (1 hour into trading day)

✓ **Expected edge:** If exists, 45-60% prediction accuracy (vs 33% baseline)

✓ **Application:** Volatility multiplier for position sizing (0.75x to 1.5x)

✓ **Not for:** Directional entry/exit signals (only risk management)

---

## Questions?

Refer to detailed methodology: `docs/VOLATILITY_REGIME_METHODOLOGY.md`

