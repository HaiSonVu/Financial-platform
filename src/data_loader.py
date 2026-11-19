import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf


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


SOURCE = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'


def load_constituents():
    """Fetch and validate Wikipedia's current constituent table."""
    response = requests.get(SOURCE, headers={'User-Agent': 'Mozilla/5.0 (compatible; educational-research/1.0)'}, timeout=30)
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text), attrs={'id': 'constituents'})
    if len(tables) != 1 or not {'Symbol', 'Security', 'GICS Sector'} <= set(tables[0].columns):
        raise ValueError('Could not identify the expected constituents table')
    frame = tables[0].copy()
    frame['Symbol'] = frame['Symbol'].astype(str).str.strip()
    if len(frame) < 400 or frame['Symbol'].duplicated().any():
        raise ValueError('Unexpected constituent count or duplicate symbols')
    frame['yahoo_symbol'] = frame['Symbol'].str.replace('.', '-', regex=False)
    if frame['yahoo_symbol'].duplicated().any():
        raise ValueError('Yahoo symbol mapping has duplicates')
    return frame, hashlib.sha256(response.content).hexdigest()


def download_price_history(symbols, start, end, batch_size=50, pause=1):
    """Download adjusted closes in batches; preserve missing values and failures.

    start is inclusive; end is exclusive. The returned columns always include all
    requested tickers, including completely unavailable tickers as all-NaN.
    """
    symbols = list(symbols)
    if not symbols or len(set(symbols)) != len(symbols) or batch_size < 1:
        raise ValueError('Provide unique symbols and a positive batch size')
    chunks = []
    for pos in range(0, len(symbols), batch_size):
        batch = symbols[pos:pos + batch_size]
        print(f'Downloading {pos+1}-{min(pos+len(batch), len(symbols))} of {len(symbols)}', flush=True)
        data = yf.download(batch, start=start, end=end, auto_adjust=True,
                           progress=False, threads=False, group_by='column')
        if data.empty:
            print(f'No prices returned for batch {pos//batch_size + 1}', flush=True)
        else:
            close = data['Close']
            if isinstance(close, pd.Series):
                close = close.to_frame(name=batch[0])
            chunks.append(close.reindex(columns=batch))
        if pos + batch_size < len(symbols) and pause:
            time.sleep(pause)
    if not chunks:
        raise RuntimeError('No prices downloaded; no dataset was saved')
    prices = pd.concat(chunks, axis=1).reindex(columns=symbols).sort_index()
    prices.index.name = 'Date'
    return prices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', default='2010-01-01', help='Inclusive date')
    parser.add_argument('--end', default='2025-01-01', help='Exclusive date')
    parser.add_argument('--output', required=True, type=Path, help='New output directory; never overwrite')
    args = parser.parse_args()
    if pd.Timestamp(args.start) >= pd.Timestamp(args.end):
        parser.error('start must be before end')
    if args.output.exists():
        parser.error('output directory already exists; choose a new path')
    retrieved = datetime.now(timezone.utc).isoformat()
    constituents, source_hash = load_constituents()
    prices = download_price_history(constituents['yahoo_symbol'], args.start, args.end)
    coverage = pd.DataFrame({'symbol': prices.columns, 'observations': prices.notna().sum().values,
                             'first_date': [s.first_valid_index() for _, s in prices.items()],
                             'last_date': [s.last_valid_index() for _, s in prices.items()]})
    metadata = {'retrieved_utc': retrieved, 'source': SOURCE, 'source_html_sha256': source_hash,
                'universe': 'current S&P 500 snapshot; not historical membership',
                'price_source': 'Yahoo Finance via yfinance; adjusted close',
                'yfinance_version': yf.__version__, 'start_inclusive': args.start, 'end_exclusive': args.end,
                'requested_symbols': len(constituents), 'symbols_with_no_prices': coverage.loc[coverage.observations == 0, 'symbol'].tolist(),
                'rows': len(prices), 'disclaimer': 'Survivorship bias, ticker changes, revised adjustments, and incomplete coverage remain.'}
    args.output.mkdir(parents=True, exist_ok=False)
    constituents.to_csv(args.output / 'constituents.csv', index=False)
    prices.to_csv(args.output / 'prices.csv')
    coverage.to_csv(args.output / 'coverage.csv', index=False)
    (args.output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()


def load_historical_membership(filepath):
    """Read dated constituent snapshots; dates are effective membership dates."""
    snapshots = pd.read_parquet(filepath, columns=['date', 'ticker'])
    snapshots['date'] = pd.to_datetime(snapshots['date'])
    if snapshots.empty or snapshots[['date', 'ticker']].isna().any().any():
        raise ValueError('Historical membership data is empty or incomplete')
    if snapshots.duplicated(['date', 'ticker']).any():
        raise ValueError('Duplicate historical membership records')
    return snapshots.sort_values(['date', 'ticker']).reset_index(drop=True)


def constituents_as_of(snapshots, date):
    """Return latest membership snapshot on or before date; fail if unavailable."""
    date = pd.Timestamp(date)
    eligible = snapshots.loc[snapshots['date'] <= date, 'date']
    if eligible.empty:
        raise ValueError(f'No historical membership available on {date.date()}')
    return pd.Index(snapshots.loc[snapshots['date'] == eligible.max(), 'ticker'])


def load_historical_prices(filepath):
    """Load a previously saved historical adjusted-price dataset in wide form."""
    data = pd.read_parquet(filepath, columns=['date', 'ticker', 'adj_close'])
    data['date'] = pd.to_datetime(data['date'])
    if data.duplicated(['date', 'ticker']).any():
        raise ValueError('Duplicate historical prices')
    return data.pivot(index='date', columns='ticker', values='adj_close').sort_index()
