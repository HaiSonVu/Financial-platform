import numpy as np
import pandas as pd

from src.backtest import run_momentum_low_vol_backtest
from src.metrics import calculate_performance_metrics


def parameter_sensitivity_analysis(
    prices,
    weights=np.arange(0, 1.01, 0.1)
):
    """
    Evaluate different momentum/low-volatility weight combinations.
    """

    results = []
    portfolios = {}

    for momentum_weight in weights:

        low_vol_weight = 1 - momentum_weight

        portfolio, _ = run_momentum_low_vol_backtest(
            prices,
            momentum_weight=momentum_weight,
            low_vol_weight=low_vol_weight
        )

        portfolios[momentum_weight] = portfolio

        metrics = calculate_performance_metrics(portfolio)

        results.append({
            "Momentum Weight": momentum_weight,
            "Low Vol Weight": low_vol_weight,
            **metrics.to_dict()
        })

    results = pd.DataFrame(results)

    return results, portfolios