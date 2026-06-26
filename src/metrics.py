import numpy as np
import pandas as pd


def calculate_growth(returns: pd.Series) -> pd.Series:
    """
    Convert returns into growth of $1.
    """
    return (1 + returns).cumprod()


def calculate_drawdown(growth: pd.Series) -> pd.Series:
    """
    Calculate drawdown from previous peak.
    """
    running_max = growth.cummax()

    return (
        growth - running_max
    ) / running_max


def calculate_performance_metrics(
    returns: pd.Series
) -> pd.Series:
    """
    Calculate common investment performance metrics.
    Assumes monthly returns.
    """

    growth = calculate_growth(returns)

    annual_return = returns.mean() * 12

    annual_vol = returns.std() * np.sqrt(12)

    sharpe = annual_return / annual_vol

    years = (
        returns.index[-1] - returns.index[0]
    ).days / 365.25

    cagr = growth.iloc[-1] ** (1 / years) - 1

    max_drawdown = calculate_drawdown(growth).min()

    return pd.Series({
        "CAGR": cagr,
        "Annual Return": annual_return,
        "Annual Volatility": annual_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_drawdown
    })