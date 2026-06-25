import pandas as pd


def calculate_momentum(prices: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """
    Calculate trailing momentum as percentage change over a lookback window.

    Parameters
    ----------
    prices : pd.DataFrame
        Adjusted close prices, indexed by date.
    lookback : int
        Number of trading days used to calculate momentum.

    Returns
    -------
    pd.DataFrame
        Momentum scores for each asset.
    """
    return prices.pct_change(lookback)