"""Tests for Universe class."""


import os
from pathlib import Path
import pytest
import pandas as pd
from .context import equities


def test_creation_without_filename():
    """Passing no filename should invoke defaults."""
    univ = equities.Universe()
    assert (univ.filename, univ.equities.dict, univ.prices.empty) == \
        (None, [], True)


def test_creation_with_filename(assets_dir, tickers):
    """Create the object by loading the universe file successfully."""
    universe_file = Path(assets_dir) / 'universe.xlsx'
    univ = equities.Universe(universe_file)

    assert set(univ.tickers) == set(tickers)
    assert type(univ.prices.index).__name__ == 'DatetimeIndex'


def test_import_csv_file(stocks_csv, csv_column_names):
    """Successfully import a CSV file."""
    univ = equities.Universe()
    univ.import_file(stocks_csv)

    assert univ.columns == csv_column_names


def test_import_incorrect_column_id(stocks_csv):
    """Specified id column name doesn't exist, raise IdColumnError."""
    univ = equities.Universe()

    with pytest.raises(equities.universe.IdColumnError):
        univ.import_file(stocks_csv, id_column_name='Non existent column')


def test_column_list(stocks_csv, csv_column_names):
    """Successfully list the universe columns."""
    univ = equities.Universe()
    univ.import_file(stocks_csv)

    assert univ.columns == csv_column_names


def test_ticker_list(stocks_csv, tickers):
    """Get a list of all tickers in this universe."""
    univ = equities.Universe()
    univ.import_file(stocks_csv)

    assert set(univ.tickers) == set(tickers)


def test_find_existent_ticker(stocks_csv, csv_column_names, dre_data):
    """Get a dict with data for a given ticker."""
    univ = equities.Universe()
    univ.import_file(stocks_csv)

    assert univ.equity('DRE') == dict(zip(csv_column_names, dre_data))


def test_find_non_existent_ticker(stocks_csv):
    """Get an empty dict if ticker doesnt exist in our universe."""
    univ = equities.Universe()
    univ.import_file(stocks_csv)

    with pytest.raises(equities.universe.TickerSymbolNotFound):
        univ.equity('NONE')


def test_prices(stocks_csv, fake_prices):
    """Get a pd.Series object with price data for a given ticker."""
    def helper(ticker, _prices, _period):
        return pd.Series(fake_prices, name=ticker)
    univ = equities.Universe(prices_helper=helper)
    univ.import_file(stocks_csv)
    ticker = 'DRE'
    expected_series = pd.Series(fake_prices, name=ticker)
    expected_series.index = pd.DatetimeIndex(expected_series.index)
    # Fetch the prices.
    univ.fetch_prices()

    prices = univ.prices[ticker]

    pd.testing.assert_series_equal(prices, expected_series)


def test_save_universe_without_file():
    """Raise UniverseFilenameNotSet if we try to save a universe without a
    filename.
    """
    univ = equities.Universe()

    with pytest.raises(equities.universe.UniverseFilenameNotSet):
        univ.save()


def test_save_universe_new_file(tmpdir, stocks_csv, fake_prices):
    """Save universe contents to a file by calling save() with a filename."""
    def helper(ticker, _prices, _period):
        return pd.Series(fake_prices, name=ticker)
    universe_file = tmpdir.join('universe.xlsx')
    univ = equities.Universe(prices_helper=helper)
    univ.import_file(stocks_csv)
    # Let's also get some price data.
    univ.fetch_prices()

    univ.save(universe_file)

    assert os.stat(universe_file).st_size > 0


def test_save_universe_file(tmpdir, fake_prices, xlsx_content):
    """Save updated universe contents to an existing universe file."""
    def helper(ticker, _prices, _period):
        return pd.Series(fake_prices, name=ticker)
    universe_file = tmpdir.join('universe2.xlsx')
    universe_file.write_binary(xlsx_content)
    univ = equities.Universe(universe_file, prices_helper=helper)

    # Contains no prices.
    assert univ.prices.empty is True
    # Let's get some price data.
    univ.fetch_prices()
    univ.save()
    # Reload a universe, with the saved file this time.
    univ = equities.Universe(universe_file)

    assert univ.prices.empty is False


def test_load_universe(assets_dir, tickers):
    """Load a universe file."""
    universe_file = Path(assets_dir) / 'universe.xlsx'
    univ = equities.Universe()

    univ.load(universe_file)

    assert set(univ.tickers) == set(tickers)


def test_fetch_prices_calls_helper(stocks_csv):
    """Should pass 3 arguments to prices_helper."""
    def helper_func(ticker, price_series, period):
        assert isinstance(ticker, str)
        assert isinstance(price_series, pd.Series)
        assert isinstance(period, int)

        return pd.Series(name='ticker')

    univ = equities.Universe(prices_helper=helper_func)
    univ.import_file(stocks_csv)

    univ.fetch_prices()


def test_add_column(stocks_csv, csv_column_names):
    """Should add new column to universe.equities."""
    univ = equities.Universe()
    univ.import_file(stocks_csv)

    assert univ.columns == csv_column_names
    new_column_name = 'test_col'
    univ.add_column(new_column_name)

    assert new_column_name in univ.columns
