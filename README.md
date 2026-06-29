# Multi-Factor Equity Strategy Backtester

A Python-based quantitative finance project that builds and evaluates factor-based equity strategies using historical stock price data.

The project starts with a simple momentum strategy, then expands into a multi-factor framework using momentum, low volatility, and value signals. The goal is to test whether factor-based stock selection can outperform SPY on a risk-adjusted basis.

---

## Project Overview

This project follows a full quantitative research workflow:

- Download historical stock price data
- Build factor signals
- Rank stocks cross-sectionally
- Construct monthly rebalanced portfolios
- Backtest strategies against SPY
- Evaluate return and risk metrics
- Run robustness checks and parameter tuning
- Refactor reusable logic into Python modules

---

## Repository Structure

- `data/` — saved price data, factor tables, holdings history, and performance results
- `notebooks/` — research notebooks from data download to factor testing
- `src/` — reusable Python modules for factors, backtesting, metrics, experiments, and visualization
- `requirements.txt` — project dependencies

---

## Phase 1: Momentum Strategy

### Objective

Phase 1 tested whether a simple 12-month momentum strategy could outperform SPY.

Momentum is based on the idea that stocks with strong recent performance may continue to outperform in the near term.

### Method

The strategy calculated 252-trading-day momentum, ranked stocks by momentum score, selected the top-ranked stocks, and rebalanced monthly.

### Results

| Strategy | CAGR | Annual Volatility | Sharpe Ratio | Max Drawdown |
|---|---:|---:|---:|---:|
| Momentum Strategy | 23.05% | 19.84% | 1.14 | -17.75% |
| SPY | 16.06% | 17.30% | 0.94 | -23.93% |

### Interpretation

The momentum strategy outperformed SPY across return, Sharpe ratio, and max drawdown.

However, a robustness check showed that performance was heavily influenced by NVDA. After removing NVDA, the strategy’s outperformance became weaker. This showed that strong backtest results can depend heavily on a small number of winners.

---

## Phase 2: Multi-Factor Strategy Expansion

### Objective

Phase 2 expanded the project from a single-factor momentum strategy into a multi-factor framework.

The goal was to test whether adding low-volatility and value factors could improve the original momentum strategy.

---

## Phase 2A: Momentum + Low Volatility

### Objective

This experiment tested whether adding a low-volatility factor could reduce drawdowns and improve risk-adjusted performance.

### Results

| Strategy | CAGR | Annual Volatility | Sharpe Ratio | Max Drawdown |
|---|---:|---:|---:|---:|
| Momentum | 23.05% | 19.84% | 1.14 | -17.75% |
| Momentum + Low Volatility | 13.94% | 18.09% | 0.80 | -13.49% |
| SPY | 16.06% | 17.30% | 0.94 | -23.93% |

### Interpretation

Adding low volatility reduced max drawdown from -17.75% to -13.49%, showing better downside protection.

However, the combined strategy had lower CAGR and a lower Sharpe ratio than pure momentum. This suggests that low volatility acted as a defensive overlay, but did not improve overall performance in this universe.

---

## Phase 2B: Momentum / Low-Volatility Tuning

This experiment tested different momentum and low-volatility weights.

The results showed that higher momentum weights generally produced stronger returns and Sharpe ratios. Low volatility helped reduce risk, but too much low-volatility exposure weakened upside performance.

The main conclusion was that pure momentum remained stronger than the momentum/low-volatility combinations.

---

## Phase 2C: Momentum + Value

### Objective

This experiment added a value factor using P/E ratio.

The goal was to test whether cheaper stocks, based on valuation, could improve the original momentum strategy.

### Results

| Strategy | CAGR | Sharpe Ratio | Max Drawdown |
|---|---:|---:|---:|
| Momentum | 23.05% | 1.14 | -17.75% |
| Momentum + Low Volatility | 13.94% | 0.80 | -13.49% |
| Momentum + Value | 22.29% | 1.08 | -23.48% |
| SPY | 16.06% | 0.94 | -23.93% |

### Interpretation

The momentum + value strategy performed better than the momentum + low-volatility strategy and outperformed SPY.

However, it slightly underperformed pure momentum in CAGR and Sharpe ratio. This suggests that value was a more promising complement to momentum than low volatility, but the 50/50 combination was not the best weighting.

---

## Phase 2D: Momentum / Value Tuning

This experiment tested different momentum and value weights.

The best tested combination was:

| Strategy | CAGR | Annual Volatility | Sharpe Ratio | Max Drawdown |
|---|---:|---:|---:|---:|
| 60% Momentum / 40% Value | 25.72% | 20.53% | 1.21 | -19.84% |

This was the strongest Phase 2 result by both CAGR and Sharpe ratio.

### Interpretation

The results suggest that value can improve the momentum strategy when used as a moderate overlay.

Pure momentum remained strong, but the 60% momentum / 40% value strategy produced better return and risk-adjusted performance than pure momentum in this backtest.

---

## Final Phase 2 Summary

Phase 2 showed that adding more factors does not automatically improve a strategy.

Key findings:

- Momentum strongly outperformed SPY.
- Low volatility reduced drawdown but lowered returns.
- Value was more useful than low volatility as a complement to momentum.
- The best tested strategy was 60% momentum and 40% value.
- The value factor result should be treated as exploratory because it currently uses a static P/E snapshot rather than point-in-time historical fundamentals.

---

## Skills Demonstrated

- Python programming
- pandas and NumPy
- Quantitative finance research
- Factor investing
- Momentum strategy design
- Low-volatility strategy design
- Value factor construction
- Portfolio backtesting
- Monthly rebalancing
- Performance evaluation
- Parameter tuning
- Robustness testing
- Data visualization
- Git/GitHub project organization
- Modular code refactoring

---

## Technologies Used

- Python
- pandas
- NumPy
- yfinance
- matplotlib
- Jupyter Notebook
- Git/GitHub

---

## Evaluation Metrics

The strategies are evaluated using:

- CAGR
- Annual return
- Annual volatility
- Sharpe ratio
- Max drawdown

---

## Limitations

- The stock universe is limited and may suffer from survivorship bias.
- Transaction costs and slippage are not yet included.
- The value factor uses a static P/E snapshot rather than point-in-time historical fundamentals.
- Parameter tuning was performed on the same historical period, so results may be overfit.
- SPY is used as the main benchmark, but the strategy universe is a selected group of large-cap stocks.

---

## Next Steps

- Add transaction costs and turnover analysis
- Use point-in-time historical fundamentals for the value factor
- Add out-of-sample or walk-forward validation
- Add sector exposure analysis
- Add risk controls such as max position weight and volatility targeting
- Save charts into a `reports/figures/` folder
- Build a Streamlit dashboard for interactive strategy comparison
- Add unit tests for core functions

---

## Project Status

Phase 1 and Phase 2 are complete.

Next phase: risk controls, validation, and dashboard development.

---

## Disclaimer

This project is for educational and research purposes only. It is not financial advice or a recommendation to buy or sell any security.