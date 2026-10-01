import pandas as pd
from config import CANDIDATE_PAIRS, PROSPECTS, UNIT_SIZE, DEV_FRAC, EG_GATE, HALF_LIFE_MAX
from data import fetch_raw_data
from screening import screen_pair
from spread import construct_spread, zscore
from signals import generate_signals
from backtest import backtest
from walkforward import walk_forward
from metrics import (trade_pnls, mae, volatility, skew, excess_kurtosis, max_return,
                     min_return, semi_deviation, sharpe, sortino, s_ratio, var_95,
                     cvar_95, win_rate, max_drawdown, drawdown_duration)


def split_dev_holdout(df):
    cutoff = int(len(df) * DEV_FRAC)
    return df.iloc[:cutoff], df.iloc[cutoff:]


def screen_universe(pairs, period='max'):
    rows = []
    for pair in pairs:
        try:
            df = fetch_raw_data(pair, period=period)
            dev, _ = split_dev_holdout(df)
            rows.append(screen_pair(dev))
        except Exception as e:
            print(f"skip {pair}: {e}")
    table = pd.DataFrame(rows).sort_values('eg_pval')
    table['qualifies'] = ((table['eg_pval'] < EG_GATE)
                          & (table['half_life'] > 0)
                          & (table['half_life'] < HALF_LIFE_MAX))
    return table


def validate(pair, period='max'):
    df = fetch_raw_data(pair, period=period)
    dev, holdout = split_dev_holdout(df)

    res = screen_pair(dev)
    gamma, alpha = res['gamma'], res['alpha']
    spread = construct_spread(dev, gamma, alpha)
    z = zscore(spread)
    positions, trades = generate_signals(z)
    bt = backtest(positions, spread, dev, gamma)
    pnl, equity = bt['pnl'], bt['equity']
    active = pnl[pnl != 0]
    tpnl = trade_pnls(spread, trades)

    oos_r = walk_forward(holdout, mode='rolling')
    oos_e = walk_forward(holdout, mode='expanding')

    print(f"\n{'=' * 52}")
    print(f"  {pair[0]}/{pair[1]}  -- validation")
    print('=' * 52)
    print(f"  dev     {dev.index[0].date()} to {dev.index[-1].date()}  ({len(dev)} bars)")
    print(f"  holdout {holdout.index[0].date()} to {holdout.index[-1].date()}  ({len(holdout)} bars)")

    print("\n[ cointegration (dev) ]")
    print(f"  gamma {gamma:.3f}   alpha {alpha:.2f}")
    print(f"  eg_pval {res['eg_pval']:.4f}   adf_pval {res['dkf_pval']:.4f}")
    print(f"  half_life {res['half_life']:.1f} days")

    print("\n[ dev trades ]")
    blotter = trades.copy()
    blotter['pnl'] = tpnl.values * UNIT_SIZE
    blotter['mae'] = mae(spread, trades).values * UNIT_SIZE
    print(blotter.to_string(index=False))

    print("\n[ dev (in-sample) -- daily series ]")
    print(f"  gross pnl       {bt['gross_pnl']:.0f}")
    print(f"  costs           {bt['costs']:.0f}")
    print(f"  net pnl         {bt['total_pnl']:.0f}")
    print(f"  sharpe          {sharpe(pnl):.2f}")
    print(f"  sortino         {sortino(pnl):.2f}")
    print(f"  s_ratio         {s_ratio(pnl):.2f}")
    print(f"  volatility      {volatility(pnl):.0f}")
    print(f"  semi_dev        {semi_deviation(pnl):.2f}")
    print(f"  var_95          {var_95(pnl):.2f}")
    print(f"  cvar_95         {cvar_95(pnl):.2f}")
    print(f"  max_drawdown    {max_drawdown(equity):.0f}")
    print(f"  dd_duration     {drawdown_duration(equity)} days")
    print(f"  best/worst day  {max_return(pnl):.0f} / {min_return(pnl):.0f}")

    print("\n[ dev (in-sample) -- active-return shape ]")
    print(f"  skew            {skew(active):.2f}")
    print(f"  excess_kurt     {excess_kurtosis(active):.2f}")
    print(f"  win_rate        {win_rate(tpnl):.2f}   trades {len(trades)}")

    print("\n[ holdout (out-of-sample, walk-forward) ]")
    for name, o in [('rolling', oos_r), ('expanding', oos_e)]:
        p = o['pnl']
        print(f"  {name:9} total {p.sum():.0f}   sharpe {sharpe(p):.2f}   maxDD {max_drawdown(p.cumsum()):.0f}"
              f"   windows {o['n_traded']}/{o['n_windows']}   trades {len(o['trades'])}")


table = screen_universe(CANDIDATE_PAIRS)
print(table.to_string())

for prospect in PROSPECTS:
    validate(prospect)
