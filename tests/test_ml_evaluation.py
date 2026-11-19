import unittest
import numpy as np
import pandas as pd
from src.experiment import monthly_rank_ic, predict_month_scores

class EvaluationTests(unittest.TestCase):
    def test_rank_ic_and_constant_predictions(self):
        idx=pd.MultiIndex.from_product([pd.to_datetime(['2020-01-31','2020-02-29']), ['A','B','C']],names=['formation_date','ticker'])
        pred=pd.Series([1,2,3,1,1,1],index=idx)
        actual=pd.Series([3,2,1,1,2,3],index=idx)
        result=monthly_rank_ic(pred,actual)
        self.assertAlmostEqual(result.iloc[0].rank_ic,-1)
        self.assertTrue(np.isnan(result.iloc[1].rank_ic))
        self.assertEqual(result.iloc[0].n_stocks,3)
    def test_predictions_ignore_unknown_labels_and_reject_future_features(self):
        class Model:
            def predict(self,x): return x['f'].to_numpy()
        idx=pd.MultiIndex.from_tuples([(pd.Timestamp('2020-01-31'),'A'),(pd.Timestamp('2020-01-31'),'B')],names=['formation_date','ticker'])
        panel=pd.DataFrame({'f':[1.,2.], 'next_month_return':[np.nan,0.4], 'signal_date':pd.to_datetime(['2020-01-30','2020-01-30'])},index=idx)
        scores=predict_month_scores(Model(),panel,'2020-01-31','2020-01-30',['f'])
        self.assertEqual(scores.to_dict(),{'A':1.,'B':2.})
        panel.loc[(pd.Timestamp('2020-01-31'),'A'),'signal_date']=pd.Timestamp('2020-01-31')
        with self.assertRaises(ValueError): predict_month_scores(Model(),panel,'2020-01-31','2020-01-30',['f'])

if __name__ == '__main__': unittest.main()

class ConversionTests(unittest.TestCase):
    def test_conversion_combines_positions_without_a_trade(self):
        from src.backtest import run_factor_backtest
        dates = pd.date_range('2019-01-31', periods=13, freq='ME').append(pd.DatetimeIndex(['2020-02-03','2020-02-28','2020-03-31']))
        prices = pd.DataFrame({'OLD':100., 'NEW':100.}, index=dates)
        prices.loc['2020-02-03':,'OLD']=np.nan
        prices.loc['2020-02-03':,'NEW']=110.
        def score(current_prices,current_returns,formation_date):
            return pd.Series({'OLD':2.,'NEW':1.}) if formation_date.month == 1 else pd.Series({'NEW':1.})
        r,h,t=run_factor_backtest(prices,score,top_n=2,corporate_actions=[{'date':'2020-02-03','old':'OLD','new':'NEW','ratio':1}])
        self.assertAlmostEqual(r.iloc[0],0.10)
        self.assertEqual(h.iloc[0]['ending_weights'],{'NEW':1.0})
        self.assertAlmostEqual(t.iloc[1]['gross_traded_value'],0.0)
