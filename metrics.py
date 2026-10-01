import numpy as np
import pandas as pd
import scipy.stats as ss
from config import TRADING_DAYS_PER_YEAR


def trade_pnls(spread, trades):
    entry = spread.loc[trades['entry_date']].values
    exit_ = spread.loc[trades['exit_date']].values
    return pd.Series(trades['direction'].values * (exit_ - entry), index=trades.index)


def mean_pnl(pnl):
    return pnl.mean()


def volatility(pnl, annualize=True):
    v = pnl.std()
    return v * np.sqrt(TRADING_DAYS_PER_YEAR) if annualize else v


def skew(pnl):
    return ss.skew(pnl)


def excess_kurtosis(pnl):
    return ss.kurtosis(pnl)


def max_return(pnl):
    return pnl.max()


def min_return(pnl):
    return pnl.min()


def semi_deviation(pnl, mar=0.0):
    downside = np.minimum(pnl - mar, 0)
    return np.sqrt((downside ** 2).mean())


def sharpe(pnl, rf=0.0):
    std = pnl.std()
    return np.sqrt(TRADING_DAYS_PER_YEAR) * (pnl.mean() - rf) / std if std > 0 else 0.0


def sortino(pnl, mar=0.0):
    return np.sqrt(TRADING_DAYS_PER_YEAR) * (pnl.mean() - mar) / semi_deviation(pnl, mar)


def s_ratio(pnl):
    up = pnl[pnl > 0].std()
    down = pnl[pnl < 0].std()
    return up / down


def var_95(pnl, level=0.05):
    return np.percentile(pnl, level * 100)


def cvar_95(pnl, level=0.05):
    return pnl[pnl <= var_95(pnl, level)].mean()


def win_rate(tpnl):
    return (tpnl > 0).mean()


def max_drawdown(equity):
    return (equity - equity.cummax()).min()


def drawdown_duration(equity):
    underwater = equity < equity.cummax()
    groups = (~underwater).cumsum()
    return underwater.groupby(groups).sum().max()


def mae(spread, trades):
    out = []
    for _, t in trades.iterrows():
        window = spread.loc[t['entry_date']:t['exit_date']]
        path = t['direction'] * (window - window.iloc[0])
        out.append(path.min())
    return pd.Series(out, index=trades.index)

