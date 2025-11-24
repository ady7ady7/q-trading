# Window Ranking: Which Early Range is Best?

## Rank 1: WINNER - Open 2hr (09:00-11:00)

**Why This Window Is Best:**

| Metric | Value |
|--------|-------|
| **Pearson Correlation (r)** | 0.7280 |
| **R² (Predictive Power)** | 0.5300 (explains 53% of variance) |
| **p-value** | <0.0001 (highly significant) |
| **Spearman r** | 0.5400 (robust, rank-based) |
| **Signal Quality** | EXCELLENT |

**What This Means:**
- The 09:00-11:00 window explains **53% of rest-of-day range variation**
- This is your BEST early signal for predicting how much the market will move from 11:00-17:30
- The correlation is **not due to chance** (p < 0.0001)
- Even using rank-based correlation (more robust), it holds at 0.54

**The Practical Impact:**
- If you wait until 11:00 AM and measure the range formed so far
- You can predict the remaining day's volatility with 53% accuracy
- This is significantly better than the other windows

---

## Rank 2-5: One-Hour Windows (All Equally Weak)

| Metric | 1hr (09-10) | 30min (09-09:30) | 5min (09-09:05) | Premarket (08-09) |
|--------|---|---|---|---|
| **Pearson r** | 0.5970 | 0.5895 | 0.5895 | 0.5791 |
| **R²** | 0.3564 | 0.3476 | 0.3476 | 0.3353 |
| **Predictive Power** | 35.6% | 34.8% | 34.8% | 33.5% |

**Why They're All Similar:**
- The 5min, 30min, and 1hr windows are **nested subsets** of each other
- Correlation between them: 0.998-1.000 (basically identical)
- You're measuring the same thing 3 different times
- Not 3 independent signals, just 1 signal at different timeframes

---

## Key Numerical Observations for Trading

### [1] MAGNITUDE EFFECT - The Strongest Signal

**If you use the Open 2hr window (09:00-11:00):**

```
Small opening (bottom 25%):   Rest-of-day avg = 0.0081
Medium opening (25-50%):      Rest-of-day avg = 0.0090
Large opening (50-75%):       Rest-of-day avg = 0.0098
Very Large opening (75%+):    Rest-of-day avg = 0.0153
```

**Translation to DAX Points:**
```
Daily open ≈ 19,000 points (typical)

Small opening:       ~154 points rest-of-day expected
Very Large opening:  ~291 points rest-of-day expected

Difference:          +89% (Almost 2x as much!)
```

**ANOVA Test Result:** F = 10.11, p < 0.0001 (Highly significant)
- Rest-of-day ranges ARE statistically different across opening magnitude categories
- This is **NOT due to chance**

### [2] MOMENTUM PATTERN CONFIRMED (Not Mean-Reversion)

**Using 1hr window (09:00-10:00) for simplicity:**

```
Small opening:   0.0081 rest-of-day → Quiet rest of day
Large opening:   0.0143 rest-of-day → Active rest of day
Difference:      +77% (Much larger)
```

**Trading Implication:**
- This is **MOMENTUM**, not mean-reversion
- Large morning volatility predicts large rest-of-day volatility
- Quiet morning predicts quiet rest-of-day
- **Signal: "Volatility regime carries through the day"**

### [3] VOLATILITY RATIO - How Much Is Left to Trade?

**Opening 1hr contains about 26.9% of daily range:**
```
Typical daily range:      0.0142 (284 points on 19,000)
Opening 1hr avg:          0.0038 (76 points)
Rest-of-day expected:     0.0103 (206 points)
```

**Using 2hr window (better predictor):**
```
Opening 2hr avg:          0.0053 (106 points)
Rest-of-day expected:     0.0090 (171 points)
```

**Trading Window Efficiency:**
- **2-hour wait gives 53% predictive accuracy**
- **1-hour wait gives 36% predictive accuracy**
- **30-min wait gives 35% predictive accuracy**
- **5-min wait gives 35% predictive accuracy**

### [4] SIGNAL-TO-NOISE RATIO (How Reliable is the Edge?)

**For the best window (2hr, R² = 0.53):**

```
Explained variance:   53%
Unexplained (noise):  47%

Signal-to-Noise ratio: 0.53 / 0.47 = 1.13:1
```

**Translation:**
- For every 1 unit of "signal," there's 0.47 units of "noise"
- This is moderate predictive power, not strong
- You need multiple confirmations to trade this
- **Alone, it's not enough for profitable trading**

### [5] PRACTICAL THRESHOLDS - Actionable Trading Levels

**For Open 2hr window (09:00-11:00):**

```
25th percentile (Bottom 25%):  < 0.0030  →  Low volatility regime
75th percentile (Top 25%):     > 0.0071  →  High volatility regime
```

**In DAX Points (assume open = 19,000):**
```
Bottom 25%:  < 57 points in first 2 hours   →  Expect quiet rest-of-day
Top 25%:     > 135 points in first 2 hours  →  Expect active rest-of-day
```

**Prediction Accuracy by Regime:**
```
Low volatility opening:
  Expected rest-of-day range: 0.0081
  Actual range std dev: ±0.0038

High volatility opening:
  Expected rest-of-day range: 0.0143
  Actual range std dev: ±0.0140 (5x wider!)
```

### [6] THE REST-OF-DAY / EARLY RATIO (How Much Volatility Remains?)

**For Open 2hr window:**

```
Mean ratio:      2.22x  (rest is typically 2.2x larger than opening 2 hours)
Median ratio:    2.05x
Range (25-75%):  1.42x - 2.61x

% of days where rest > early: 93.4%
```

**Practical Trading Signal:**
- If you see 100 points in first 2 hours
- Expect ~200 more points (2.22x) in the remaining 6.5 hours
- But the range: 1.42x to 2.61x (high variability)

### [7] AUTOCORRELATION CONTROL (Does Yesterday Matter?)

**The Confounding Factor:**

```
Yesterday's range → Today's range: r = 0.457 (Significant!)
```

**This Matters Because:**
- 45.7% of the correlation might be "yesterday was volatile → today is too"
- Not just because "opening behavior predicts rest"
- The opening 2hr window might be picking up **volatility regime carry-over**
- Not an independent opening signal

**Recommendation:**
- **Filter: Only trade when yesterday was QUIET (low ATR) but today opened ACTIVE**
- This separates the real signal from autocorrelation noise

### [8] ACTIONABLE NUMBERS - Building Trade Rules

**Best Window: Open 2hr (09:00-11:00)**

```
Baseline rest-of-day expectation (all days):  0.0090 (171 points)

Small opening (< 0.0030):    0.0081 expect → -10% below baseline
Large opening (> 0.0071):    0.0143 expect → +59% above baseline

Difference worth trading: 59% above baseline = SIGNIFICANT
```

**Trade Rule Skeleton:**

```
At 11:00 AM Berlin time:
1. Measure range formed in first 2 hours (09:00-11:00)
2. Is it in top 25% (>0.0071)?
   YES → Expect 59% more volatility rest-of-day
   NO  → Expect 10% less volatility rest-of-day

3. Adjust position sizing:
   High volatility opening → Use 1.5x normal position
   Low volatility opening  → Use 0.75x normal position

4. Verify with yesterday's range:
   If yesterday was also quiet → Signal is STRONGER
   If yesterday was volatile → Signal is WEAKER (might be carry-over)
```

---

## Summary Table: All 5 Windows Ranked

| Rank | Window | Duration | Correlation | R² | Predictive Power | Wait Time |
|------|--------|----------|-------------|----|----|---|
| 1️⃣ | Open 2hr (09-11) | 120 min | 0.728 | 0.530 | **53.0%** | 2 hours |
| 2️⃣ | Open 1hr (09-10) | 60 min | 0.597 | 0.356 | 35.6% | 1 hour |
| 3️⃣ | Open 30min (09-09:30) | 30 min | 0.590 | 0.348 | 34.8% | 30 min |
| 4️⃣ | Open 5min (09-09:05) | 5 min | 0.590 | 0.348 | 34.8% | 5 min |
| 5️⃣ | Premarket (08-09) | 60 min | 0.579 | 0.335 | 33.5% | 60 min |

---

## The Honest Bottom Line

**Is there an edge?**
- **Yes, but conditional.** The 2hr window explains 53% of rest-of-day volatility variation.

**Is it tradeable alone?**
- **No.** 47% is still unexplained noise. You need:
  1. Position sizing based on volatility regime (not entry/exit)
  2. Autocorrelation filter (exclude yesterday-volatile days)
  3. Additional confirmations (support/resistance, order flow, etc.)

**Best Use Case:**
- Use the **2hr window (11:00 AM decision point)** to adjust position size and risk management for the rest of the day
- Don't use it as a standalone trading signal
- Use it as a **volatility regime filter** for other trading strategies

**Why 2hr beats the others:**
- 53% vs 36% predictive power is a 47% improvement
- You get 2 extra hours of data (more information)
- Autocorrelation from yesterday matters less with 2 hours of new information
- Trade-off: You wait longer, but the signal is worth it
