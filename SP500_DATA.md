# S&P 500 research data

The current Phase 3–4 notebooks use `data/sp500_historical_2018_2024/`, containing historical membership snapshots and adjusted prices, including former constituents. The data is a subset of [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data) (commit `25b21604fdd167824c32370070232971c0391de0`); it is a community reconstruction, not an official index dataset. `metadata.json` records release URLs and hashes for both downloaded files and extracted subsets. Price data covers 2018–2024; membership includes the last earlier snapshot and changes through 2024. Symbols, prices and effective dates may contain errors; corporate actions and delisting outcomes need independent verification.

Notebook 09 scores historical members using the previous trading close and assumes trading at the following formation close; notebook 10 builds historical-membership stock-month features (6-month momentum, 12–1 momentum, 63-day volatility, 21-day reversal) and next-month return labels. The available history and complete-observation requirements can exclude securities lacking usable histories. These limitations prevent a guarantee that all survivorship bias has been removed. Phase 3 results are in [README.md](README.md).

The old `data/sp500_2010_2024_snapshot/` was built from a current Wikipedia list. It is retained as a historical record and **must not be used as an unbiased historical S&P 500 universe**. Its 60.78% CAGR result is superseded. `src.data_loader` can still acquire a new current snapshot, but such a snapshot does not provide historical membership:

```bash
venv/bin/python -m src.data_loader --start 2010-01-01 --end 2025-01-01 --output data/sp500_new_snapshot
```

The script avoids overwriting existing directories. Use dated membership and appropriate historical prices for backtesting.

## Phase 4 extended data and Ridge baseline

`data/sp500_historical_2010_2024/` extends the same historical membership and adjusted price source for model training. The extract records hashes and preserves the Phase 3 dataset. Notebook 10 validates the panel and splits by formation month: training 2011–November 2018, validation January 2019–November 2021, and test January 2022–November 2024; December 2018 and December 2021 are excluded. The Ridge baseline fits its scaler and model on the training period and selects regularization using validation MSE. Its test MSE is 0.008685, compared with 0.008704 for the zero-return baseline and 0.008671 for the training-mean baseline. Mean monthly rank IC is -0.0387; the test-period top-five Ridge portfolio returned -29.89% CAGR after 10 bps per trade side versus 14.80% for a same-universe 12–1 momentum portfolio. The explicit DISCK-to-WBD conversion uses a one-for-one exchange; IC excludes the missing realized return spanning that conversion. These are concentrated, exploratory results rather than an untouched forward test. Missing outcomes, reconstructed membership, and previously inspected Phase 3 holdout years remain limitations.
