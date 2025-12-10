21.11, Day 1 (of this devlog)
- I've tested manually some data points and it makes the most sense to keep the current candles in UTC and simply be aware of the possible changes (DST) during every single research and cross-check a few candles from the dataset manually on TradingView to confirm that we're analyzing the proper time of the day - at least for some time it makes sense to me to keep it manual
- I've done the first attempt to research High/Low forming on DAX - it definitely doesn't give an edge by itself, but it definitely gives some useful observations - a lot of Hods/Lods form during the early market hours, we're looking at around 60% of Hods/Lods formed by 10:00 - this is to be further explored/confirmed and repeated in the future AS I REMEMBER THESE NUMBERS BEING EVEN HIGHER WHEN I'VE DONE THE RESEARCH IN THE PAST
- I've also done some attempts to look over pullbacks - we could be looking at a sweet spot of around 10 ATR14 (m1) from the local high as an expected pullback magnitude. However, I NEED TO RESEARCH THESE PULLBACKS ON THEIR OWN + also check these in relation to overall ATR regime (in relation to 8-9 range or 9-10 range, probably both)

22.11, Day 2
- I added some docs + DST manual validation instructions - THIS IS AN ABSOLUTELY CRITICAL THING TO DO and I want to check it at least for a first few research projects, whether the offset is correct and we're making right observations (as DST offset between winter/summer time shift could POTENTIALLY also change how we should offset our data from the database).

24.11, Day 3
- I ran another research on volatility correlation between the early range (tested multiple options) and the range of the rest of the day (11-17:30). Some key observations: Ther is a 53% predictive accuracy for predicting rest-of-the-day range after waiting for the first 2 hours (9-11). Pearson r = 0.728; p < 0.001 and generally large volatility morning signifies large volatility for the rest of the day; quiet morning -> quiet rest-of-day; 
THIS IS NOT A STRONG EDGE, but rather an observation of medium predictive power of session momentum, but it is there, and we can explore DAX further to find more similar observations that could support a bias and perhaps build a stable edge.

25.11, Day 4
- This time I've used my own trading experience, the brilliance of the smartest math LLM (Gemini according to the LLM leaderboard as of today) to properly plan out the research and then obviously used the smartest coding LLM which resulted in quite fruitful reveal of a potential edge with over 70% prediction accuracy - this is still to be verified, but it seems that I have my first actionable and scientifically proven edge that I will definitely try out or maybe back up with more scientific observations. NICE!

27.11.25 Day 5
- After following up with Volatility Regimes + Direction -> Mean Rev vs Continuation reseearch - it seems that the best pattern to work with (that I can actually calculate beforehand) is actually a quiet (Q1) volatility regime + strong up movement during the first hour (9:00 - 10:00) - it gives a 65% for continuation up. The other regimes don't give such an edge, so I can assume that Q4 is choppy and can go both ways (est. 50-60% for continuation, unstable)
- I already planned a follow up research of day-to-day continuation patterns depending on regimes and maybe some other factors

29.11.25 Day 6 (Saturday)
- While I'm doing the research, I'm downloading about 3 more years of data to my DB - doing it, but honestly I believe the markets change so much that IT MIGHT NOT BE THE BEST IDEA - we will see though.
- Research 1 (CHAR_DE40_Volatility_Regime_Persistence): started with a simple Volatility Regimes day-to-day correlation - the results were not super meaningful, but we have roughly 61.5% continuation on HIGH->HIGH regime + 60% on LOW->LOW regime day-to-day.
- Research 2 (CHAR_DE40_Directional_Persistence_by_Regime). 
I decided to extend my current research to also take the direction into account (obviously not only up -> up, down -> down, but also continuation/mean rev tendentions + days of the week).
- As for day-to-day direction continuation based on the previous day move (direction + magnitude, normalized on regimes), it gives no edge and direction seems to be very close to 50/50 - absolutely useless - NO SIGNIFICANT EDGE!
- Research 3 (CHAR_DE40_Daily_Direction_Continuation) -  checks day-to-day directional perstistence based on the yesterday's volatility regime (all day). Although this seems to be the same as reserach above. We confirmed that there's NO SIGNIFICANT EDGE based on that in none of those regimes - the results are mixed.
- Research 4 (CHAR_DE40_Direction_Given_Regime_Change) - DAY-TO-DAY direction given volatility regime changes seem to give NO STATISTICALLY SIGNIFICANT PREDICTIVE POWER beyond 50/50 - they are useless for the time being 
- Research 5 (CHAR_DE40_Directional_Persistence_DayOfWeek)  - testing day-to-day directional persistence based on day of week.
- TLDR: NO STATISTICALLY MEANINGFUL EDGES or POSITIVE FOUNDINGS TODAY, but we've eliminated the possibility of these (pd volatility regime + pd direction + pd volatility regime changes) being SIGNIFICANT, which is also nice!
+ moved today's notebooks to a new folder archive/ as they don't seem to have a lot of use - might delete them later


30.11.25 (Day 7)
- Replicated my previous research (Volatility Regimes + FHM) using slightly different FHM calculation approach (more H-L oriented than O-C) - the findings are promising imo and COULD POTENTIALLY BUILD A VALID STRATEGY WITH CERTAIN ADJUSTMENTS

9.12.25 (Day 8)
- Today's research focuses on quantifying the probabilistic advantage of DAX 9:00 and 10:00 prices in relation to the daily PP in predicting the daily close and the touch probability of R/S levels - CHAR_DE_40_Pivot_Point_Predictive_Power.ipynb. The H0 was rejected, and it seems to have a PRETTY HIGH EDGE, and I will want to backtest it further! We could also do a similar research and calculate PP on the basis of 8:00-9:00 and 9:00-10:00 and set different time windows.
I could try to set up a backtest for a very simple strat (TP -> R1, SL -> S1 - while checking that R:R is at least 2:1 [We risk twice as much as we gain])
That's one of the two researches I'm planning to do in relation to DAX, and sooner or later I will also move to check NASDAQ. The second research will focus on Pullbacks.

10.12.25 (Day 9)
- Today I'm recreating yesterday's research WITH MUCH MORE DETAILED AND GRANULAR APPROACH - we're looking at different scenarios of openings (not only above/below PP, but also above R1, R2, S1 etc.) AND we're also looking at more granular targets (0.25, 0.5, 0.75 between the pivot points) to get more detailed data.
- The research again seems to be very promising and I've found POTENTIAL scenarios that could serve as great examples for a mechanical strategy - almost all of them seem to make sense, but I will have to test it out more.