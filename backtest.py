import numpy as np
import pandas as pd
from config import TRADING_DAYS_PER_YEAR, COST_CONFIG, BORROW_DAY_COUNT, UNIT_SIZE

def backtest(positions, spread, df, gamma):
    gross = positions.shift(1) * spread.diff() * UNIT_SIZE
    costs = transaction_cost(positions, df, gamma).reindex(gross.index).fillna(0)
    pnl = (gross - costs).dropna()

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


def transaction_cost(position, df, gamma):
    indep, dep = df.columns[0], df.columns[1]
    px_indep, px_dep = df.iloc[:, 0], df.iloc[:, 1]
    cfg_i, cfg_d = COST_CONFIG[indep], COST_CONFIG[dep]

    shares_i, shares_d = gamma * UNIT_SIZE, UNIT_SIZE

    def leg_turn(cfg, shares):
        commission = max(cfg['commission_per_share'] * shares, cfg['min_commission'])
        return commission + cfg['half_spread'] * shares

    turn_cost = leg_turn(cfg_i, shares_i) + leg_turn(cfg_d, shares_d)
    turns = position.diff().abs().fillna(0) > 0
    per_turn = turns * turn_cost

    carry = pd.Series(0.0, index=position.index)
    long_spread = position == 1     # short the independent leg (indep)
    short_spread = position == -1   # short the dependent leg (dep)
    carry[long_spread] = cfg_i['borrow_rate_annual'] / BORROW_DAY_COUNT * shares_i * px_indep[long_spread]
    carry[short_spread] = cfg_d['borrow_rate_annual'] / BORROW_DAY_COUNT * shares_d * px_dep[short_spread]

    return per_turn + carry