# Quantitative Lab Research Index

## Overview
Central index of all research notebooks and analysis in the quant_lab directory. Each entry links to the corresponding Jupyter notebook and provides executive summary.

---

## Active Research

### 1. CHAR_DE40_Volatility_Regime_Analysis.ipynb
**Status:** ACTIVE (Created 2025-11-25)

**Objective:** Determine if first-hour volatility (09:00-10:00 Berlin time) on DAX can predict the full-day volatility regime.

**Data:**
- M5 (5-minute) OHLCV bars
- Date range: Jan 2023 - Sept 2025
- Timezone: UTC → Europe/Berlin (with DST handling)

**Key Features:**
- True Range (TR) calculation for M5 granularity
- Daily ATR % (ATRP) as regime target
- Rolling percentile rank labeling (Low/Normal/High)
- Early session relative strength (20-day comparison)

**Output Metrics:**
- Pearson & Spearman correlation (early vs daily volatility)
- Conditional probability P(High Regime | Early Strength Quartile)
- Regime transition heatmap
- Volatility regime thresholds for position sizing

**Trading Application:**
- Position size adjustment: 0.75x to 1.5x multiplier
- Stop loss width adjustment based on expected daily volatility
- Decision point: 10:00 AM Berlin time

**Next Steps:**
- Run notebook and evaluate correlation strength
- Test on out-of-sample data (Sept 2025+)
- Compare with alternative volatility metrics
- Explore direction patterns (momentum vs mean-reversion)

**Documentation:**
- See [VOLATILITY_REGIME_METHODOLOGY.md](../docs/VOLATILITY_REGIME_METHODOLOGY.md)

---

### 2. CHAR_DE40_Early_Session_Range_Analysis.ipynb  ---- REPEATED LATER WITH EVEN BETTER RESULTS
**Status:** COMPLETED & ANALYZED (Created 2025-11-24)

**Objective:** Analyze correlation between early session ranges (5 windows) and rest-of-day ranges.

**Data:**
- M1 (1-minute) OHLCV bars
- 300-day sample (Nov 2024 - Sept 2025)
- Timezone: UTC → Europe/Berlin

**Key Features:**
- Relative range measurements (not points)
- 5 early windows analyzed: Premarket, 5min, 30min, 1hr, 2hr
- Pearson, Spearman, R² correlation metrics
- Binning analysis and ANOVA significance testing

**Key Findings:**

| Window | Correlation (r) | R² | Predictive Power |
|--------|---|---|---|
| **Open 2hr (09-11)** | 0.728 | 0.530 | **53.0%** ✓ |
| Open 1hr (09-10) | 0.597 | 0.356 | 35.6% |
| Open 30min (09-09:30) | 0.590 | 0.348 | 34.8% |
| Open 5min (09-09:05) | 0.590 | 0.348 | 34.8% |
| Premarket (08-09) | 0.579 | 0.335 | 33.5% |

**Pattern Identified:** MOMENTUM (not mean-reversion)
- Large opening ranges predict larger rest-of-day ranges
- Small opening ranges predict smaller rest-of-day ranges
- Difference: 77% larger rest-of-day when opening is in top 25%

**Diagnostic Results:**
- Window nesting: 89-100% correlation between windows (expected subset behavior)
- Autocorrelation: Daily range shows 0.457 lag-1 correlation (yesterday matters)
- Random data: No significance (sanity check passed)
- Mathematical artifact: Confirmed opening + rest ≈ daily range

**Edge Assessment:** Moderate, conditional on volatility regime
- Explains 53% of variance (good but not magic)
- Actionable only with proper position sizing, not directional entry

**Documentation:**
- See [WINDOW_RANKING_SUMMARY.md](../../WINDOW_RANKING_SUMMARY.md)

---

## Planned Research

### 3. CHAR_DE40_Direction_Analysis.ipynb (Planned)
**Objective:** Analyze if opening move direction predicts rest-of-day direction.

**Hypothesis:**
- Opening gap UP + maintained momentum = likely to continue up
- Opening gap UP + quick reversal = mean-reversion likely

**Features:**
- Opening direction (up/down/neutral)
- Speed of reversal (if any)
- Rest-of-day direction
- Win rate by opening pattern

---

### 4. CHAR_DE40_Support_Resistance.ipynb (Planned)
**Objective:** Test if opening range highs/lows act as support/resistance for rest-of-day.

**Hypothesis:**
- Opening hour creates boundaries
- Market respects these levels during rest-of-day
- Can be used for directional trading

---

## Completed Research (Previous Sessions)

### CHAR_DE40_Intraday_Volatility.ipynb
**Status:** ARCHIVED

**Findings:** Early session analysis showing correlation between morning volatility and daily range.

---

## Research Templates & Standards

All research notebooks should follow this structure:

1. **Part 1: Data Engineering**
   - Timezone handling with verification
   - RTH filtering
   - Feature calculation

2. **Part 2: Feature Construction**
   - Target variable definition
   - Predictor variable definition
   - Statistical normalization

3. **Part 3: Statistical Validation**
   - Correlation analysis (Pearson, Spearman)
   - Significance testing (p-values)
   - Predictive power metrics

4. **Part 4: Visualization**
   - Scatter plots with trend lines
   - Box plots by category
   - Heatmaps for transitions

5. **Part 5: Summary & Findings**
   - Executive summary
   - Key metrics
   - Practical implications
   - Next steps

---

## Data Standards

### Timezone Rules
- **Storage:** UTC
- **Analysis:** Europe/Berlin (CET/CEST with DST)
- **Conversion:** Always explicit (never assume)
- **Verification:** Check offsets at DST transitions

### Trading Hours
- **RTH (Regular Trading Hours):** 09:00-17:30 Berlin time
- **Pre-market:** 08:00-09:00 (analyzed separately if included)
- **Post-market:** 17:30+ (excluded from main analysis)

### Data Quality
- Minimum 100 bars per trading day (for M5: ~8 hours)
- Drop days with <50 bars (holidays, early closes)
- Verify no duplicate timestamps
- Check for 5-minute alignment (m5 bars at :00, :05, :10, ... :55)

### Naming Conventions
- Notebook: `CHAR_[SYMBOL]_[TOPIC]_[VERSION].ipynb`
- Example: `CHAR_DE40_Volatility_Regime_Analysis.ipynb`
- Documentation: `[TOPIC]_METHODOLOGY.md`
- Example: `VOLATILITY_REGIME_METHODOLOGY.md`

---

## Key Learnings Across Research

1. **Window Sizing Matters**
   - 5-min, 30-min windows are too short
   - 1-hour and 2-hour windows provide better signal
   - 2-hour window has 47% better predictive power than 1-hour

2. **Relative Measurements > Absolute**
   - Normalize by price (percent) not points
   - Remove daily volatility bias
   - Comparable across time periods

3. **Volatility Persistence**
   - Autocorrelation is strong (r=0.45)
   - "Yesterday's regime matters" confounds analysis
   - Filter for regime change days

4. **Correlation ≠ Causation**
   - High correlation might be mathematical artifact
   - Components of same total create spurious correlation
   - Run diagnostic checks (random data, alternative measures)

5. **Actionable Edge Requires**
   - Correlation R² > 0.25 (explains 25%+ variance)
   - Out-of-sample validation
   - Practical application (position sizing, not just signal)
   - Edge difference > 15% above baseline

---

## Dashboard of Key Metrics

### Early Session Range Analysis
```
Strongest Correlation:  Open 2hr (r=0.728, R²=0.530)
Pattern Type:           Momentum (large opening → large rest)
Magnitude Effect:       77% more volatility if opening in top 25%
Signal Quality:         Moderate (47% unexplained variance)
Trading Edge:           Position sizing only, not directional
```

### Volatility Regime Analysis
```
Correlation:            [PENDING - run notebook]
Regime Distribution:    Low 33%, Normal 33%, High 33% (rolling percentile)
Early Strength Effect:  [PENDING - run notebook]
Actionable Edge:        [PENDING - run notebook]
Decision Point:         10:00 AM Berlin time
Position Multiplier:    0.75x to 1.5x based on early strength
```

---

## How to Use This Index

1. **Start Here** if you're new to the research → Read this index
2. **Find Active Research** → See "ACTIVE (Created date)" section
3. **Review Key Findings** → Check metrics tables
4. **Read Methodology** → Link to detailed .md documentation
5. **Understand Standards** → Review "Data Standards" section
6. **Run Notebooks** → Execute in order (dependencies managed internally)

---

## Document Control

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-25 | 1.0 | Analysis | Created index, added early session analysis findings |
| 2025-11-25 | 1.1 | Analysis | Added volatility regime research structure |

