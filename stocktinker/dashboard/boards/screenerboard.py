from urllib.request import urlopen
import lxml

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np

from stocktinker.stock import Stock

from ..app import app
from ..app import stock_cache

def get_available_stock_options():
    options = []
    for symbol, stock in stock_cache.items():
        options.append({'label': stock.company_name, 'value': symbol})
    return options

def get_ratio_axis_options():
    if not stock_cache:
        return [{'label': "earnings-ps-growth", 'value': "earnings-ps-growth"},
                {'label': "book-value-ps-growth", 'value': "book-value-ps-growth"},
                {'label': "shares", 'value': "shares"}  ]
    option_set = set(list(stock_cache[list(stock_cache)[-1]].ratios))
    for ticker, stock in stock_cache.items():
        option_set = option_set.intersection(set(list(stock.ratios)))
        print(option_set)
    return [{'label': o, 'value': o} for o in option_set]

layout = html.Div([
    html.Div(
        [dcc.Input(id='screener-symbol-input', type="text", value='', placeholder="AAPL GOOG"),
         html.Button(id='screener-submit-button', n_clicks=0, children='add companies')],
        style={'width': '49%', 'display': 'inline-block'}
    ),
    html.Div(id='screener-stock-selection-div', children=[
            dcc.Dropdown(
                id='screener-stock-selection',
                options=get_available_stock_options(),
                multi=True,
                value=""
            )
        ]
    ),
    html.Div([ html.Div(id="screener-2d-xaxis-div", children=[
                   html.Div(u"x-axis:"),
                   dcc.Dropdown(
                       id='screener-2d-xaxis-selection',
                       options=get_ratio_axis_options(),
                       value='book-value-ps-growth'
                   ),]
                   ,style={'width': '32%', 'display': 'inline-block'}),
               html.Div(id="screener-2d-yaxis-div", children=[
                              html.Div(u"y-axis:"),
                              dcc.Dropdown(
                                  id='screener-2d-yaxis-selection',
                                  options=get_ratio_axis_options(),
                                  value="earnings-ps-growth"
                              ),]
                              ,style={'width': '32%', 'display': 'inline-block'}),
               html.Div(id="screener-2d-size-axis-div", children=[
                              html.Div(u"y-axis:"),
                              dcc.Dropdown(
                                  id='screener-2d-size-axis-selection',
                                  options=get_ratio_axis_options(),
                                  value="shares"
                              ),]
                              ,style={'width': '32%', 'display': 'inline-block'}),
               dcc.Graph(id='screener-2d-graph')],
             style={'width': '49%', 'display': 'inline-block'}
    ),
])

@app.callback(Output('screener-stock-selection-div', 'children'),
              [Input('screener-submit-button', 'n_clicks')],
              [ State('screener-symbol-input', 'value'),
                State('screener-stock-selection', 'value')])
def onadd_stock_company_name_label(n_clicks, symbol, selected_stocks):
    symbols = []
    if len(symbol.split(" ")) > 1:
        symbols = symbol.split(" ")
    if len(symbol.split(";")) > 1:
        symbols = symbol.split(";")
    if not symbols:
        symbols = [symbol]
    symbols = [ s for s in symbols if symbol]
    for symbol in symbols:
        stock = stock_cache.get(symbol, Stock(symbol))
        if symbol not in stock_cache:
            stock_cache[symbol] = stock
    return dcc.Dropdown(
                        id='screener-stock-selection',
                        options=get_available_stock_options(),
                        multi=True,
                        value=list(set(list(selected_stocks) + symbols))
                    )

@app.callback(Output('screener-2d-xaxis-selection', 'options'),
              [Input('screener-stock-selection', 'value')])
def onadd_stock_xaxis_options(symbols):
    print("updating x axis")
    stocks = [stock_cache.get(symbol, Stock(symbol)) for symbol in symbols]
    return get_ratio_axis_options()

@app.callback(Output('screener-2d-yaxis-selection', 'options'),
              [Input('screener-stock-selection', 'value')])
def onadd_stock_yaxis_options(symbols):
    stocks = [stock_cache.get(symbol, Stock(symbol)) for symbol in symbols]
    return get_ratio_axis_options()

@app.callback(Output('screener-2d-size-axis-selection', 'options'),
              [Input('screener-stock-selection', 'value')])
def onadd_stock_yaxis_options(symbols):
    stocks = [stock_cache.get(symbol, Stock(symbol)) for symbol in symbols]
    return get_ratio_axis_options()

@app.callback(Output('screener-2d-graph', 'figure'),
              [Input('screener-stock-selection', 'value'),
              Input('screener-2d-xaxis-selection', 'value'),
              Input('screener-2d-yaxis-selection', 'value'),
              Input('screener-2d-size-axis-selection', 'value')])
def update_2d_graph(symbols, xkey, ykey, sizekey):

    data = []
    stocks = [stock_cache.get(symbol, Stock(symbol)) for symbol in symbols]
    if not stocks:
        max_area = 1
    elif len(stocks) > 1:
        max_area = max(*[stock.ratios[sizekey].iloc[-1] for stock in stocks])
    else:
        max_area = stocks[0].ratios[sizekey].iloc[-1]

    # max_area = 20000000
    for stock in stocks:
        if not xkey:
            x=[]
        else:
            x=[stock.ratios[xkey].iloc[-1]]
        if not ykey:
            y=[]
        else:
            y=[stock.ratios[ykey].iloc[-1]]
        data.append(go.Scatter(
                    x=x,
                    y=y,
                    text=[stock.company_name],
                    mode='line',
                    name=stock.symbol,
                    marker={
                        'sizemode': 'area', #stock.ratios[sizekey].iloc[-1],
                        'sizeref': 2. * max_area / (40.**2),
                        'size': [stock.ratios[sizekey].iloc[-1]],
                        'sizemin' : 4,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'blue'}
                    }
                   ))
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': xkey,
                'type': 'linear'
            },
            yaxis={
                'title': ykey,
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
            hovermode='closest',
            showlegend=False,
        ),
    }
