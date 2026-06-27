import numpy as np
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


def calculate_volatility(
    returns: pd.DataFrame,
    window: int = 252
):
    """
    Calculate rolling annual volatility.
    """
    return returns.rolling(window).std() 


def zscore_factor(signal: pd.Series) -> pd.Series:
    """
    Standardize a factor signal into z-scores.

    Higher z-score = better, assuming the factor is already oriented correctly.
    """
    return (signal - signal.mean()) / signal.std()
