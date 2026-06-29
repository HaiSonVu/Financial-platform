import numpy as np
import pandas as pd

from src.factors import calculate_momentum, select_top_n


def run_momentum_backtest(
    prices: pd.DataFrame,
    lookback: int = 252,
    top_n: int = 5
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Run a monthly rebalanced momentum strategy.

    Steps:
    1. At each month end, calculate momentum using only past data.
    2. Select top_n stocks.
    3. Equal weight them.
    4. Hold until next month end.
    5. Store monthly portfolio return and holdings.
    """

    returns = prices.pct_change()
    month_ends = prices.resample("ME").last().index

    portfolio_returns = []
    portfolio_dates = []
    holdings_records = []

    for i in range(12, len(month_ends) - 1):
        formation_date = month_ends[i]
        next_date = month_ends[i + 1]

        current_prices = prices.loc[:formation_date]

        momentum = calculate_momentum(
            current_prices,
            lookback=lookback
        )

        latest_momentum = momentum.iloc[-1]

        selected_stocks = select_top_n(
            latest_momentum,
            n=top_n
        )

        holdings_records.append({
            "formation_date": formation_date,
            "holding_until": next_date,
            "holdings": list(selected_stocks)
        })

        weights = np.repeat(
            1 / len(selected_stocks),
            len(selected_stocks)
        )

        holding_period = returns.loc[
            formation_date:next_date,
            selected_stocks
        ]

        daily_portfolio_return = (
            holding_period * weights
        ).sum(axis=1)

        monthly_return = (
            1 + daily_portfolio_return
        ).prod() - 1

        portfolio_returns.append(monthly_return)
        portfolio_dates.append(next_date)

    portfolio = pd.Series(
        portfolio_returns,
        index=portfolio_dates,
        name="Momentum Strategy"
    )

    holdings_history = pd.DataFrame(holdings_records)

    return portfolio, holdings_history

from src.factors import (


    calculate_volatility,

    zscore_factor,

    select_top_n

)

def run_momentum_low_vol_backtest(

    prices,

    lookback=252,

    vol_window=252,

    top_n=5,

    momentum_weight=0.5,

    low_vol_weight=0.5

):

    returns = prices.pct_change()

    month_ends = prices.resample("ME").last().index

    portfolio_returns = []

    portfolio_dates = []

    holdings_records = []

    for i in range(12, len(month_ends) - 1):

        formation_date = month_ends[i]

        next_date = month_ends[i + 1]

        current_prices = prices.loc[:formation_date]

        current_returns = returns.loc[:formation_date]

        momentum = calculate_momentum(current_prices, lookback)

        volatility = calculate_volatility(current_returns, vol_window)

        latest_momentum = momentum.iloc[-1]

        latest_vol = volatility.iloc[-1]

        momentum_z = zscore_factor(latest_momentum)

        low_vol_z = zscore_factor(-latest_vol)

        combined_score = (

            momentum_weight * momentum_z

            + low_vol_weight * low_vol_z

        )

        selected_stocks = select_top_n(combined_score, n=top_n)

        holdings_records.append({

            "formation_date": formation_date,

            "holding_until": next_date,

            "holdings": list(selected_stocks)

        })

        weights = np.repeat(1 / len(selected_stocks), len(selected_stocks))

        holding_period = returns.loc[
            returns.index[(returns.index > formation_date) & (returns.index <= next_date)],
            selected_stocks
        ]

        daily_portfolio_return = (holding_period * weights).sum(axis=1)

        monthly_return = (1 + daily_portfolio_return).prod() - 1

        portfolio_returns.append(monthly_return)

        portfolio_dates.append(next_date)

    portfolio = pd.Series(

        portfolio_returns,

        index=portfolio_dates,

        name="Momentum + Low Vol"

    )

    holdings_history = pd.DataFrame(holdings_records)

    return portfolio, holdings_history


def run_factor_backtest(
    prices,
    score_function,
    top_n=5,
    strategy_name="Factor Strategy"
):
    returns = prices.pct_change()
    month_ends = prices.resample("ME").last().index

    portfolio_returns = []
    portfolio_dates = []
    holdings_records = []

    for i in range(12, len(month_ends) - 1):
        formation_date = month_ends[i]
        next_date = month_ends[i + 1]

        current_prices = prices.loc[:formation_date]
        current_returns = returns.loc[:formation_date]

        scores = score_function(
            current_prices=current_prices,
            current_returns=current_returns,
            formation_date=formation_date
        )

        selected_stocks = select_top_n(
            scores,
            n=top_n
        )

        holdings_records.append({
            "formation_date": formation_date,
            "holding_until": next_date,
            "holdings": list(selected_stocks)
        })

        weights = np.repeat(
            1 / len(selected_stocks),
            len(selected_stocks)
        )

        holding_period = returns.loc[
            returns.index[
                (returns.index > formation_date)
                & (returns.index <= next_date)
            ],
            selected_stocks
        ]

        daily_portfolio_return = (
            holding_period * weights
        ).sum(axis=1)

        monthly_return = (
            1 + daily_portfolio_return
        ).prod() - 1

        portfolio_returns.append(monthly_return)
        portfolio_dates.append(next_date)

    portfolio = pd.Series(
        portfolio_returns,
        index=portfolio_dates,
        name=strategy_name
    )

    holdings_history = pd.DataFrame(holdings_records)

    return portfolio, holdings_history


def momentum_score(
    current_prices,
    current_returns,
    formation_date,
    lookback=252
):
    momentum = calculate_momentum(
        current_prices,
        lookback
    )

    latest_momentum = momentum.iloc[-1]

    return zscore_factor(latest_momentum)


def momentum_low_vol_score(
    current_prices,
    current_returns,
    formation_date,
    momentum_weight=0.5,
    low_vol_weight=0.5,
    lookback=252,
    vol_window=252
):
    momentum = calculate_momentum(
        current_prices,
        lookback
    )

    volatility = calculate_volatility(
        current_returns,
        vol_window
    )

    latest_momentum = momentum.iloc[-1]
    latest_vol = volatility.iloc[-1]

    momentum_z = zscore_factor(latest_momentum)
    low_vol_z = zscore_factor(-latest_vol)

    scores = (
        momentum_weight * momentum_z
        + low_vol_weight * low_vol_z
    )

    return scores


def momentum_value_score(
    current_prices,
    current_returns,
    formation_date,
    value_z,
    momentum_weight=0.5,
    value_weight=0.5,
    lookback=252
):
    momentum = calculate_momentum(
        current_prices,
        lookback
    )

    latest_momentum = momentum.iloc[-1]

    momentum_z = zscore_factor(latest_momentum)

    scores = (
        momentum_weight * momentum_z
        + value_weight * value_z
    )

    return scores.dropna()
