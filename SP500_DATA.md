# S&P 500 research data

The current Phase 3–4 notebooks use `data/sp500_historical_2018_2024/`, containing historical membership snapshots and adjusted prices, including former constituents. The data is a subset of [Johnbrick123/sp500-data](https://github.com/Johnbrick123/sp500-data) (commit `25b21604fdd167824c32370070232971c0391de0`); it is a community reconstruction, not an official index dataset. `metadata.json` records release URLs and hashes for both downloaded files and extracted subsets. Price data covers 2018–2024; membership includes the last earlier snapshot and changes through 2024. Symbols, prices and effective dates may contain errors; corporate actions and delisting outcomes need independent verification.

```bash
venv/bin/python -m src.data_loader --start 2010-01-01 --end 2025-01-01 --output data/sp500_new_snapshot
```

The script avoids overwriting existing directories. Use dated membership and appropriate historical prices for backtesting.
