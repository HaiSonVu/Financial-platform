# Financial Platform

This project builds and evaluates a simple equity momentum strategy using historical stock price data.

## Phase 1: Momentum Backtest

- Downloaded adjusted stock prices using yfinance
- Built a 252-day momentum factor
- Selected top-ranked momentum stocks
- Backtested the strategy against SPY
- Evaluated CAGR, annual return, volatility, Sharpe ratio, and max drawdown

## Key Result

The momentum strategy achieved a higher CAGR and Sharpe ratio than SPY, but performance was heavily influenced by NVDA. After removing NVDA, the strategy underperformed SPY, showing the need for robustness testing.

## Next Steps

- Add more factors
- Improve backtesting engine
- Add risk controls
- Build dashboard or app interface