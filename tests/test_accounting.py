import unittest
import numpy as np
import pandas as pd
from src.backtest import run_factor_backtest
from src.metrics import calculate_performance_metrics

class AccountingTest(unittest.TestCase):
    def run_case(self, values, fee=0, select=None):
        dates = pd.date_range('2019-01-31', periods=13, freq='ME').append(pd.DatetimeIndex(['2020-02-03', '2020-02-28', '2020-03-31']))
        prices = pd.DataFrame(100., index=dates, columns=['A','B','C','D'])
        for date, changes in values.items():
            for stock, value in changes.items(): prices.loc[pd.Timestamp(date):, stock] = value
        def score(current_prices, current_returns, formation_date):
            stocks = select(formation_date) if select else ['A','B']
            return pd.Series({s: 2-i for i,s in enumerate(stocks)})
        return run_factor_backtest(prices, score, top_n=2, transaction_cost_bps=fee)

    def test_buy_hold_and_zero_cost(self):
        returns, holdings, trades = self.run_case({'2020-02-03': {'A':120}, '2020-02-28': {'A':100}})
        self.assertAlmostEqual(returns.iloc[0], 0)
        self.assertAlmostEqual(trades.iloc[0].buys, 1)
        self.assertAlmostEqual(trades.iloc[0].sells, 0)
        self.assertAlmostEqual(trades.iloc[1].gross_traded_value, 0)

    def test_drift_and_replacement(self):
        _, holdings, trades = self.run_case({'2020-02-03': {'A':120}})
        self.assertAlmostEqual(holdings.iloc[0].ending_weights['A'], 120/220)
        self.assertAlmostEqual(trades.iloc[1].buys, 1/22)
        self.assertAlmostEqual(trades.iloc[1].sells, 1/22)
        _, _, trades = self.run_case({}, select=lambda d: ['A','B'] if d.month==1 else ['C','D'])
        self.assertAlmostEqual(trades.iloc[1].gross_traded_value, 2)

    def test_costs(self):
        wealth=[]
        for fee in (0,5,10,25):
            r, _, t = self.run_case({}, fee, lambda d: ['A','B'] if d.month==1 else ['C','D'])
            wealth.append((1+r).prod())
            self.assertAlmostEqual(t.iloc[0].transaction_cost, fee/10000*t.iloc[0].buys)
        self.assertTrue(all(x>y for x,y in zip(wealth, wealth[1:])))

    def test_weekend_month_end_return_boundaries(self):
        dates = pd.date_range('2019-01-31', periods=13, freq='ME').append(pd.DatetimeIndex(['2020-02-28', '2020-03-02', '2020-03-31']))
        prices = pd.DataFrame({'A': 100.0, 'B': 100.0}, index=dates)
        prices.loc['2020-02-28':, 'A'] = 110.0
        prices.loc['2020-03-02':, 'A'] = 121.0
        def scores(**kwargs): return pd.Series({'A': 2.0, 'B': 1.0})
        r, _, t = run_factor_backtest(prices, scores, top_n=2)
        self.assertAlmostEqual(r.iloc[0], 0.05)
        self.assertAlmostEqual(r.iloc[1], 0.05)
        self.assertEqual(t.iloc[0].holding_until, pd.Timestamp('2020-02-29'))
        self.assertEqual(t.iloc[1].formation_date, pd.Timestamp('2020-02-29'))

    def test_metrics_initial_loss(self):
        r = pd.Series([-0.1, 0], index=pd.to_datetime(['2020-02-29','2020-03-31']))
        m = calculate_performance_metrics(r)
        self.assertAlmostEqual(m['Max Drawdown'], -0.1)
        self.assertAlmostEqual(m['CAGR'], 0.9**6-1)

if __name__ == '__main__': unittest.main()
