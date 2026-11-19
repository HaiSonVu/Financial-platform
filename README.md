# Multi-Factor Equity Strategy Backtester

An educational Python project for researching factor strategies, realistic portfolio backtests, and eventually machine-learning stock models. Historical results are exploratory, not financial advice.

## Project and data

- `src/` contains data loading, factor scores, backtesting, metrics, experiments, and visualization.
- `notebooks/01`–`07` contain the original Phase 1–2 work. `08` is the superseded cost experiment, `09` is the corrected Phase 3 evaluation, and `10` explores the larger Phase 4 dataset.
- `data/prices.csv` preserves the original 30-stock research. `data/sp500_historical_2018_2024/` contains the historical membership and prices for Phase 3; `data/sp500_historical_2010_2024/` extends the same source for Phase 4; the current-constituent snapshot is retained as a biased historical record. See [SP500_DATA.md](SP500_DATA.md).
- `tests/` contains checks for accounting, metrics, and dataset loading.

Run from the project root with the project Python environment:

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m unittest discover -s tests -v
venv/bin/jupyter lab
```

## Phase 1 — Momentum

The initial study ranked a selected 30-stock universe by 252-trading-day momentum and held the top five. Its saved historical results reported a 23.05% CAGR for momentum versus 16.06% for SPY. The original work also found that performance weakened when NVDA was removed. These are research records using the earlier backtest and metric conventions, and should not be directly compared with the corrected results below.

## Phase 2 — Multi-factor research

The original experiments added low volatility and a value score. The momentum/low-volatility combination had lower drawdown but lower returns in that sample. In the value weight sweep, 60% momentum / 40% value recorded a 25.72% CAGR and 1.21 Sharpe ratio, the best tested combination by those measures.

**The value result is exploratory and look-ahead biased:** one current P/E snapshot was applied to historical dates. The weights were also selected and evaluated on the same data. A valid historical test needs fundamentals dated by when they became available and a separate evaluation period.

## Phase 3 — Portfolio evaluation

Notebook 09 uses reconstructed historical S&P 500 membership and adjusted prices over 2018–2024. At each rebalance, momentum and inverse-volatility sizing use data through the previous trading close, and the portfolio is assumed to trade at the formation close. Membership is selected as of the same prior close. The backtest requires 253 consecutive observed prices for momentum and fails if a selected position lacks a holding-period return. Positions drift between rebalances.

Fees apply to each dollar bought and sold, including the initial purchase. Trades and costs use pre-trade wealth, and target weights apply after costs. CAGR uses the number of monthly periods, drawdown includes initial wealth, and Sharpe assumes a zero risk-free rate. Legacy specialized runners and earlier notebook outputs retain old conventions.

### Exploratory historical-membership results

The evaluation covers 71 monthly periods from February 2019 through December 2024. Membership is reconstructed by a third party and prices combine multiple sources; see [SP500_DATA.md](SP500_DATA.md). Results remain in-sample and are not evidence of future performance.

| Strategy | Cost per trade side | CAGR | Sharpe | Max drawdown |
|---|---:|---:|---:|---:|
| Equal-weight momentum | 0 bps | 22.10% | 0.79 | -26.51% |
| Equal-weight momentum | 10 bps | 20.99% | 0.76 | -26.81% |
| Inverse-volatility momentum | 10 bps | 17.76% | 0.68 | -29.68% |
| SPY | Not modeled | 15.83% | 0.94 | -23.93% |

The experiment moves signals to the prior close and changes price data sources; the change in return cannot be attributed to membership alone. The strategy holds five stocks, unlike diversified SPY; trading costs are not applied to the benchmark. Same-close market-on-close execution remains an assumption and slippage, taxes, market impact and delisting proceeds are not fully modeled.

Notebook 09 plots rolling 12-month results and prepares past-only momentum and volatility features with next-month labels. Development ends November 2021, December is purged, and the model holdout starts January 2022. Phase 3 outcomes in these years have been inspected, so a later evaluation period would provide a more independent final study.

## Phase 4 — Predictive machine learning

Notebook 10 uses historical membership and prices to build four past-only features (6-month momentum, 12–1 momentum, 63-day volatility, and 21-day reversal) and next-month return labels. It checks the panel and uses 2011–November 2018 for training, January 2019–November 2021 for validation, and January 2022–November 2024 for test; December 2018 and December 2021 are purged. The scaler and final Ridge model are fit on training data only; the penalty is selected by validation MSE (alpha 0.1).

The test-period mean monthly Spearman rank IC was **-0.0387** across 35 months, with 40% of months positive. Test Ridge MSE was 0.008685 compared with 0.008704 for zero-return predictions and 0.008671 for the training-mean baseline. IC excludes missing realized returns, including a Discovery Series C outcome spanning its conversion.

A five-stock test-period backtest at 10 bps per trade side returned **-29.89% CAGR** for the Ridge ranking versus **14.80% CAGR** for a 12–1 momentum ranking, using the same historically eligible, feature-complete stock universe. These are concentrated portfolios: maximum drawdowns were -72.30% and -26.63%, respectively. Discovery Series C (DISCK) is converted one-for-one into WBD on 2022-04-11 with no trading fee, based on the [SEC filing](https://www.sec.gov/Archives/edgar/data/1437107/000119312522103051/d328161d8k.htm). Other unresolved missing prices stop the run. Exact formation-close execution and adjusted-price consistency across the conversion are assumptions. The 35-month results are exploratory, the test years were inspected during earlier Phase 3 research, and missing outcomes, data-source errors, and unmodeled corporate actions can bias the comparison. Next assess stability and alternative models with time-aware validation and a later independent period where possible.

## Phase 5 — Statistical validation

Compare ML models with simple factor baselines using time-series cross-validation, bootstrap confidence intervals, appropriate hypothesis tests, model stability analysis, and checks for overfitting. Respect dependence across stocks and over time.

## Phase 6 — Interactive ML investing platform

Build a Streamlit application for comparing factor strategies and ML models, with interactive plots, experiment tracking, and reproducible data pipelines. Clearly show assumptions and limitations.

## Limitations

- Historical index membership is reconstructed from third-party data and may contain errors; incomplete delisted prices, identifier reuse, and missing outcomes can still introduce bias.
- A stock's missing history may reflect listing dates, ticker changes, or download failures. Adjusted prices and SPY downloads may be revised.
- Execution at the formation close is assumed after using the previous close for signals; fees do not model slippage, market impact, taxes, financing, or all delisting outcomes.
- The historical value signal uses a current P/E snapshot and cannot support a valid historical result. Historical fundamentals require availability dates.
- Earlier parameter tuning and Phase 3 comparisons are in-sample; they do not establish future performance. The legacy specialized runners use older accounting conventions.
