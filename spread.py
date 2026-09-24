
def construct_spread(df, gamma, alpha):
    x = df.iloc[:, 0]
    y = df.iloc[:, 1]
    spread = y - gamma * x - alpha
    return spread


def zscore(spread, window=None):
    if window is None:
        return (spread - spread.mean()) / spread.std()

    rolling_mean = spread.rolling(window).mean()
    rolling_std = spread.rolling(window).std()
    return (spread - rolling_mean) / rolling_std