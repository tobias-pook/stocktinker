# Stocktinker

A tool to play around with stock data. Currently in alpha

## Installation
The package is currently not listed in pypip. You may however use pip to install
it locally:

     cd stocktinker
     pip install -e .

## Using the excel export
The script `create_xls_report.py` allows to create excel reports for a given list
of ticker symbols. One xls file with a detailed report is created in `/reports` for every ticker
symbol in addition to a summary table for all selected tickers.

## Using the dashboard

### dash installation
The dashboard uses plotly and dash, which currently need a fixed set of versions
to work together as intended (see [dash installation isntructions](https://plot.ly/dash/installation))

    pip install dash==0.19.0  # The core dash backend
    pip install dash-renderer==0.11.1  # The dash front-end
    pip install dash-html-components==0.8.0  # HTML components
    pip install dash-core-components==0.14.0  # Supercharged components
    pip install plotly --upgrade  # Latest Plotly graphing library

### Usage
The script `start_tinker_dashboard.py` should be available after instlling this
package and dash. Running it creates a local server instance which can be
accessed in your browser under the address: `http://127.0.0.1:8050`

currently two routes are implemented:

* `/stock` Has an input field for a single stock ticker symbol and shows a summary
of key ratios, growth plots and price charts for the selected stock.
* `/screener` Allows to add a list of plots into a one plotly scatter plot.
The displayed information in the x and y axis and the size of point in the plots
can be chosen from a list of available key ratios for the selected stocks.
