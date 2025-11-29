# DAX Research Index

**Period:** Jan 2023 - Sept 2025 (M5 data, 09:00-17:30 Berlin time)
**Status:** 8 research notebooks, key edges identified, many dead ends ruled out

---

## Key Finding: The 65% Edge

**Best signal found so far:**
- **Quiet (Q1) volatility regime + Strong UP first hour (09-10) → 65% continuation**
- Window: 09:00-11:00, Open 2hr correlation with rest-of-day: R²=0.530
- This is the ONLY actionable edge confirmed so far
- All other day-to-day patterns tested: No significant edges (≈50/50)

---

## Active Research Notebooks

### 1. CHAR_DE40_Direction_Given_Regime_Change.ipynb
**Finding:** NO EDGE
Tested if direction persists differently when volatility regime changes (stable vs rising vs falling).
**Result:** All regime transitions show ≈50/50 direction continuation. Volatility changes don't predict direction persistence.

### 2. CHAR_DE40_Directional_Persistence_DayOfWeek.ipynb
**Finding:** PENDING (Not yet run - robustness check)
Coarse check: Does 65% edge hold on Monday vs Friday vs mid-week?
**Expected:** If difference < 5%, pattern is robust. If > 10%, day-specific rules needed.

### 3. CHAR_DE40_Directional_Persistence_by_Regime.ipynb
**Finding:** NO SIGNIFICANT EDGE
Tested if today's direction predicts tomorrow's direction, separately by regime (Low/Normal/High).
**Result:** ~50-55% continuation across all regimes (not significant, p > 0.05).

### 4. CHAR_DE40_Volatility_Regime_Persistence.ipynb
**Finding:** WEAK PERSISTENCE
Tested if today's volatility regime predicts tomorrow's regime.
**Result:** 60-61% stay probability (vs 33% random). Statistically significant but weak for trading.

### 5. CHAR_DE40_Daily_Direction_Continuation.ipynb
**Finding:** NO EDGE
Tested if yesterday's direction + magnitude predict today's direction.
**Result:** 49.6% continuation (essentially 50/50). Move size and regime don't improve prediction.

### 6. CHAR_DE40_Direction_Magnitude_MomentumReversion.ipynb
**Finding:** THE 65% EDGE (only confirmed signal)
Tested if first-hour move (09-10) predicts rest-of-day behavior by regime.
**Result:**
- **Low vol + Strong UP → 65% continuation** ✓
- High vol + moves → ~50% (unpredictable, choppy)
- Normal vol → mixed results
- **This is intraday, not day-to-day**

### 7. CHAR_DE40_Volatility_Regime_Analysis.ipynb
**Finding:** MODERATE SIGNAL
Tested if early volatility (09-10) predicts daily regime.
**Result:** Correlation exists but modest. Used for position sizing (0.75x to 1.5x multiplier), not directional entry.

### 8. CHAR_DE40_Early_Session_Range_Analysis.ipynb
**Finding:** CONFIRMED MOMENTUM (53% R²)
Tested which early window (5min, 30min, 1hr, 2hr, premarket) predicts rest-of-day range.
**Result:**
- Open 2hr (09-11) best: R²=0.530, Pearson r=0.728
- Pattern: Large morning → large rest-of-day (momentum, not reversal)
- Effect size: 77% more rest-of-day volatility if opening in top 25%

---

## What Didn't Work (Dead Ends)

❌ **Day-to-day direction prediction:** 50/50 regardless of yesterday's move
❌ **Volatility regime changes affecting direction:** No predictive power
❌ **Yesterday's return predicting today:** No edge across any regime
❌ **Direction by regime:** ≈50/50 in Low, Normal, High vol regimes

---

## What Works (Confirmed)

✓ **Intraday momentum in quiet regimes** (65% continuation, first hour → rest of day)
✓ **Early volatility predicts daily regime** (R²=0.53, used for position sizing)
✓ **Volatility regime persistence** (60% stay probability, weak but real)
✓ **Large opening ranges predict large rest-of-day** (77% effect size difference)

---

## Data Standards (All Research)

- **Source:** M5 OHLCV bars, database (UTC stored)
- **Timezone:** Converted to Europe/Berlin via pytz (automatic DST)
- **Trading Hours:** 09:00-17:30 Berlin time only (RTH)
- **Regime Labeling:** Rolling 60-day percentile rank (Low/Normal/High), no look-ahead bias
- **Measurements:** Relative (percent returns, normalized by 20-day volatility), not absolute points
- **Sample Size:** 450+ trading days, sufficient for statistical tests
- **Significance:** p < 0.05 required, binomial tests for direction, correlation tests for ranges

---

## Trading Implications

### Only Use This Signal
**Quiet (Q1) + Strong UP (first hour) → 65% continuation to rest-of-day**
- Entry: After 10:00 AM if conditions met
- Position: Long bias, expect follow-through
- Stop: Standard levels (not tight)
- Exit: EOD or support breakage

### Don't Use These
- Day-to-day direction betting (no edge)
- "Tomorrow will continue today's direction" (no edge)
- Regime changes as direction signal (no edge)

### Use Volatility For
- Position sizing: 0.75x (quiet) to 1.5x (spicy) based on early regime
- Stop loss width adjustment
- Risk management only, not directional entry

---

## Next Research Directions

**Worth exploring:**
- Support/resistance levels (do opening highs/lows matter?)
- Gap analysis (overnight gaps predict or filled?)
- News calendar correlation (do patterns hold on quiet days only?)
- Intraday pullback magnitudes (relate to ATR regime?)

**Not worth pursuing further:**
- Day-to-day direction prediction
- Volatility regime as direction predictor
- Direction persistence by regime

---

## Summary

| Research | Question | Finding | Status |
|----------|----------|---------|--------|
| 1 | Direction given regime change? | No | Ruled out |
| 2 | Day-of-week effect? | TBD | Pending |
| 3 | Today→tomorrow direction by regime? | No | Ruled out |
| 4 | Regime persistence? | Weak (60%) | Confirmed |
| 5 | Yesterday→today direction? | No | Ruled out |
| 6 | First hour→rest-of-day (intraday)? | YES 65% (quiet+strong up) | **KEEP THIS** |
| 7 | Early vol→daily regime? | Moderate (R²=0.53) | Confirmed |
| 8 | Early range→rest-of-day range? | YES (R²=0.53, 77% effect) | Confirmed |

**Bottom line:** Focus on intraday patterns (first hour, quiet regime). Ignore day-to-day direction betting.

---

## File Locations

All notebooks in: `/quant_lab/notebooks/CHAR_DE40_*.ipynb`

Docs:
- VOLATILITY_REGIME_METHODOLOGY.md (methodology details)
- VOLATILITY_REGIME_QUICK_START.md (quick reference)
- WINDOW_RANKING_SUMMARY.md (early window rankings)

---

**Last Updated:** 2025-11-29
**Version:** 2.0 (simplified, actual findings only)
