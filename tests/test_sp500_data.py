import unittest
from unittest.mock import patch
import pandas as pd
from src.data_loader import download_price_history, load_constituents

class DatasetTests(unittest.TestCase):
    def test_symbols_and_snapshot_validation(self):
        rows = ''.join(f'<tr><td>SYM{i}</td><td>Company {i}</td><td>Sector</td></tr>' for i in range(399))
        rows += '<tr><td>BRK.B</td><td>Berkshire</td><td>Financials</td></tr>'
        html = '<table id="constituents"><thead><tr><th>Symbol</th><th>Security</th><th>GICS Sector</th></tr></thead><tbody>' + rows + '</tbody></table>'
        class Response:
            text=html
            content=html.encode()
            def raise_for_status(self): pass
        with patch('src.data_loader.requests.get', return_value=Response()):
            constituents, digest = load_constituents()
        self.assertEqual(constituents.iloc[-1]['yahoo_symbol'], 'BRK-B')
        self.assertEqual(len(digest),64)

    def test_missing_ticker_is_retained(self):
        dates=pd.to_datetime(['2020-01-02','2020-01-03'])
        data=pd.DataFrame({('Close','AAA'):[1.0,2.0], ('Close','BBB'):[float('nan'),float('nan')]},index=dates)
        with patch('src.data_loader.yf.download',return_value=data):
            prices=download_price_history(['AAA','BBB'], '2020-01-01','2020-02-01',pause=0)
        self.assertEqual(prices.columns.tolist(), ['AAA','BBB'])
        self.assertEqual(prices['AAA'].notna().sum(), 2)
        self.assertTrue(prices['BBB'].isna().all())

if __name__ == '__main__': unittest.main()
