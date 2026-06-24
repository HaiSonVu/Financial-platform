import pandas as pd

def calculate_momentum(prices, lookback=252):
    return prices.pct_change(lookback)
