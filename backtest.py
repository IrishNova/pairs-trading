import numpy as np
from config import TRADING_DAYS_PER_YEAR

def backtest(positions, spread):
    pnl = positions.shift(1) * spread.diff()
    pnl = pnl.dropna()

    equity = pnl.cumsum()

    sharpe = np.sqrt(TRADING_DAYS_PER_YEAR) * pnl.mean() / pnl.std()
    mdd = (equity - equity.cummax()).min()

    return {
        'total_pnl': equity.iloc[-1],
        'sharpe': sharpe,
        'max_drawdown': mdd,
        'equity': equity,
        'pnl': pnl,
    }
