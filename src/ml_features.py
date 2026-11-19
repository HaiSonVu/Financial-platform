"""Point-in-time stock-month features and next-month adjusted-price labels."""
import numpy as np
import pandas as pd

from src.data_loader import constituents_as_of

FEATURE_COLUMNS = ["momentum_6m", "momentum_12_1", "volatility_63d", "reversal_21d"]


def build_ml_dataset(prices, membership):
    """Build one row per historical member and month-end.

    Features and membership are known at the previous trading close; the
    target is the formation-close to next month-end adjusted-price return.
    Month-end labels use the last observed trading session, preserving missing
    prices rather than falling back to an earlier day. Missing inputs/targets
    remain NaN so the caller can inspect missingness before dropping rows.
    Price windows must be continuous. 12-1 momentum uses P[t-21]/P[t-252]-1
    at the signal close, where t is a trading-session index.
    """
    if not isinstance(prices.index, pd.DatetimeIndex) or prices.empty:
        raise ValueError("prices must have a nonempty DatetimeIndex")
    if not prices.index.is_monotonic_increasing or not prices.index.is_unique or not prices.columns.is_unique:
        raise ValueError("price dates and tickers must be unique and dates sorted")
    if (prices <= 0).any().any():
        raise ValueError("observed adjusted prices must be positive")
    # A monthly last row is a market session, not the last nonmissing stock price.
    month_close = prices.resample('ME').last(skipna=False)
    daily_return = prices.pct_change(fill_method=None)
    complete_253 = prices.notna().rolling(253, min_periods=253).sum().eq(253)
    complete_127 = prices.notna().rolling(127, min_periods=127).sum().eq(127)
    complete_22 = prices.notna().rolling(22, min_periods=22).sum().eq(22)
    daily_features = {
        'momentum_6m': prices.div(prices.shift(126)).sub(1).where(complete_127),
        'momentum_12_1': prices.shift(21).div(prices.shift(252)).sub(1).where(complete_253),
        'volatility_63d': daily_return.rolling(63, min_periods=63).std() * np.sqrt(252),
        'reversal_21d': -prices.div(prices.shift(21)).sub(1).where(complete_22),
    }
    # Shift by a trading session before sampling the formation-month last close.
    monthly_features = {key: value.shift(1).resample('ME').last(skipna=False)
                        for key, value in daily_features.items()}
    targets = month_close.shift(-1).div(month_close).sub(1)
    rows = []
    for date in month_close.index:
        formation_pos = prices.index.searchsorted(date, side='right') - 1
        if formation_pos < 1:
            continue
        signal_date = prices.index[formation_pos - 1]
        tickers = constituents_as_of(membership, signal_date)
        frame = pd.DataFrame(index=pd.Index(tickers, name='ticker'))
        for key in FEATURE_COLUMNS:
            frame[key] = monthly_features[key].loc[date].reindex(tickers).to_numpy()
        frame['next_month_return'] = targets.loc[date].reindex(tickers).to_numpy()
        frame['signal_date'] = signal_date
        frame['formation_date'] = date
        rows.append(frame.reset_index())
    if not rows:
        raise ValueError('No formation dates with an available prior close')
    return (pd.concat(rows, ignore_index=True)
            .replace([np.inf, -np.inf], np.nan)
            .set_index(['formation_date', 'ticker']).sort_index())
