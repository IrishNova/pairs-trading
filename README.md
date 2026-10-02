# Pairs Trading: Cointegration Stat-Arb Research Engine

## Brief
Cointegration-based stat-arb pairs-trading research engine that uses transparent validation rather than a curve-fit backtest, where no pair in the candidate universe survives honest out-of-sample validation.

## Motivation
This project was completed to dually produce a working model which demonstrates my coding ability as well as my trading acumen. It prioritizes methodology transparency, with out-of-sample validation favored over simply fitting an in-sample curve. Given that rigor, none of the candidate pairs survived the process, and I can point to exactly why each one failed using cold-hard stats.

## Theory
A multi-metric model was used to determine a potential pair's suitability. The two assets are each non-stationary on their own (they behave like random walks), but for the pair to be tradeable, the spread between them needs to be stationary, such that its mean, variance, and autocorrelation stay constant over time. That is, does the spread actually revert over time, or is it merely a random walk? This cannot be confirmed using OLS regression alone. Rather, the model uses cointegration, which determines if there is an honest relationship that spurious regression would misidentify.

That being the case, this app uses the Engle-Granger method to test for cointegration, and does so in two steps. First, OLS regresses one price on the other to find the hedge ratio plus the residual. Next, it runs a stationarity test on that residual.

Engle-Granger is treated as the primary test, and it uses adjusted critical values because the residual was fitted to look as stationary as possible. As a cross-check, a raw ADF test is also run on the residual to test whether the series has a unit root. The null hypothesis is that the series has a unit root (is non-stationary), which may be rejected by finding a low p-value.

Finally, the half-life of the spread is calculated to determine how fast it reverts.

## Methodology
In order to build a system that is as robust as possible, a two-stage approach was taken. The first stage screened an array of candidate pairs, assembled with economic reasoning in mind. That is, two stocks may statistically appear as a relevant pair, but if they're two drastically different businesses, then the significance is an illusion.

Second, the top ranked prospects are scrutinized to validate their profitability. Step two strikes at the heart of the 'don't just curve match' thesis.

The system is built on the following components:

- Data ingestion: While I actively trade using an Interactive Brokers data feed, this research project uses simple yfinance to provide data. Any real-world research would use a better quality of data, but given the scope of this project, I felt using something simpler which wouldn't ever strain my existing trading system's data feed to be the way to go.

- Cointegration screening: these are the three metrics which are run on every pair and used to rank them in order to determine which should be carried forward into the second stage.

- Spread construction + z-score: Once a pair clears screening, I build the spread using the hedge ratio from the regression, which is one asset minus the hedge-adjusted other. From there the spread gets converted into a z-score, which measures how far it has drifted from its mean in standard deviations. That lets me treat any pair on the same scale, no matter what the underlying prices are.

- Signal generation: The z-score is what actually triggers trades. When the spread stretches far enough from its mean I enter, betting it reverts. When it returns to the mean I exit. If it stretches too far past that, a stop closes the position in case the relationship has broken. This is where the bar-by-bar for loop lives, since the position has to be tracked as it moves through each bar.

- Backtest: Following the statistical tests, a backtest runs over every bar of the data, ensuring the strategy is tested exactly as it would be implemented.

- Walk-forward validation: Because a backtest can lie, the data is split into a development slice used for selecting the pair and a hold-out slice used only for validation, which selection never sees. On the hold-out, the walk-forward re-estimates the hedge ratio on a rolling training window and trades the next unseen window, so nothing from the future leaks into a fit. This is what makes the out-of-sample findings honest.

## Design Decisions

**Economic coherence over raw statistics.** I find that new students to quantitative trading often take a naive approach to statistical analysis. My time serving with the Special Forces in Afghanistan, along with two professors' perspectives, have pushed me to be much more rigorous. The lesson I keep coming back to is that life is about more than statistics. Something may look great on paper but present serious dangers due to overlooked information. Call them logical fallacies, or an uninformed view, but these are the things which cause harm. Extrapolating that to this project, a pair testing as statistically significant means nothing if the underlying economic story isn't aligned with reality. One concrete check I built in is on the hedge ratio itself. Two stocks that genuinely move together should produce a positive hedge ratio, so when a pair tested well but came back with a backwards, negative ratio, I threw it out. KO and PEP were exactly this case, a low p-value paired with a hedge ratio that made no economic sense. Ford Motors and Verizon would be a fugazi even if they tested well, while Ford and GM at least present real economic reasoning, so long as the statistics back it up.

**Anti-churn on stop-outs.** In the real world, being stopped out of a position causes one to steer clear of it at least until things settle down. Initially when constructing the backtest, I omitted this truth, which made for highly unrealistic findings. A soldier whose company sustained heavy losses is unlikely to rush back into the same battle space which caused them. It follows that the backtest features an anti-churn mechanism which prevents it from re-entering terrain which just caused damage to the PnL.

**Two-stage screening to avoid p-hacking.** To do my best to avoid trusting a pair naively, I separated the model into two parts. If you test enough candidate pairs, some will pass a p<0.05 filter by pure chance, which is essentially p-hacking. Separating the wide-net screening from the focused, out-of-sample analysis is how I guard against that, so a pair has to earn its place rather than get lucky once.

**Tradeability gate on half-life.** Cointegration alone does not make a pair tradeable. A pair can be statistically cointegrated and still revert far too slowly to trade, which is exactly what happened with WM/RSG and its 190 day half-life. I added a half-life gate so a pair has to revert fast enough to be worth trading, not just pass a statistical test.

## Results
The candidate universe was screened on the development slice of each pair's history, so selection never touched the hold-out data. To qualify, a pair had to clear two gates, a cointegration p-value below 0.05 and a mean-reversion half-life short enough to actually trade, which I set at under 60 days.

| pair | eg_pval | half-life (days) | qualifies |
|------|---------|------------------|-----------|
| WM / RSG | 0.025 | 190 | No |
| XOM / CVX | 0.28 | 100 | No |
| PM / MO | 0.53 | 245 | No |
| NLY / AGNC | 0.60 | 105 | No |
| TRV / ALL | 0.72 | 578 | No |
| V / MA | 0.77 | 142 | No |
| HD / LOW | 0.89 | 849 | No |
| AAPL / MSFT | 0.90 | 1043 | No |
| KO / PEP | 0.97 | 497 | No |

Not a single pair qualified. Eight of the nine were killed at the first gate, with cointegration p-values nowhere near significant on the development slice. Only WM / RSG, the waste-hauling duopoly, passed the cointegration test, but it failed the second gate badly, with a half-life of 190 days. That means the spread takes the better part of a year to revert, which is far too slow to trade.

Two pairs are worth a closer look.

PM / MO is the pair an earlier version of this project selected, back when screening was done on recent data alone. On recent history it looked strong. Once it was screened honestly on the earlier development slice it had never been tuned to, its cointegration p-value came back at 0.53, a complete failure. This is textbook selection bias. The pair only ever looked good because the earlier process let it peek at the data it was later tested on.

WM / RSG shows the other lesson. It genuinely passed the cointegration test, so the statistical relationship is real. But passing cointegration does not make a pair tradeable. With a 190 day half-life it barely moves, generating a single trade across seventeen years of development data, and that trade lost money. Pushed through to the hold-out it lost money there too, on both a rolling and an expanding basis. Statistically real, practically useless.

## Key Finding
The headline finding is that no pair in the candidate universe survived honest validation. That is not a failure of the project, it is the project working as designed. The system has two features which make this result trustworthy. First, a proper hold-out, where pair selection happens on an early slice of data and validation happens on a later slice the system has never seen, which removes selection bias. Second, a half-life gate, which rejects pairs that are statistically cointegrated but revert too slowly to trade. Together these catch the two most common ways a pairs strategy fools you, picking a pair because it looked good on the test data, and trusting a cointegration result that is real but not tradeable.

## Limitations
This project has real limitations worth stating plainly.

- The data is yfinance daily closes, which is retail-grade. My live trading uses a better feed, and anything moving toward real capital would too.
- The candidate universe is small and hand-picked. A wider scan might surface a pair that qualifies, but it would also multiply the multiple-testing problem, so a wider search would need even stricter correction.
- The gates are my chosen thresholds. A p-value of 0.05 and a 60 day half-life are reasonable, but they are judgment calls, and different thresholds would change which pairs qualify.
- Statistical power is low. The qualifying pairs barely trade, so even the hold-out results rest on very few trades. The conclusion is better read as no evidence of a tradeable edge than as proof that one is impossible.
- Transaction costs and borrow rates are modeled estimates, not pulled live. They are realistic but would need confirming before trading.
- Daily-close equity pairs are one of the most picked-over corners of the market, so finding a durable edge here was always unlikely.

## What Didn't Work
It is worth being honest about the pairs I expected to work and didn't. Several of my candidates had strong economic stories behind them. HD and LOW are a home-improvement duopoly fighting over the same customer. KO and PEP are the textbook consumer-staples pair. V and MA are a payment-network near-duopoly. On paper these should be about as close to cointegrated as equities get.

None of them came close on the development slice. KO and PEP tested at a p-value of 0.97, V and MA at 0.77, and HD and LOW at 0.89, all nowhere near significant. A compelling economic story clearly is not enough. Two businesses can be as similar as any in the market and still never form a spread that reliably reverts, because things like different growth rates, capital structures, and idiosyncratic shocks pull their prices apart over time.

This is the mirror image of the economic-coherence point made earlier. There, statistics without an economic story was a trap. Here, an economic story without the statistics to back it up is just as much of one. A pair needs both, and most of mine had neither in the end.

## Future Work
There are two directions I would take this next.

The first is widening the search. Right now the candidate universe is a short, hand-picked list. The natural extension is an automated scanner that casts a much wider net across sectors, feeding candidates into the same engine. The catch is that a wider search makes the multiple-testing problem worse, so it would have to come with stricter correction, otherwise you are just manufacturing false positives at scale. Done properly though, it turns this from a tool that checks a handful of pairs into a radar that scans for opportunity across the whole market.

The second is moving from pairs to baskets. Instead of trading one stock against another, you trade a single name against a basket of its peers, which stands in for the sector's common factor. This is the approach Avellaneda and Lee describe, and it tends to be more stable than a single pair because a basket averages out the idiosyncratic noise that breaks two-stock relationships. The engine is already built to be generic about what it screens, so extending it from a pair to a name-versus-basket is a natural step rather than a rebuild.

## References
- Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). Pairs Trading: Performance of a Relative-Value Arbitrage Rule. *Review of Financial Studies*.
- Engle, R. F., & Granger, C. W. J. (1987). Co-integration and Error Correction: Representation, Estimation, and Testing. *Econometrica*.
- Avellaneda, M., & Lee, J. H. (2010). Statistical Arbitrage in the US Equities Market. *Quantitative Finance*.

## Running It
Clone the repo, create a virtual environment, and install the dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the pipeline:

```
python main.py
```

This screens the candidate universe on the development slice, prints the ranked table with the qualifies column, and runs the full validation on whatever is listed in PROSPECTS.

To change what gets tested, edit `config.py`:
- `CANDIDATE_PAIRS`, the universe that gets screened
- `PROSPECTS`, the pairs carried into full validation
- `EG_GATE`, `HALF_LIFE_MAX`, and `DEV_FRAC`, the thresholds and the dev/hold-out split
