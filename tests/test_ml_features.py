import unittest
import numpy as np
import pandas as pd
from src.ml_features import build_ml_dataset, FEATURE_COLUMNS

class FeatureTests(unittest.TestCase):
    def setUp(self):
        dates = pd.bdate_range('2020-01-01', periods=330)
        self.prices = pd.DataFrame({'A':100*1.001**np.arange(len(dates)), 'B':100*1.002**np.arange(len(dates))}, index=dates)
        self.members = pd.DataFrame({'date': pd.to_datetime(['2019-01-01','2019-01-01']), 'ticker':['A','B']})

    def test_formulas_and_label(self):
        data = build_ml_dataset(self.prices, self.members)
        date = pd.Timestamp('2021-02-28')
        row = data.loc[(date,'A')]
        formation = self.prices.loc[:date].index[-1]
        prior = self.prices.index[self.prices.index.get_loc(formation)-1]
        pos = self.prices.index.get_loc(prior)
        a = self.prices.A
        self.assertEqual(row.signal_date, prior)
        self.assertAlmostEqual(row.momentum_6m, a.iloc[pos]/a.iloc[pos-126]-1)
        self.assertAlmostEqual(row.momentum_12_1, a.iloc[pos-21]/a.iloc[pos-252]-1)
        self.assertAlmostEqual(row.reversal_21d, -(a.iloc[pos]/a.iloc[pos-21]-1))
        self.assertAlmostEqual(row.volatility_63d, a.pct_change(fill_method=None).iloc[pos-62:pos+1].std()*np.sqrt(252))
        end = self.prices.loc[:'2021-03-31'].index[-1]
        self.assertAlmostEqual(row.next_month_return, a.loc[end]/a.loc[formation]-1)

    def test_future_prices_do_not_change_features(self):
        date=pd.Timestamp('2021-02-28')
        baseline=build_ml_dataset(self.prices,self.members).loc[(date,'A'),FEATURE_COLUMNS]
        p=self.prices.copy(); p.loc[p.index >= pd.Timestamp('2021-02-26'),'A'] *= 2
        updated=build_ml_dataset(p,self.members).loc[(date,'A'),FEATURE_COLUMNS]
        pd.testing.assert_series_equal(baseline,updated)

    def test_missing_prices_and_missing_labels_remain_missing(self):
        p=self.prices.copy(); p.loc['2021-02-26','A']=np.nan
        data=build_ml_dataset(p,self.members)
        self.assertTrue(pd.isna(data.loc[(pd.Timestamp('2021-02-28'),'A'),'next_month_return']))
        self.assertTrue(data.xs(data.index.get_level_values(0).max())['next_month_return'].isna().all())

    def test_excludes_future_member(self):
        members=pd.DataFrame({'date':pd.to_datetime(['2019-01-01','2021-03-01','2021-03-01']), 'ticker':['A','A','B']})
        data=build_ml_dataset(self.prices,members)
        self.assertNotIn((pd.Timestamp('2021-02-28'),'B'),data.index)
        self.assertIn((pd.Timestamp('2021-03-31'),'B'),data.index)

if __name__=='__main__': unittest.main()
