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
    prices, score_function, top_n=5, strategy_name="Factor Strategy",
    transaction_cost_bps=0, weighting="equal", volatility_window=252,
    volatility_lag=0, corporate_actions=None,
):
    """Monthly buy-and-hold, trading at the close used to calculate the signal.

    The rate is charged on each dollar bought or sold, including initial buys.
    Trades and costs are fractions of pre-trade wealth; target weights describe
    post-cost wealth. Calendar month-end labels use the last available close.
    Missing selected prices are errors rather than silently assumed flat.
    """
    if not prices.index.is_monotonic_increasing or not prices.index.is_unique:
        raise ValueError("Prices must have a sorted, unique date index")
    if not 0 <= transaction_cost_bps < 10000 or top_n < 1:
        raise ValueError("top_n must be positive and transaction_cost_bps in [0, 10000)")
    if not isinstance(volatility_lag, int) or volatility_lag < 0:
        raise ValueError("volatility_lag must be a nonnegative integer")
    if weighting not in ("equal", "inverse_volatility"):
        raise ValueError("weighting must be equal or inverse_volatility")
    actions = []
    for action in corporate_actions or []:
        event = dict(action)
        event['date'] = pd.Timestamp(event['date'])
        if (event['old'] not in prices.columns or event['new'] not in prices.columns
                or event['old'] == event['new'] or event.get('ratio', 1) <= 0):
            raise ValueError("Invalid corporate-action ticker or conversion ratio")
        actions.append(event)
    returns = prices.pct_change(fill_method=None)
    month_ends = prices.resample("ME").last().index
    records, holdings_records, portfolio_returns, dates = [], [], [], []
    previous = pd.Series(0.0, index=prices.columns)
    for i in range(12, len(month_ends) - 1):
        formation_date, next_date = month_ends[i:i+2]
        current_prices = prices.loc[:formation_date]
        current_returns = returns.loc[:formation_date]
        scores = score_function(current_prices=current_prices,
                                current_returns=current_returns,
                                formation_date=formation_date)
        selected = select_top_n(scores, n=top_n)
        if len(selected) == 0:
            raise ValueError(f"No eligible stocks at {formation_date}")
        target = pd.Series(0.0, index=prices.columns)
        if weighting == "equal":
            target.loc[selected] = 1 / len(selected)
        else:
            volatility_returns = current_returns.iloc[:-volatility_lag] if volatility_lag else current_returns
            vol = volatility_returns.loc[:, selected].tail(volatility_window).std()
            if vol.isna().any() or (vol <= 0).any() or len(volatility_returns.tail(volatility_window)) < volatility_window:
                raise ValueError(f"Insufficient or zero volatility at {formation_date}")
            inverse = 1 / vol
            target.loc[selected] = inverse / inverse.sum()
        if current_prices.loc[:, selected].iloc[-1].isna().any():
            raise ValueError(f"Missing formation price at {formation_date}")
        # Solve self-financing equation: post-cost wealth + fee = pre-trade wealth.
        rate = transaction_cost_bps / 10000
        low, high = 0.0, 1.0
        for _ in range(60):
            mid = (low + high) / 2
            if mid + rate * (mid * target - previous).abs().sum() > 1:
                high = mid
            else:
                low = mid
        net_fraction = (low + high) / 2
        trades = net_fraction * target - previous
        buys, sells = trades.clip(lower=0).sum(), -trades.clip(upper=0).sum()
        cost = rate * (buys + sells)
        period = returns.loc[(returns.index > formation_date) & (returns.index <= next_date), selected].copy()
        conversions = []
        for event in actions:
            old_symbol, new_symbol = event['old'], event['new']
            event_date = event['date']
            if old_symbol not in selected or not (formation_date < event_date <= next_date):
                continue
            if event_date not in period.index:
                raise ValueError(f"Conversion date {event_date} is not a trading date")
            prior_pos = prices.index.get_loc(event_date) - 1
            if prior_pos < 0:
                raise ValueError("Conversion has no prior trading date")
            old_close = prices.iloc[prior_pos][old_symbol]
            new_close = prices.loc[event_date, new_symbol]
            if pd.isna(old_close) or pd.isna(new_close) or old_close <= 0 or new_close <= 0:
                raise ValueError(f"Missing conversion prices for {old_symbol} on {event_date}")
            # Explicit one-for-one (or documented ratio) share conversion; no trade.
            period.loc[event_date, old_symbol] = event.get('ratio', 1) * new_close / old_close - 1
            later = period.index > event_date
            period.loc[later, old_symbol] = returns.loc[period.index[later], new_symbol]
            conversions.append((old_symbol, new_symbol))
        if period.empty or period.isna().any().any():
            missing = period.columns[period.isna().any()].tolist()
            raise ValueError(f"Missing holding-period returns after {formation_date}: {missing}")
        growth = (1 + period).prod()
        gross_growth = (target.loc[selected] * growth).sum()
        if gross_growth <= 0:
            raise ValueError("Portfolio wealth must remain positive")
        previous = pd.Series(0.0, index=prices.columns)
        previous.loc[selected] = target.loc[selected] * growth / gross_growth
        for old_symbol, new_symbol in conversions:
            previous.loc[new_symbol] += previous.loc[old_symbol]
            previous.loc[old_symbol] = 0.0
        gross_return = gross_growth - 1
        net_return = net_fraction * gross_growth - 1
        holdings_records.append({"formation_date": formation_date, "holding_until": next_date,
                                 "holdings": list(selected), "target_weights": target[target > 0].to_dict(),
                                 "ending_weights": previous[previous > 0].to_dict()})
        records.append({"formation_date": formation_date, "holding_until": next_date,
                        "turnover": 0.5 * (buys + sells), "buys": buys, "sells": sells,
                        "gross_traded_value": buys + sells, "transaction_cost": cost,
                        "gross_return": gross_return, "net_return": net_return})
        portfolio_returns.append(net_return)
        dates.append(next_date)
    return (pd.Series(portfolio_returns, index=pd.DatetimeIndex(dates), name=strategy_name),
            pd.DataFrame(holdings_records), pd.DataFrame(records))


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


def create_equal_weights(selected_stocks, universe):
    """
    Create a portfolio-weight Series over the full stock universe.

    Selected stocks receive equal weights.
    Unselected stocks receive weight zero.
    """
    weights = pd.Series(0.0, index=universe)

    weights.loc[selected_stocks] = 1 / len(selected_stocks)

    return weights


def calculate_turnover(
    current_weights,
    previous_weights
):
    """
    Calculate one-way portfolio turnover.
    """
    return 0.5 * (
        current_weights - previous_weights
    ).abs().sum()



def point_in_time_momentum_score(current_prices, current_returns, formation_date,
                                 membership, lookback=252):
    """Rank members known at the prior close, for execution at formation close.

    Requires lookback+1 consecutive, observed prices per security. The latest
    close is deliberately excluded, so it cannot influence the closing trade.
    """
    from src.data_loader import constituents_as_of

    signal_prices = current_prices.iloc[:-1]
    if len(signal_prices) < lookback + 1:
        return pd.Series(dtype=float)
    signal_date = signal_prices.index[-1]
    members = constituents_as_of(membership, signal_date)
    eligible = signal_prices.tail(lookback + 1).notna().all()
    score = calculate_momentum(signal_prices, lookback).iloc[-1]
    score = zscore_factor(score.where(eligible & score.index.isin(members)))
    return score
