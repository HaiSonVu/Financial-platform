# Phase 3 evaluation notes

See `notebooks/09_phase3_evaluation.ipynb` for the executed analysis. Notebook 08 preserves the earlier exploratory results and is superseded.

The generalized runner selects at month end using data through the last available close, assumes trading at that same close, then holds positions until the next month end without daily rebalancing. Same-close execution is optimistic. A fee in basis points is charged per dollar bought and sold, including the initial purchase. Trades and fees are measured against pre-trade wealth; a self-financing calculation targets weights after costs. The `turnover` field is half gross traded value; initial purchases should be read using `buys` and `gross_traded_value`, not turnover alone. Fee-bearing trades vary slightly with the fee because the target portfolio is funded after paying fees.

Metrics assume monthly returns: CAGR uses the number of monthly periods and drawdown includes starting wealth. Sharpe assumes a zero risk-free rate. These changes and buy-and-hold accounting mean results differ from the Phase 1–2 saved outputs; those remain historical records. The legacy specialized backtest functions retain their original behavior and should not be used for the corrected comparisons.

The notebook compares momentum against SPY on common dates, shows rolling 12-month return, volatility and maximum drawdown, and compares equal with inverse-volatility weighting. SPY is downloaded on execution and can change with data-provider revisions. The fixed present-day stock universe introduces survivorship bias; P/E is excluded from historical evaluation because current snapshots leak future information. Weighting comparisons are in-sample and do not establish future performance.

For Phase 4 the notebook creates past-only momentum and volatility features and next-month-return labels. Development ends at November 2021 and holdout starts in January 2022, leaving a one-month purge. The holdout is not used for tuning. Historical fundamentals must be dated by availability and historical universe membership must be addressed before broader conclusions.
