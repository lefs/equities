"""Fixtures for testing the Universe class."""


import pathlib
import pytest


JKHY_DATA = ['JKHY', '"Jack Henry & Associates, Inc."',
             'Technology,Business Software & Services', '9502.72', '38.81']
SNA_DATA = ['SNA', 'Snap-on Incorporated', 'Industrial Goods',
            'Small Tools & Accessories', '9507.61', '17.25']
DRE_DATA = ['DRE', 'Duke Realty Corporation', 'Financial',
            'REIT - Industrial', '9508.24', '35.95']


@pytest.fixture()
def tickers():
    """The list of ticers in our fake data."""
    return [JKHY_DATA[0], SNA_DATA[0], DRE_DATA[0]]


@pytest.fixture()
def fake_prices():
    """Dict with fake price data."""
    return {
        '2018-02-05':  164.29,
        '2018-02-06':  167.07,
        '2018-02-07':  166.63
    }


@pytest.fixture()
def dre_data():
    """Data for company with DRE ticker symbol."""
    return DRE_DATA


@pytest.fixture()
def csv_column_names():
    """Column names for the mock CSV file."""
    return ['Ticker', 'Company', 'Sector', 'Industry', 'Market Cap', 'P/E']


@pytest.fixture()
def csv_content(csv_column_names):
    """Descriptive stock information."""
    # Ticker,Company,Sector,Industry,Market Cap,P/E
    content = '{}\n{}\n{}\n{}'.format(','.join(csv_column_names),
                                      ','.join(JKHY_DATA),
                                      ','.join(SNA_DATA),
                                      ','.join(DRE_DATA))
    return content


@pytest.fixture()
def stocks_csv(tmpdir, csv_content):
    """Create a CSV file with some descriptive stock information."""
    csv_file = tmpdir.join('stocks.csv')
    csv_file.write(csv_content)

    return csv_file

@pytest.fixture()
def assets_dir():
    """Return the path of the directory with helper test files."""
    return pathlib.Path(__file__).resolve().parent / 'assets'


@pytest.fixture()
def xlsx_content():
    """Return xlsx content to be used in tests."""
    file = pathlib.Path(__file__).resolve().parent / 'assets' / \
        'universe2.xlsx'
    with open(file, 'rb') as xlsx_file:
        return xlsx_file.read()
