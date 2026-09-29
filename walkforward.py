import pandas as pd
from screening import screen_pair
from spread import construct_spread
from signals import generate_signals
from backtest import backtest


def walk_forward(df, mode='rolling', train_len=504, test_len=126, gate=0.05):
    oos_pnl = []
    test_start = train_len
    while test_start + test_len <= len(df):
        train_start = 0 if mode == 'expanding' else test_start - train_len
        train = df.iloc[train_start:test_start]
        test = df.iloc[test_start:test_start + test_len]

        res = screen_pair(train)
        if res['eg_pval'] >= gate:
            oos_pnl.append(pd.Series(0.0, index=test.index))
            test_start += test_len
            continue

        gamma, alpha = res['gamma'], res['alpha']
        spread_train = construct_spread(train, gamma, alpha)
        mu, sd = spread_train.mean(), spread_train.std()

        spread_test = construct_spread(test, gamma, alpha)
        z_test = (spread_test - mu) / sd

        positions, trades = generate_signals(z_test)
        bt = backtest(positions, spread_test, test, gamma)
        oos_pnl.append(bt['pnl'])

        test_start += test_len

    return pd.concat(oos_pnl)
