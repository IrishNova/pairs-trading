import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller


def screen_pair(df):
    x = df.iloc[:, 0]   # independent
    y = df.iloc[:, 1]   # dependent

    X = sm.add_constant(x)
    model = sm.OLS(y, X).fit()

    alpha = model.params.iloc[0]
    gamma = model.params.iloc[1]
    spread = model.resid

    eg_pval = coint(y, x)[1]
    dkf_pval = adfuller(spread, result_object=False)[1]

    spread_lag = spread.shift(1)
    delta = spread - spread_lag

    spread_lag = spread_lag.iloc[1:]
    delta = delta.iloc[1:]

    ou_X = sm.add_constant(spread_lag)
    ou_model = sm.OLS(delta, ou_X).fit()
    beta = ou_model.params.iloc[1]

    half_life = -np.log(2) / beta if beta < 0 else np.nan

    return {
        'independent': x.name,
        'dependent': y.name,
        'gamma': gamma,
        'alpha': alpha,
        'eg_pval': eg_pval,
        'dkf_pval': dkf_pval,
        'half_life': half_life,
    }

