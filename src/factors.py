import pandas as pd


def calculate_momentum(prices: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """
    Calculate momentum as percentage change over a lookback window.
    """
    return prices.pct_change(lookback)


def select_top_n(signal: pd.Series, n: int = 5) -> pd.Index:
    """
    Select top n stocks based on a factor signal.
    """
    return (
        signal
        .dropna()
        .sort_values(ascending=False)
        .head(n)
        .index
    )