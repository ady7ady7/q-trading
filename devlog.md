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