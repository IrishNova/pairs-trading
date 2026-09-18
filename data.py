import yfinance as yf
import pandas as pd


def fetch_raw_data(tickers):
    """
    Fetch split/dividend-adjusted daily closing prices for a single pair and
    align them onto a common date index.

    Downloads the maximum available history for each ticker from yfinance
    (auto-adjusted closes), then joins the two series on their shared trading
    dates. Rows where either ticker has no data are dropped, so the result
    covers only the window in which both tickers traded: the aligned series
    required for cointegration testing.

    :param tickers: Tuple of exactly two ticker symbols, e.g. ('AAPL', 'MSFT').
    :return: DataFrame indexed by date, with one adjusted-close column per
        ticker, restricted to their overlapping trading window.
    :raises ValueError: If ``tickers`` does not contain exactly two symbols.
    """

    if len(tickers) != 2:
        raise ValueError('Error: You need exactly two tickers')

    export = {}
    for t in tickers:
        export[t] = yf.download(tickers=t,
                                period='max',
                                multi_level_index=False,
                                auto_adjust=True)['Close']
    return pd.concat(export, axis=1).dropna()

