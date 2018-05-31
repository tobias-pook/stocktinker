import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np

from stocktinker.stock import Stock

from ..app import app
from ..app import stock_cache

layout = html.Div([
    html.Div([
        html.Div(
            [dcc.Input(id='stock-symbol-input', type="text", value='AAPL'),
             html.Button(id='submit-button', n_clicks=0, children='Submit', style={'backround' : 'white'}),
             html.Button(id='clear-cache-button', n_clicks=0, children='Reload', style={'backround' : 'white'})],
            style={'width': '49%', 'display': 'inline-block'}
        ),
        html.Div(
            [html.Div(id='stock-company-name-label', children=u'choose company',style={'fontSize': 14})],
            style={'width': '49%', 'display': 'inline-block', }
        ),
        ],style={'position': 'sticky', 'top' : 1, 'background': 'white'}

    ),
    html.Div(
        [ html.Div([
                    html.Table(id='stock-ratios-summary-table'),
                    dcc.Graph(id='stock-rule1-growth-plot'),
                    dcc.Graph(id='stock-historic-closing-price-plot')
                    ])
        ],
        style={'width': '48%', 'display': 'inline-block'}
    ),
    html.Div(
        [  html.Table(id='stock-rule1-summary-table'),
           html.Table(id='stock-projection-input-table'),
           html.Table(id='stock-projection-output-table'),
        ],
        style={'width': '48%',
               'display': 'inline-block',
               'vertical-align':'top',
               'padding': '10px'}
    ),
    html.H1("Key Ratios"),
    html.Div([ html.Table(id='stock-ratios-table')],
             style={'width': '65%', 'display': 'inline-block'}
    ),
])

@app.callback(Output('submit-button', 'n_clicks'),
              [Input('clear-cache-button', 'n_clicks')],
            [ State('stock-symbol-input', 'value')])
def stock_clear_cache_on_click(_nclicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    stock.clear_cached_files()
    del stock_cache[symbol]
    return 1

@app.callback(Output('stock-projection-output-table', 'children'),
              [Input('submit-button', 'n_clicks'),
                Input('stock-projection-table-nyear-input', 'value'),
                Input('stock-projection-table-eps-growth-rate-input', 'value'),
                Input('stock-projection-table-target-yield-input', 'value'),
                Input('stock-projection-table-target-pe-input', 'value'),
                Input('stock-projection-table-expected-dividends-input', 'value'),
                Input('stock-projection-table-projected-dividends-growth-input', 'value'),
                ],
              [ State('stock-symbol-input', 'value')])
def stock_projection_input_table_on_stock_update(n_clicks,
                                                 n_years,
                                                 estimated_growth,
                                                 target_yield,
                                                 target_pe,
                                                 expected_dividends,
                                                 projected_dividends_growth,
                                                 symbol):

    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    stock.n_projection_years = int(n_years)
    stock.estimated_growth = float(estimated_growth) / 100.
    stock.target_yield = float(target_yield) / 100.
    stock.target_pe = float(target_pe)
    stock.expected_dividends = float(expected_dividends)
    stock.projected_dividends_growth = float(projected_dividends_growth) / 100.
    rows = []

    rows.append(html.Tr([html.Th("Projected price"), html.Td(round(stock.price_projection,2))]))
    rows.append(html.Tr([html.Th("Projected Total Dividends"), html.Td(round(stock.projected_dividend_earnings,2))]))
    rows.append(html.Tr([html.Th("Target Price"), html.Td(round(stock.target_price,2))]))
    rows.append(html.Tr([html.Th("Current Price"), html.Td(round(stock.current_price,2))]))
    # rows.append(html.Tr([html.Th("dividend"), html.Td(stock.projected_dividends_growth)]))
    return rows

@app.callback(Output('stock-projection-input-table', 'children'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def stock_projection_input_table_on_stock_update(n_clicks, symbol):

    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock

    rows = []
    default_input_kwargs = {"type" : "number",
                            "inputmode" : "numeric",
                            }

    n_years_input = dcc.Input(id='stock-projection-table-nyear-input',
                              value=stock.n_projection_years,
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Projection years"), html.Td(n_years_input)]))

    eps_growth_input = dcc.Input(id='stock-projection-table-eps-growth-rate-input',
                                               value=round(stock.estimated_growth * 100.,2),
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected EPS growth %"), html.Td(eps_growth_input)]))

    target_yield = dcc.Input(id='stock-projection-table-target-yield-input',
                                               value=round(stock.target_yield * 100.,2),
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Target yield %"), html.Td(target_yield)]))

    target_pe = dcc.Input(id='stock-projection-table-target-pe-input',
                                               value=round(stock.target_pe,1),
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Target p/e"), html.Td(target_pe)]))

    expected_dividends = dcc.Input(id='stock-projection-table-expected-dividends-input',
                                                   value=round(stock.expected_dividends,2),
                                                   **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected dividends %s" % stock.currency), html.Td(expected_dividends)]))

    projected_dividends_growth = dcc.Input(id='stock-projection-table-projected-dividends-growth-input',
                                                   value=round(stock.projected_dividends_growth * 100. ,2),
                                                   **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected dividends growth %"), html.Td(projected_dividends_growth)]))

    return rows

@app.callback(Output('stock-ratios-summary-table', 'children'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def update_stock_ratios_summary_table(n_clicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    desired_keys= [ 'book-value-per-share-%s' % stock.currency,
                        'earnings-per-share-%s' % stock.currency,
                        'revenue-per-share-%s' % stock.currency,
                        'operating-cashflow-per-share-%s' % stock.currency,
                        'shares',
                        'return-on-invested-capital',
                        'return-on-equity',
                        'long-term-debt',
                        'debt-equity',
                      ]

    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table(stock.ratios[keys], n_years=8)

@app.callback(Output('stock-ratios-table', 'children'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def update_stock_ratios_table(n_clicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock

    desired_keys= [ 'earnings-per-share-%s' % stock.currency,
                    'dividends-%s' % stock.currency,
                    'book-value-per-share-%s' % stock.currency,
                    'free-cash-flow-per-share-%s' % stock.currency,
                    'operating-cash-flow-growth-yoy',
                    'free-cash-flow-growth-yoy',
                    'shares',
                    'operating-cash-flow-%s' % stock.currency,
                    'free-cash-flow-%s' % stock.currency,
                    'working-capital-%s' % stock.currency,
                    'net-income-%s' % stock.currency,
                    'revenue-%s' % stock.currency,
                    'return-on-invested-capital',
                    'return-on-equity',
                    'debt-equity',
                    'long-term-debt']
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table(stock.ratios[keys])

def fundamentals_to_table(df,n_years=99):
    #
    # [print(s.strftime("%m-%Y")) for s in df.index)]
    n_years = min(len(df.index), n_years)
    header = [ html.Tr([ html.Th('Date') ] + list(reversed([html.Th(s.strftime("%m-%Y")) for s in df.index]))[:n_years])]
    body = []
    def formated_value(df, col, iloc=0, header=False):
        output_value = df[col].iloc[iloc]
        output_header = col
        try:
            if np.fabs(df[col].iloc[0]) > 1.e6:
                output_value = output_value / 1.e6
                output_header = col + " (mil)"
        except ValueError:
            pass
        try:
            if int(output_value) == float(output_value):
                decimals = 0
            else:
                decimals = 2 # Assumes 2 decimal places for money
            output_value = '{0:.{1}f}'.format(output_value, decimals)
        except ValueError:
            pass
        if header:
            return output_header
        return output_value

    for key in list(df):

        body.append(html.Tr([html.Th(formated_value(df, key, header=True))] + list(reversed([ html.Td(formated_value(df, key, iloc=i)) for i in range(len(df))]))[:n_years] ) )
    return header + body

@app.callback(Output('stock-company-name-label', 'children'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def onsumbit_stock_company_name_label(n_clicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    return  u'{name}'.format(name=stock.company_name)

@app.callback(Output('stock-rule1-summary-table', 'children'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def onsumbit_stock_rule1_summary_table(n_clicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    return  [html.Tr([html.Th(s[0]), html.Td(s[1])]) for s in stock.get_summary_info()]

@app.callback(Output('stock-rule1-growth-plot', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def update_growth_rate_graph(n_clicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    label_map = {'earnings-ps-growth' : "Earnings per share",
                 'book-value-ps-growth' : "Book value per share",
                 'revenue-ps-growth' : "Revenue per share",
                 'operating-cashflow-ps-growth' : "Operating Cashflow per share"}

    growth_keys = ['earnings-ps-growth',
                   'book-value-ps-growth',
                   'revenue-ps-growth',
                   'operating-cashflow-ps-growth']

    data = []
    for key in growth_keys:
        data.append(go.Scatter(
                    x=list(stock.ratios[key].index),
                    y=stock.ratios[key] * 100,
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='line',
                    name=label_map[key],
                    marker={
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                   ))

    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': "Date",
                'type': 'date'
            },
            yaxis={
                'title': "relative change (%)",
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
            hovermode='closest',
            legend=dict(
                            x=0.1,
                            y=1,
                            traceorder='normal',
                            font=dict(
                                family='sans-serif',
                                size=12,
                                color='#000'
                            ),
                            bgcolor='rgba(0,0,0,0)'
         )

        ),

    }

@app.callback(Output('stock-historic-closing-price-plot', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [ State('stock-symbol-input', 'value')])
def update_growth_rate_graph(n_clicks, symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    if symbol not in stock_cache:
        stock_cache[symbol] = stock
    data = []
    data.append(go.Scatter(
                x=list(stock.historic_prices.index),
                y=stock.historic_prices['Close'],
                # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                mode='line',
                name="closing",
                marker={
                    'size': 5,
                    'opacity': 0.5,
                    'line': {'width': 0.5, 'color': 'white'}
                }
               ))
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': "Date",
                'type': 'date'
            },
            yaxis={
                'title': "closing price (%s)" % stock.currency,
                'type': 'linear'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 40},
            hovermode='closest',
            legend=dict(
                            x=0.1,
                            y=1,
                            traceorder='normal',
                            font=dict(
                                family='sans-serif',
                                size=12,
                                color='#000'
                            ),
                            bgcolor='rgba(0,0,0,0)'
         )

        ),
    }
