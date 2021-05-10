import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.userInfo import UserInfo

import numpy as np
import pandas as pd

from dash.stock import Stock
from dash.userInfo import UserInfo

from ..app import app
from ..app import stock_cache
def get_layout(token):
    userInfo = UserInfo(token['username'])
    lest_from_db = userInfo.get_watch_list()
    watch_list = []
    for record in lest_from_db:
        watch = dict()
        symbol = record['company'].upper()
        fundamentals_link = html.A(html.P(symbol), href='/Prod/fundamentals/' + symbol)
        watch['Company'] = fundamentals_link
        watch['Name'] = record['company_name']
        watch['Currency'] = record['currency']
        watch['EPS TTM'] = record['epsTTM']
        watch['Estimated Growth'] = record['average_growth']
        watch['Projection Years'] = record['projection_years']
        watch['Excpected EPS'] = record['excpected_eps']
        watch['Target Yield'] = record['target_yield']
        watch['Target P/E'] = record['target_p_e']
        watch['Expected Dividends'] = record['expected_dividends']
        watch['Expected Dividends Growth'] = record['expected_dividends_growth']
        watch['Projected Price'] = record['projected_price']
        watch['Projected Total Dividends'] = ''
        if 'projected_total_dividends' in record:
            watch['Projected Total Dividends'] = record['projected_total_dividends']
        watch['Target Price'] = ''
        if 'target_price' in record:
            watch['Target Price'] = record['target_price']
        watch['Current Price'] = ''
        if 'current_price' in record:
            watch['Current Price'] = record['current_price']
        watch['Delta'] = ''
        if 'delta' in record:
            watch['Delta'] = record['delta']
        watch['Alert Price'] = "no alert defined"
        if 'alert_price' in record:
            watch['Alert Price'] = record['alert_price']
        remove_link = html.A(html.P('x'), href='/Prod/remove-from-watch-list/' + record['company'])
        watch['Remove'] = remove_link
        watch_list.append(watch)
    df_company = pd.DataFrame(watch_list, columns=['Company'])
    df_other_columns = pd.DataFrame(watch_list, columns=['Company', 'Name', 'Currency', 'EPS TTM', 'Estimated Growth', 'Projection Years', 'Excpected EPS', 'Target Yield', 'Target P/E', 'Expected Dividends', 'Expected Dividends Growth', 'Projected Price', 'Projected Total Dividends', 'Target Price', 'Current Price', 'Delta', 'Alert Price', 'Remove'])
    table_company = dbc.Table.from_dataframe(df_company)
    table_other_columns = dbc.Table.from_dataframe(df_other_columns, id='watchlist-tables')
    layout = html.Div([ 
                html.Td(table_other_columns)
    ],style={'overflow-x': 'scroll', 'padding': '10px', 'margin-right':'10px'})
    return layout
def remove_company(token, company):
    userInfo = UserInfo(token['username'])
    print('company:' + company)
    responce = userInfo.remove_company_from_watch_list(company)
    print(responce)
    return dcc.Location(id='redirect_back', href='/Prod/watchlist', refresh=True)
