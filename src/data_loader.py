import yfinance as yf
import pandas as pd


def download_prices(
    tickers,
    start,
    end
):
    """
    Download adjusted closing prices from Yahoo Finance.
    """

    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True
    )

    return data["Close"]

def load_prices(
    filepath="../data/prices.csv"
):
    """
    Load saved price data.
    """

    return pd.read_csv(
        filepath,
        index_col=0,
        parse_dates=True
    )