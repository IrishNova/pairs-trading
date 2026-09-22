import yfinance as yf
import pandas as pd


def order_pair(data):
    """
    Decide which leg of a pair is the independent variable and which is the base.

    Uses average dollar volume (Close * Volume, meaned over the full aligned
    history) as a liquidity proxy. The more liquid leg is treated as the
    independent variable in the cointegration regression, on the reasoning that
    the deeper, more efficiently priced name is the better explanatory series and
    the thinner name carries the tradeable deviation.

    :param data: DataFrame with a column MultiIndex whose level 0 is the ticker
        and level 1 contains at least ``'Close'`` and ``'Volume'``, as produced
        by concatenating two single-ticker yfinance frames.
    :return: Tuple ``(independent, dependent)`` of ticker symbols, ordered by
        descending average dollar volume.
    :raises ValueError: If fewer than 252 aligned bars are available (roughly one
        trading year), too little history to test cointegration reliably.
    """

    if len(data) < 252:
        raise ValueError('Not enough data, one or both of the tickers has less than 252 bars')

    # measure price * volume -> average dollar volume per ticker
    close = data.xs('Close', axis=1, level=1)
    volume = data.xs('Volume', axis=1, level=1)
    avg_dollar_vol = (close * volume).mean()

    # more liquid leg is the independent variable, thinner leg is the base
    independent = avg_dollar_vol.idxmax()
    dependent = avg_dollar_vol.idxmin()

    return independent, dependent


def fetch_raw_data(tickers):
    """
    Fetch split/dividend-adjusted daily closing prices for a single pair, align
    them onto a common date index, and order the columns by liquidity.

    Downloads the maximum available history for each ticker from yfinance
    (auto-adjusted closes plus volume), then joins the two series on their shared
    trading dates. Rows where either ticker has no data are dropped, so the result
    covers only the window in which both tickers traded: the aligned series
    required for cointegration testing. Volume is used solely to decide the
    independent/dependent ordering (see :func:`order_pair`) and is dropped from
    the returned frame.

    :param tickers: Tuple of exactly two ticker symbols, e.g. ('AAPL', 'MSFT').
    :return: DataFrame indexed by date with two adjusted-close columns, ordered
        ``[independent, dependent]`` (more liquid leg first), restricted to the
        pair's overlapping trading window.
    :raises ValueError: If ``tickers`` does not contain exactly two symbols, or
        if the aligned history is shorter than 252 bars (raised by
        :func:`order_pair`).
    """

    if len(tickers) != 2:
        raise ValueError('Error: You need exactly two tickers')



    export = {}
    for t in tickers:
        export[t] = yf.download(tickers=t,
                                period='max',
                                multi_level_index=False,
                                auto_adjust=True)[['Close', 'Volume']]

    df = pd.concat(export, axis=1).dropna()

    independent, dependent = order_pair(df)
    df = df.xs('Close', axis=1, level=1)[[independent, dependent]]

    return df

# print(fetch_raw_data(('AAPL', 'MSFT')))

