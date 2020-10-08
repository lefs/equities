"""Various utility/helper functions."""


import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import pandas_datareader.data as datareader


def download_iex_eod_prices(ticker, exisiting_prices, years='5'):
    """Helper method to download EoD prices from IEX."""

    exisiting_prices = exisiting_prices.copy(deep=True).to_frame()

    # Estimate the shortest period needed.
    end_date = datetime.datetime.utcnow().date()
    if exisiting_prices.empty:
        # If existing prices are empty, get the full period.
        start_date = end_date - relativedelta(years=years)
    else:
        start_date = max(exisiting_prices.index).date()

    frame = datareader.DataReader(ticker.upper(), 'iex', start_date, end_date)
    # Only need 'close' prices for now.
    frame = frame['close'].to_frame(name=ticker.upper())

    prices = \
        frame if exisiting_prices.empty else exisiting_prices.append(frame)

    return prices
