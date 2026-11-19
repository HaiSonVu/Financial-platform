import unittest
import pandas as pd
from src.data_loader import constituents_as_of

class HistoricalMembershipTest(unittest.TestCase):
    def test_uses_latest_past_snapshot_and_no_future_additions(self):
        data = pd.DataFrame({'date':pd.to_datetime(['2020-01-01','2020-01-01','2020-02-03','2020-02-03']), 'ticker':['A','B','B','C']})
        self.assertEqual(set(constituents_as_of(data,'2020-02-02')), {'A','B'})
        self.assertEqual(set(constituents_as_of(data,'2020-02-03')), {'B','C'})
        with self.assertRaises(ValueError): constituents_as_of(data,'2019-12-31')

if __name__ == '__main__': unittest.main()

class SignalTimingTest(unittest.TestCase):
    def test_latest_close_and_future_membership_do_not_change_signal(self):
        from src.backtest import point_in_time_momentum_score
        dates = pd.date_range('2020-01-01', periods=5, freq='B')
        p = pd.DataFrame({'A':[100,101,102,103,104], 'B':[100,102,104,106,108], 'C':[100,110,120,130,140]},index=dates)
        membership = pd.DataFrame({'date':[dates[0],dates[0],dates[-1],dates[-1],dates[-1]],'ticker':['A','B','A','B','C']})
        def calc(x):
            return point_in_time_momentum_score(x,x.pct_change(),dates[-1],membership,lookback=2)
        original=calc(p)
        p.loc[dates[-1],:] = [500,1,1000]
        pd.testing.assert_series_equal(original,calc(p))
        self.assertTrue(pd.isna(original['C']))
