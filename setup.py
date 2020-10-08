from setuptools import setup, find_packages

setup(
    name='equities',
    version='0.2',
    description='Keep track of an investment universe in a simple manner',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'openpyxl>=3.0.5',
        'tablib>=2.0',
        'pandas>=1.1.3',
        'pandas-datareader>=0.9.0'
    ]
)
