import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.userInfo import UserInfo

import numpy as np


from dash.stock import Stock
from dash.userInfo import UserInfo

from ..app import app
from ..app import stock_cache
def get_layout(company):
    stock = stock_cache.get(company, Stock(company))

    stock_company_name_output = onsumbit_stock_company_name_label_raw(stock)

    ratios_df = stock.load_report_csv_to_original_df('ratios')
    ratios_table = dbc.Table.from_dataframe(ratios_df)

    balancesheet_df = stock.load_report_csv_to_original_df('balancesheet')
    balancesheet_table = dbc.Table.from_dataframe(balancesheet_df)

    cashflow_df = stock.load_report_csv_to_original_df('cashflow')
    cashflow_table = dbc.Table.from_dataframe(cashflow_df)

    income_df = stock.load_report_csv_to_original_df('income')
    income_table = dbc.Table.from_dataframe(income_df)

    layout = html.Div([
        html.Div([
            html.Div(
                [dcc.Input(id='stock-symbol-input-raw', type="text", value=company),
                 html.Button(id='submit-button-raw', children='Submit', style={'backround' : 'white'})],
                style={'width': '49%', 'display': 'inline-block'}
            ),
            html.Div(
                [html.Div(id='stock-company-name-label_raw', children=stock_company_name_output, style={'fontSize': 14})],
                style={'width': '49%', 'display': 'inline-block', }
            ),
            ],style={'position': 'sticky', 'top' : '90px', 'background': 'white'}
        ),
        html.Div(id='fundamental-redirect-raw'),
        html.H1("Income:"),
        income_table,
        html.H1("Balancesheet:"),
        balancesheet_table,
        html.H1("Cashflow:"),
        cashflow_table,
        html.H1("Ratios:"),
        ratios_table
    ],style={'padding': '10px', 'margin-right':'10px'})
    return layout
def onsumbit_stock_company_name_label_raw(stock):
    print('onsumbit_stock_company_name_label_raw')
    return  u'{name}'.format(name=stock.company_name)
@app.callback(Output('fundamental-redirect-raw', 'children'),
              [Input('submit-button-raw', 'n_clicks')],
              [State('stock-symbol-input-raw', 'value')])
def on_stock_update(n_clicks,
                    symbol):
    print('on_stock_update n_clicks'+str(n_clicks))
    if not n_clicks:
        return ''
    return dcc.Location(pathname='/Prod/raw-data/'+symbol.upper(), id='company_redirect-raw')
