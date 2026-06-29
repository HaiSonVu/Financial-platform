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