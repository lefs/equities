"""This module containts the Universe class.

It can be used to group and manage descriptive, fundamental, and price data
for a number of equities.
"""

import pathlib
import tablib
import pandas as pd
import equities.utils


class Universe:
    """Represents a universe of equities."""

    SUPPORTED_STORAGE_FORMATS = ['xlsx', 'json']

    def __init__(self, filename=None, prices_helper=None, prices_yr_period=5):
        """Creates a Universe object.

        filename      -- the filename of the universe to load; xlsx or json.
        prices_helper -- helper function for fetching price data.
        prices_yr_period -- how many years of price data to request.
        """
        self._id_column_name = 'Ticker'
        self._prices_yr_period = prices_yr_period
        self._prices_index = 'date'
        self.filename = filename
        if self.filename:
            self.load(self.filename)
        else:
            self._universe_file = None
            self.equities = tablib.Dataset()
            self.prices = pd.DataFrame()
        if prices_helper is None:
            self._prices_helper = equities.utils.download_iex_eod_prices
        else:
            self._prices_helper = prices_helper

    def __len__(self):
        """Returns the number of equities in the universe."""
        return len(self.tickers)

    def import_file(self, filename, id_column_name=None):
        """Import a CSV, XLS/XLSX, JSON file with descriptive stock data."""
        old_equities = self.equities
        self.equities.load(open(filename).read())

        col_names = self.columns
        if id_column_name:
            if id_column_name not in col_names:
                # User is asking for a column name that doesn't exist
                # in the imported file.
                self.equities = old_equities
                msg = "Column name '{}' not found in file".\
                    format(id_column_name)
                raise IdColumnError(msg)
            else:
                self._id_column_name = id_column_name
        else:
            if self._id_column_name not in col_names:
                if self._id_column_name.lower() in col_names:
                    self._id_column_name = self._id_column_name.lower()
                else:
                    # Give up at this point.
                    self.equities = old_equities
                    msg = "No column named '{}' or '{}' in data.".\
                        format(self._id_column_name,
                               self._id_column_name.lower())
                    raise IdColumnError(msg)

    @property
    def columns(self):
        """Return a list of equity column names."""
        if not self.equities.dict:
            return []

        return self.equities.headers

    @property
    def tickers(self):
        """Return a list of tickers in the universe."""
        if not self.equities.dict:
            return []

        return self.equities[self._id_column_name]

    def equity(self, ticker_symbol):
        """Return a dict with data for given ticker symbol."""
        if not self.equities.dict:
            return {}

        try:
            row_index = \
                self.equities[self._id_column_name].index(ticker_symbol)
        except ValueError:
            return {}
        # Replace 'None' strings with real None objects.
        data = [None if v == 'None' else v for v in
                self.equities[row_index]]

        return dict(zip(self.columns, data))

    def save(self, filename=None):
        """Save the current universe to a file."""
        if not filename and not self.filename:
            raise UniverseFilenameNotSet
        elif filename:
            self.filename = filename

        book = tablib.Databook()
        book.add_sheet(self.equities)
        if not self.prices.empty:
            prices = tablib.Dataset().load(self.prices.to_csv())
            book.add_sheet(prices)

        with open(self.filename, 'wb') as fname:
            fname.write(book.xlsx)

    def load(self, universe_file):
        """Load a universe from a file."""
        book = tablib.Databook()
        file_format = self._detect_file_format(universe_file)
        with open(universe_file, 'rb') as filename:
            book.load(filename.read(), file_format)
        self._universe_file = book
        self.equities = book.sheets()[0]
        if self._universe_file.size > 1:
            # We assume the second sheet is prices.
            self.prices = book.sheets()[1].df
            # Ensure prices index is Datetime.
            try:
                self.prices.set_index(
                    pd.DatetimeIndex(self.prices[self._prices_index]),
                    inplace=True
                )
            except KeyError:
                pass
        else:
            self.prices = pd.DataFrame()

    def fetch_prices(self):
        """Fetch prices for each equity in the universe."""
        prices = {}
        for ticker in self.tickers:
            if not self.prices.empty:
                existing_prices = self.prices[ticker]
            else:
                existing_prices = pd.Series(name=ticker)
            prices[ticker] = self._prices_helper(ticker, existing_prices,
                                                 self._prices_yr_period)

        self.prices = pd.concat(prices.values(), axis=1)
        # Ensure prices index is Datetime.
        self.prices.set_index(pd.DatetimeIndex(self.prices.index),
                              inplace=True)

    def add_column(self, column_name):
        """Add a new column to the descriptive data."""
        if self.equities.dict:
            if column_name not in self.columns:
                empty_rows = ['' for i in range(self.equities.height)]
                self.equities.append_col(empty_rows, header=column_name)

    def _detect_file_format(self, filename):
        """Detect file format from file extension."""
        ext = pathlib.Path(filename).suffix.lstrip('.')
        if ext in self.SUPPORTED_STORAGE_FORMATS:
            return ext
        raise UnsupportedFormat


class UniverseFilenameNotSet(RuntimeError):
    "Universe has no filename associated with it."


class IdColumnError(RuntimeError):
    "Please specify a unique id column (it's 'Ticker' or 'ticker' by default.)"


class UnsupportedFormat(NotImplementedError):
    "Format is not supported."
