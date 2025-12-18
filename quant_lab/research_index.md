# DAX Research Index

**Period:** Jan 2023 - Sept 2025 (M5 data, 09:00-17:30 Berlin time)
**Status:** 14 research notebooks, key edges identified, many dead ends ruled out

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

### 9. CHAR_DE40_HL_Based_First_Hour_Move.ipynb
**Finding:** PENDING (Alternative classification method)
Tested if high/low-based first-hour move (vs open/close) improves edge detection.
**Method:** First-hour classified by range structure (StrongUpHL, StrongDownHL, Balanced, Quiet) instead of open-close return.
**Hypothesis:** HL structure might capture volatility + direction better than simple O/C return.
**Two periods tested:** 2020-2025 (full) and 2023-2025 (recent)
**Expected:** If no improvement over existing 65% edge, confirms original method is sufficient.

### 10. CHAR_DE40_Pivot_Point_Predictive_Power.ipynb
**Finding:** PENDING (Standard pivot levels)
Tested if opening position (09:00) relative to standard pivot point predicts R/S level hits and closing outcome.
**Method:**
- Calculate pivot point from previous day H/L/C
- Test: Open > PP → R1/R2/R3 hit probability
- Test: Open < PP → S1/S2/S3 hit probability
- Test: 10:00 confirmation adds value vs 09:00 only
**Hypothesis:** If Open > PP, expect higher probability of hitting R1 (> 60%).
**Edge threshold:** Strong = 60%+, Weak = 55-60%, None = <55% (≈random)

### 11. CHAR_DE40_Pivot_Points_Detailed_Excursion_Study3.ipynb
**Finding:** Findings in devlog -> subject to conditional research (12.)
Measures probability of reaching fractional targets between pivot levels, conditioned on opening zone.
**Method:**
- ALL targets measured LOW→HIGH as absolute price levels (e.g., S2, S1_S2_050, S1, S1_PP_025, PP)
- 8 opening zones: Above_R3, R2_R3, R1_R2, PP_R1, S1_PP, S2_S1, S3_S2, Below_S3
- Fractional targets: 0.25, 0.50, 0.75 of each range
- Simple reach: Did day's [Low, High] include this level?
**Hypothesis:** Certain opening zones have asymmetric probabilities (e.g., PP_R1 zone → 80% reach PP_R1_050 but only 30% reach PP_R1_075).
**Use:** Identify highest-probability fractional targets for profit-taking and stop placement.

### 12. CHAR_DE40_Pivot_Points_Conditional_Probabilities2.ipynb
**Finding:** There are very promising scenarios with positive delta and I will definitely backtest them - findings in devlog/private notes.
Measures "Given we reached level X, what's the probability of reaching level Y AFTER that during the same session?" for STANDARD pivots (previous day H/L/C).
**Method:**
- Track FIRST timestamp when each level is touched (using M5 intrabar data)
- Calculate P(Target | Condition, Zone) = Count(Target reached AFTER Condition) / Count(Condition reached)
- Temporal ordering enforced: Only count if timestamp_target > timestamp_condition
- Extended targets: All fractional levels (025, 050, 075) across all ranges
**Example:** Zone S1_PP, Condition "reached S1" → What's probability of reaching S2 AFTER S1? PP AFTER S1?
**Critical Fix:** Eliminates false positives from reverse ordering (where target was reached BEFORE condition).
**Hypothesis:** After hitting certain levels, probabilities change dramatically (e.g., after S1 hit, 85% chance of PP but only 40% of S2 = mean reversion edge).
**Use:** Build decision trees for intraday trading ("if zone X and level Y hit, then target Z with W% probability").

### 13. CHAR_DE40_Local_Pivot_Conditional_Probabilities.ipynb
**Finding:** PROMISING - to be backtested (potentially superior to standard pivots for intraday)
Measures conditional probabilities using LOCAL pivots calculated from FIRST HOUR (9:00-10:00) instead of previous day.
**Method:**
- Calculate local pivots from first hour H/L/C using standard formulas: LPP = (H+L+C)/3, LR1 = (2×LPP)-L, etc.
- Classify opening zone at 10:00 (where price is relative to local pivots)
- Track conditional probabilities for 10:00-17:30 session
- **CRITICAL FIX:** To reach target, ALL intermediate levels must be crossed - sometimes more than one level was crossed ON A SINGLE m5 candle, and it only counted the FARTHEST level; We've fixed that with using >= for candle timestamps
**Hypothesis:** First hour establishes intraday support/resistance more relevant than overnight levels. Local pivots may provide stronger conditional edges for same-day trading.
**Advantage over standard pivots:** Reflects current day's intraday dynamics rather than previous day context.
**Use:** If backtesting confirms superiority, use first hour (9:00-10:00) to establish local levels, then trade 10:00-17:30 based on local pivot conditional probabilities.
**Status:** Potentially promising, requires backtesting vs standard pivot approach to determine which is superior.

### 14. CHAR_DE40_Local_Pivot_Conditional_By_Regime.ipynb
**Finding:** Positive delta scenarios identified in regime-specific conditions - to be backtested
Extends local pivot conditional probabilities by splitting results across volatility regimes (Q1 Quiet, Q2, Q3, Q4 Spicy).
**Method:**
- Uses LOCAL pivots from first hour (9:00-10:00) like research #13
- Calculates Early_TR (True Range sum across first hour) as volatility metric
- Dynamic quartile assignment: Trim top/bottom 5% outliers, then rolling 60-day percentile rank
- Regime classification: Q1 (0-25th percentile), Q2 (25-50th), Q3 (50-75th), Q4 (75-100th)
- Calculate P(Target | Condition, Zone, Regime) for each quartile separately
- Compare Q1 vs Q4 deltas to identify regime-specific edges
**Hypothesis:** Certain local pivot conditional patterns may be stronger in quiet markets (mean reversion) or spicy markets (momentum continuation).
**Key Innovation:** Adaptive regime thresholds based on rolling percentiles rather than fixed values - accounts for changing market conditions over time.
**Use:** Identify which zone-condition-target combinations show large Q1-Q4 deltas (>15-20%) for regime-conditional trading rules.
**Status:** Positive delta scenarios spotted in specific regime-zone-condition combinations, requires backtesting to validate edge persistence.



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
| 9 | HL-based first hour (alternative)? | StrongUpHL -> 81% continuation (N = 212, 0.8/week) | Confirmed, Skeptical - I guess it depends on execution, this is not yet written down in Key findings, still TBC
| 10 | Pivot points predict R/S hits? | OPEN > PP -> R1 (79%) -> R2 (49%); similar rates in relation to S1/S2 below PP | Confirmed - KEEP + TEST FURTHER, not yet written down in key findings, to be tested!
| 11 | Fractional pivot targets by zone? | See research 12 (conditional) | Pending - superseded
| 12 | Conditional probabilities after level hit (standard)? | Promising scenarios found | To backtest
| 13 | Conditional probabilities - LOCAL pivots (first hour)? | Promising - potentially superior to standard | To backtest vs standard
| 14 | LOCAL pivot conditionals BY REGIME (Q1-Q4)? | Positive delta scenarios in specific regime-zone-condition combos | To backtest

**Bottom line:** Focus on intraday patterns (first hour, quiet regime). Ignore day-to-day direction betting. Test pivot levels and HL-based classification to confirm or improve existing edge.

---

## File Locations

All notebooks in: `/quant_lab/notebooks/CHAR_DE40_*.ipynb`

Docs:
- VOLATILITY_REGIME_METHODOLOGY.md (methodology details)
- VOLATILITY_REGIME_QUICK_START.md (quick reference)
- WINDOW_RANKING_SUMMARY.md (early window rankings)

---

**Last Updated:** 2024-12-18
**Version:** 2.2 (added local pivot conditional probabilities with regime-specific analysis)
