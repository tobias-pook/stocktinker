from setuptools import setup

requirements = ['pandas',
                'pandas_datareader',
                'python-slugify',
                'openpyxl',
                'yahoo-finance',
                'matplotlib',
                'fix_yahoo_finance',
                'lxml']

setup(name='stocktinker',
      version='0.1',
      description='A python package to tinker with stock fundamentals and quotes',
      url='https://github.com/tobias-pook/stocktinker',
      author='Tobias Pook',
      author_email='test@example.com',
      license='MIT',
      packages=['stocktinker'],
      scripts=['bin/create_xls_report.py'],
      install_requires=requirements,
      long_description='''
      This package contains code to build analysis for stock data based on
      moringstar data and goolge price quotes.
      ''',
      zip_safe=False)
