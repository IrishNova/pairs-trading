"""
Central configuration for the pairs-trading backtest.

Transaction costs are modelled PER LEG so each side of a pair can carry its own
venue, commission, borrow rate, and taxes. Today everything is domestic (US,
Interactive Brokers Pro Tiered); the per-leg shape is what lets a future
cross-venue trade (e.g. long US / short France) drop in without a rewrite — a
French leg would simply add its own commission and an ``ftt`` field the US legs
do not have.

Cost figures are IBKR Pro *Tiered* pricing (Sept 2026). Commission is stable and
well documented; the SEC/FINRA regulatory fees reset periodically and the short
BORROW RATE is stock- and date-specific — verify PM/MO's live borrow rate in
IBKR's short-sale-cost tool before trusting these defaults.
"""

# ---------------------------------------------------------------------------
# Backtest globals
# ---------------------------------------------------------------------------
TRADING_DAYS_PER_YEAR = 252   # annualization factor for Sharpe
BORROW_DAY_COUNT = 360        # IBKR accrues borrow fees on a 360-day basis
UNIT_SIZE = 1000              # shares of the dependent leg per position (indep leg = gamma * UNIT_SIZE)

# ---------------------------------------------------------------------------
# Per-leg cost model
# ---------------------------------------------------------------------------
# commission_per_share : IBKR Pro Tiered base rate ($/share)
# min_commission       : per-order minimum ($)
# max_commission_pct   : per-order cap as a fraction of trade value
# half_spread          : per-share, per-side slippage allowance — also the bucket
#                        we fold the small US SEC/FINRA sell-side fees into, to
#                        avoid false precision (n=5 trades, daily-close data)
# borrow_rate_annual   : annualized stock-loan fee, charged ONLY while the leg is
#                        short, accrued daily over BORROW_DAY_COUNT. ~0.25-0.50%
#                        for liquid General-Collateral names like PM/MO — VERIFY LIVE.
COST_CONFIG = {
    "PM": {
        "venue": "US",
        "commission_per_share": 0.0035,
        "min_commission": 0.35,
        "max_commission_pct": 0.01,
        "half_spread": 0.01,
        "borrow_rate_annual": 0.005,
    },
    "MO": {
        "venue": "US",
        "commission_per_share": 0.0035,
        "min_commission": 0.35,
        "max_commission_pct": 0.01,
        "half_spread": 0.01,
        "borrow_rate_annual": 0.005,
    },
}
