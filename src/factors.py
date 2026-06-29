import numpy as np
import pandas as pd
import yfinance as yf


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



def calculate_pe_ratio(tickers):
    """
    Download trailing P/E ratios for a list of tickers.
    """

    pe_ratios = {}

    for ticker in tickers:

        stock = yf.Ticker(ticker)

        info = stock.info

        pe_ratios[ticker] = info.get(
            "trailingPE",
            None
        )

    return pd.Series(pe_ratios)

def combine_factors(
    factors,
    weights=None
):
    """
    Combine multiple standardized factors.

    Parameters
    ----------
    factors : dict
        Dictionary of factor name -> z-score Series

    weights : dict
        Dictionary of factor name -> weight

    Returns
    -------
    pd.Series
        Combined factor score.
    """

    if weights is None:
        weights = {
            name: 1 / len(factors)
            for name in factors
        }

    combined = None

    for name, factor in factors.items():

        weighted_factor = weights[name] * factor

        if combined is None:
            combined = weighted_factor
        else:
            combined += weighted_factor

    return combined