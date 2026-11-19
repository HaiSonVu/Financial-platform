import numpy as np
import pandas as pd

from src.backtest import run_momentum_low_vol_backtest
from src.metrics import calculate_performance_metrics


def parameter_sensitivity_analysis(
    prices,
    backtest_function,
    factor_1_name,
    factor_2_name,
    factor_1_weight_name,
    factor_2_weight_name,
    weights=np.arange(0, 1.01, 0.1)
):
    """
    Evaluate different weight combinations between two factors.
    """

    results = []
    portfolios = {}

    for factor_1_weight in weights:

        factor_2_weight = 1 - factor_1_weight

        portfolio, _ = backtest_function(
            prices,
            **{
                factor_1_weight_name: factor_1_weight,
                factor_2_weight_name: factor_2_weight
            }
        )

        portfolios[factor_1_weight] = portfolio

        metrics = calculate_performance_metrics(portfolio)

        results.append({
            f"{factor_1_name} Weight": factor_1_weight,
            f"{factor_2_name} Weight": factor_2_weight,
            **metrics.to_dict()
        })

    results = pd.DataFrame(results)

    return results, portfolios

def monthly_rank_ic(predictions, realized_returns, min_stocks=3):
    """Spearman correlation across stocks per formation month.

    Inputs must be Series indexed by (formation_date, ticker). Missing pairs
    are excluded, and constant ranks or too few stocks produce NaN, not zero.
    """
    if min_stocks < 2:
        raise ValueError("min_stocks must be at least two")
    for series in (predictions, realized_returns):
        if not isinstance(series.index, pd.MultiIndex) or series.index.nlevels != 2 or not series.index.is_unique:
            raise ValueError("Inputs need a unique (formation_date, ticker) index")
    paired = pd.concat([predictions.rename('prediction'), realized_returns.rename('realized')], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
    rows = []
    for date, group in paired.groupby(level=0, sort=True):
        n = len(group)
        ic = (group['prediction'].rank().corr(group['realized'].rank())
              if n >= min_stocks and group['prediction'].nunique() > 1
              and group['realized'].nunique() > 1 else np.nan)
        rows.append({'formation_date': date, 'rank_ic': ic, 'n_stocks': n})
    return pd.DataFrame(rows, columns=['formation_date', 'rank_ic', 'n_stocks']).set_index('formation_date')


def predict_month_scores(model, panel, formation_date, signal_date, feature_columns):
    """Predict for feature-complete candidates without looking at their targets."""
    try:
        month = panel.xs(pd.Timestamp(formation_date), level='formation_date')
    except KeyError:
        raise ValueError(f"No feature rows for {formation_date}") from None
    if not month.index.is_unique:
        raise ValueError('Duplicate ticker rows at formation')
    usable = month.loc[month[feature_columns].notna().all(axis=1)].copy()
    if usable.empty:
        raise ValueError(f"No eligible stocks at {formation_date}")
    if not (usable['signal_date'] <= pd.Timestamp(signal_date)).all():
        raise ValueError(f"Features from after the signal date at {formation_date}")
    if not np.isfinite(usable[feature_columns].to_numpy()).all():
        raise ValueError('Non-finite feature values')
    return pd.Series(model.predict(usable[feature_columns]), index=usable.index, name='predicted_return')
