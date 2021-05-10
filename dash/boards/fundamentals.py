import dash
import json
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.server import get_aws_auth, decode_access_token
from decimal import Decimal

import numpy as np
import pandas as pd

from dash.stock import Stock
from dash.userInfo import UserInfo

from ..app import app
from ..app import stock_cache
def get_layout(token, company_name):
    default_input_kwargs = {"type" : "number",
                            "inputMode" : "numeric",
                            }
    stock = stock_cache.get(company_name, Stock(company_name))
    userInfo = UserInfo(token['username'])
    if company_name not in stock_cache:
        stock_cache[company_name] = stock
    try:
        stock_projection_input_table_output, stock_projection_output_table_rows = stock_projection_input_table_on_stock_update(userInfo, stock)
    except Exception as e:
        print(e)
        return html.Div([
            html.Div(id='fundamental-redirect'),
            html.Div(
                [dcc.Input(id='stock-symbol-input', type="text", value=company_name),
                 html.Button(id='submit-button', children='Submit', style={'backround' : 'white'})],
                style={'width': '49%', 'display': 'inline-block'}
            ),html.Div("No ticker found. Please check the ticker symbol at Morningstar.com")
            ],style={'position': 'sticky', 'top' : '90px', 'background': 'white', 'zIndex':'200'}
        )

    stock_company_name_output = onsumbit_stock_company_name_label(stock)
    stock_rule1_summary_table_output = onsumbit_stock_rule1_summary_table(stock)
    stock_pe_table_output = onsumbit_stock_pe_table(stock)
    growth_rate_graph = update_growth_rate_graph(stock)
    growth_table = update_stock_ratios_table(stock)
    returns_graph = update_returns_graph(stock)
    returns_table = update_stock_returns_table(stock)
    debt_graph = update_debt_graph(stock)
    debt_table = update_stock_debt_table(stock)
    margins_graph = update_margins_graph(stock)
    margins_table = update_stock_margins_table(stock)
    p_e_graph_output = update_p_e_graph(stock)
    price_graph_output = update_price_graph(stock)
    owner_earning_table = update_owner_earning_table(stock)
    owner_earning_table_2 = update_owner_earning_table_2(stock)
    owner_earning_calculator_table_output = owner_earning_calculator_table_update(stock)
    layout = html.Div([
        html.Div([
            html.Div(
                [dcc.Input(id='stock-symbol-input', type="text", value=company_name),
                 html.Button(id='submit-button', children='Submit', style={'backround' : 'white'})],
                style={'width': '49%', 'display': 'inline-block'}
            ),
            html.Div(
                [html.Div(id='stock-company-name-label', children=stock_company_name_output, style={'fontSize': 14})],
                style={'width': '49%', 'display': 'inline-block', }
            ),
            ],style={'position': 'sticky', 'top' : '90px', 'background': 'white', 'zIndex':'200'}
        ),
        html.Div(id='fundamental-redirect'),
        html.H1("Growth"),
        html.Div(
           html.Table(id='stock-rule1-summary-table', children=stock_rule1_summary_table_output),
           style={'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),
	html.Div(
            [
             
            ],
            style={'width': '18%',
                   'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),         
        html.Div(
            [ 
               html.Div([html.Table(id='stock-errors-table'),
                        #html.Table(id='stock-ratios-summary-table'),
                        dcc.Graph(id='stock-rule1-growth-plot', figure=growth_rate_graph)
                       ]),
                      
            ],
            style={'width': '75%', 'display': 'inline-block'}
        ),
         html.Div([html.Table(id='stock-growth-table-row', children=growth_table)], style={'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}),
         html.H1("Return on"),
          html.Div(style={'width': '18%',
                   'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),         
        html.Div(
            [dcc.Graph(id='stock-returns-plot', figure=returns_graph)],
            style={'width': '75%', 'display': 'inline-block'}
        ),
         html.Div([html.Table(id='stock-returns-table-row', children=returns_table)], style={'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}),
        html.H1("Debt"),
        html.Div(
            [
             
            ],
            style={'width': '18%',
                   'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),         
        html.Div([dcc.Graph(id='stock-debt-plot', figure=debt_graph)],
            style={'width': '75%', 'display': 'inline-block'}
        ),
         html.Div([html.Table(id='stock-debt-table-row', children=debt_table)], style={'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}),
        html.H1("Margins"),
        html.Div(style={'width': '18%',
                   'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),         
        html.Div([dcc.Graph(id='stock-margins-plot', figure=margins_graph)],
            style={'width': '75%', 'display': 'inline-block'}
        ),
        html.Div([html.Table(id='stock-margins-table-row', children=margins_table)], style={'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}),
 	html.H1("Discounted Cashflow"),
        html.Div(
            [
             html.Table(id='stock-discounted-cashflow-table'),
            ],
            style={'width': '18%',
                   'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),         
        html.Div([dcc.Graph(id='stock-p-e-plot', figure=p_e_graph_output),
                 dcc.Graph(id='stock-discounted-cashflow-plot', figure=price_graph_output)
                  ],
            style={'width': '75%', 'display': 'inline-block'}
        ), 
        html.Div(  
            html.Table(html.Tr([
                  html.Td(
                      html.Table(id='stock-pe-table', children=stock_pe_table_output),
                      style={'verticalAlign': 'top'}
                  ),
                  html.Td(
                      html.Table(id='stock-projection-input-table-row',
			children=stock_projection_input_table_output),
                      style={'verticalAlign': 'top'}
                  ),
                  html.Td(
                      html.Table(id='stock-projection-output-table', children=stock_projection_output_table_rows),
                      style={'verticalAlign': 'top'}
                  )
                  ])
            ),
            style={
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),
        html.H1("Owner Earnings"),
        html.Div([
                  html.Table(id='owner-earning-table', children=owner_earning_table),
                  html.Table(id='owner-earning-table_2', children=owner_earning_table_2)],
            style={'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),
        html.H1("Owner Earnings Caclulator"),
        html.Div(
            style={'width': '18%',
                   'display': 'inline-block',
                   'vertical-align':'top',
                   'padding': '10px', 'margin-right':'10px', 'overflow-x':'auto'}
        ),         
        html.Div([
                  html.Table(id='owner-earning-caclulator-table-row',
			children=owner_earning_calculator_table_output)
                  ],
            style={'width': '75%', 'display': 'inline-block'}
        )
    ])
    return layout
@app.callback(Output('fundamental-redirect', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('stock-symbol-input', 'value')])
def on_stock_update(n_clicks,
                    symbol):
    #print('on_stock_update n_clicks'+str(n_clicks))
    if not n_clicks:
        return ''
    return dcc.Location(pathname='/Prod/fundamentals/'+symbol.upper(), id='company_redirect')

@app.callback([Output('add-to-watch-list-button', 'children'),
               Output('add-to-watchlist-td', 'children'),
               Output('add-watchlist-toast', 'is_open')
              ],
              [Input('add-to-watch-list-button', 'n_clicks')],
              [State('add-to-watch-list-button', 'children'),
               State('add-to-watchlist-td', 'children'),
               State('stock-projection-table-nyear-input', 'value'),
               State('stock-projection-table-calculated_eps-input', 'value'),
               State('stock-projection-table-eps-growth-rate-input', 'value'),
               State('stock-projection-table-target-yield-input', 'value'),
               State('stock-projection-table-target-pe-input', 'value'),
               State('stock-projection-table-expected-dividends-input', 'value'),
               State('stock-projection-table-projected-dividends-growth-input', 'value'),
               State('curent-target-price', 'value'),
               State('projected-price-input', 'value'),
               State('projected-total-dividends-input', 'value'),
               State('target-price-input', 'value'),
               State('curent-price-input', 'value'),
               State('stock-symbol-input', 'value')
                ]
)
def on_add_to_watch_list(n_clicks,
                         curent_button_text,
                         curent_td_text,
                         n_years,
                         calculated_eps,
                         estimated_growth,
                         target_yield,
                         target_pe,
                         expected_dividends,
                         projected_dividends_growth,
                         current_target_price,
                         projected_price,
                         projected_total_dividends,
                         target_price,
                         curent_price,
                         symbol):
    if n_clicks:
        #print('on_add_to_watch_list n_clicks'+str(n_clicks))
        token = decode_access_token(app.server)
        userInfo = UserInfo(token['username'])
        stock = stock_cache.get(symbol, Stock(symbol))
        #stock.n_projection_years = int(n_years)
        #stock.calculated_eps = float(calculated_eps)
        #stock.estimated_growth = float(estimated_growth) / 100.
        #stock.target_yield = float(target_yield) / 100.
        #stock.target_pe = float(target_pe)
        #stock.expected_dividends = float(expected_dividends)
        #stock.projected_dividends_growth = float(projected_dividends_growth) / 100.
        #print(projected_price)
        watch_list_item = {
            'projection_years': stock.n_projection_years,
            'excpected_eps': round(stock.estimated_growth * 100.,2),
            'target_yield': round(stock.target_yield * 100.,2),
            'target_p_e': round(stock.target_pe,1),
            'expected_dividends': round(stock.expected_dividends,2),
            'expected_dividends_growth': round(stock.projected_dividends_growth * 100. ,2),
            #'projected_price': projected_price,
            #'projected_total_dividends': projected_total_dividends,
            #'target_price':  target_price,
            #'current_price':  current_target_price,
            'alert_price':  round(stock.target_price,2)
            }
        #print(current_target_price)
        #print(token['username'] + ' ' + symbol + ' ' + str(type(stock.ratios["earnings-per-share-%s" % stock.currency].iloc[-1])) + ' ' + str(type(max(stock.ratios["pe"]))))
        watch_list_item = {
                #'email': self.email,
                'company': symbol,
                'company_name': stock.company_name,
                'currency':  stock.currency,
                'projection_years':  n_years,
                'calculated_eps': Decimal(str(calculated_eps)),
                'excpected_eps':  estimated_growth,
                'target_yield':  target_yield,
                'target_p_e':  target_pe,
                'expected_dividends':  Decimal(str(expected_dividends)),
                'expected_dividends_growth':  projected_dividends_growth
            }
        if current_target_price != 'no alert defined':
            watch_list_item['alert_price'] = Decimal(str(current_target_price))
        #min_pe = round(stock.ratios["pe"].min(), 2)
        #if not pd.isna(min_pe):
        #    watch_list_item['minPE'] = Decimal(str(min_pe))
        #max_pe = round(stock.ratios["pe"].max(), 2)
        #if not pd.isna(max_pe):
        #    watch_list_item['maxPE'] = Decimal(str(max_pe))
        #pe75 = round(stock.ratios["pe"].quantile(q=0.75, interpolation='linear'), 2)
        #if not pd.isna(pe75):
        #    watch_list_item['PE75'] = Decimal(str(pe75))
        epsTTM = stock.ratios["earnings-per-share-%s" % stock.currency].iloc[-1]
        if not pd.isna(epsTTM):
            watch_list_item['epsTTM'] = Decimal(str(epsTTM))
        average_growth = round(100 * stock.estimated_growth, 2)
        if not pd.isna(average_growth):
            watch_list_item['average_growth'] = Decimal(str(average_growth))
        estimated_free_cash_flow_growth = round(100 * stock.estimated_free_cash_flow_growth, 2)
        if not pd.isna(average_growth):
            watch_list_item['estimated_free_cash_flow_growth'] = Decimal(str(estimated_free_cash_flow_growth))
        if not pd.isna(target_price):
            watch_list_item['target_price'] = Decimal(str(target_price))
        if not pd.isna(curent_price):
            watch_list_item['current_price'] = Decimal(str(curent_price))
        if projected_price:
            watch_list_item['projected_price'] = Decimal(str(projected_price))
        if projected_total_dividends:
            watch_list_item['projected_total_dividends'] = Decimal(str(projected_total_dividends))
        if 'target_price' in watch_list_item and 'current_price' in watch_list_item:
            watch_list_item['delta'] = Decimal(str(round((curent_price - target_price)/curent_price,2)))
        #print(watch_list_item)
        userInfo.put_company_to_watch_list(watch_list_item)
        settings = userInfo.get_settings()
        email = settings['email']
        userInfo.put_company_to_watch_list(watch_list_item)
        #userInfo.put_company_to_watch_list( symbol, n_years, estimated_growth, target_yield, target_pe, expected_dividends, expected_dividends_growth, projected_price, projected_total_dividends, target_pe, target_pe, target_pe)
        #print(token['username'] + ' ' + symbol + ' ' + str(n_years) + ' ' + str(estimated_growth))
        return "Update on watch list", "Company is on your watchlist", True
    return curent_button_text, curent_td_text, False
@app.callback([
                Output('curent-target-price', 'value'),
                Output('set-alert-price-toast', 'is_open'),
                Output('set-alert-price-not-in-watchlist-toast', 'is_open'),
              ],
              [Input('set-target-price-button', 'n_clicks')],
              [
                State('curent-target-price', 'value'),
                State('stock-set-target-price-input', 'value'),
                State('stock-symbol-input', 'value')
              ]
)
def set_target_price(n_clicks,
                        curent_value,
			target_price,
                        symbol):
    #print('set_target_price n_clicks'+str(n_clicks))
    if not n_clicks:    
        return curent_value, False, False
    token = decode_access_token(app.server)
    userInfo = UserInfo(token['username'])
    watch_list_item = userInfo.get_company_from_watch_list(symbol)
    set_watchlist = False 
    if watch_list_item:
        set_watchlist = True
        if target_price != 'Update on watch list':
            watch_list_item['alert_price'] = Decimal(str(target_price))
        userInfo.put_company_to_watch_list(watch_list_item)
    return target_price, set_watchlist, not set_watchlist
def owner_earning_calculator_table_update(stock):
    #print('owner_earning_calculator_table_update')

    rows = []
    default_input_kwargs = {"type" : "text",
                            "inputMode" : "numeric",
                            }
    net_income_val = 0
    if "net-income" in stock.cashflow:
        net_income_val = stock.cashflow['net-income'].iloc[-1]

    earning_calculator_input = dcc.Input(id='earning-calculator-input',
                              value=formated_number(net_income_val),
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Earning"), html.Td(earning_calculator_input)]))

    depreciation_amortization_val = 0
    if "depreciation-amortization" in stock.cashflow:
        depreciation_amortization_val = stock.cashflow['depreciation-amortization'].iloc[-1]

    depreciation_calculator_input = dcc.Input(id='depreciation-calculator-input',
                              value=formated_number(depreciation_amortization_val),
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Depreciation, depletion and amort"), html.Td(depreciation_calculator_input)]))

    current_assets_val = 0
    if "total-current-assets" in stock.ratios:
        current_assets_val = stock.balancesheet["total-current-assets"].iloc[-1]
    current_assets_calculator_input = dcc.Input(id='current-assets-calculator-input',
                              value=formated_number(current_assets_val),
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Current assets"), html.Td(current_assets_calculator_input)]))

    current_liabilities_val = 0
    if "total-current-liabilities" in stock.ratios:
        current_liabilities_val = stock.balancesheet["total-current-liabilities"].iloc[-1]

    current_liabilities_calculator_input = dcc.Input(id='current-liabilities-calculator-input',
                              value=formated_number(current_liabilities_val),
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Current liabilities"), html.Td(current_liabilities_calculator_input)]))

    other_working_capital_val = 0
    if "other-working-capital" in stock.cashflow:
        other_working_capital_val = stock.cashflow["other-working-capital"].iloc[-1]

    working_capital_calculator_input = dcc.Input(id='working-capital-calculator-input',
                              value=formated_number(other_working_capital_val),
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Working capital"), html.Td(working_capital_calculator_input)]))
    
    other_non_cash_items_val = 0
    if "other-non-cash-items" in stock.cashflow:
        other_non_cash_items_val = stock.cashflow["other-non-cash-items"].iloc[-1]

    other_non_cash_items_calculator_input = dcc.Input(id='other-non-cash-items-calculator-input',
                              value=formated_number(other_non_cash_items_val),
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Other non cash items"), html.Td(other_non_cash_items_calculator_input)]))


    owner_earning_calculator_result = dcc.Input(id='owner-earning-calculator-result',disabled=True,
            style={'border': 'hidden'}, **default_input_kwargs)
    rows.append(html.Tr([html.Th("Owner	earnings"), html.Td(owner_earning_calculator_result)]))
   
    return rows
@app.callback(Output('owner-earning-calculator-result', 'value'),
              [Input('earning-calculator-input', 'value'),
                Input('depreciation-calculator-input', 'value'),
                Input('current-assets-calculator-input', 'value'),
                Input('current-liabilities-calculator-input', 'value'),
                Input('working-capital-calculator-input', 'value'),
                Input('other-non-cash-items-calculator-input', 'value'),
                ])
def calculator_inputs(earning_calculator_input,
                                                 depreciation_calculator_input,
                                                 current_assets_calculator_input,
                                                 current_liabilities_calculator_input,
                                                 working_capital_calculator_input,
                                                 other_non_cash_items_calculator_input):
    #print('calculator_inputs')

    return formated_number(str_to_decimal(earning_calculator_input) + str_to_decimal(depreciation_calculator_input) + str_to_decimal(current_assets_calculator_input) + str_to_decimal(current_liabilities_calculator_input) + str_to_decimal(working_capital_calculator_input) + str_to_decimal(other_non_cash_items_calculator_input))
def formated_number(n):
    return '{:,.2f}'.format(n).replace('.00', '').replace('nan', '')
def str_to_decimal(s):
    return Decimal(s.replace(',', ''))
def stock_projection_input_table_on_stock_update(userInfo, stock):
    #print('stock_projection_input_table_on_stock_update')

    rows = []
    default_input_kwargs = {"type" : "number",
                            "inputMode" : "numeric",
                            }
    watch_list_item = {
            'projection_years': stock.n_projection_years,
            'excpected_eps': round(stock.estimated_growth * 100.,2),
            'target_yield': round(stock.target_yield * 100.,2),
            'target_p_e': round(stock.target_pe,1),
            'expected_dividends': round(stock.expected_dividends,2),
            'expected_dividends_growth': round(stock.projected_dividends_growth * 100. ,2),
            #'projected_price': projected_price,
            #'projected_total_dividends': projected_total_dividends,
            #'target_price':  target_price,
            #'current_price':  current_target_price,
            'alert_price':  round(stock.target_price,2)
            }
    watch_list_item = userInfo.get_company_from_watch_list(stock.symbol)
    is_in_watch_list = True
    if not watch_list_item:
        is_in_watch_list = False
        watch_list_item = {
                'projection_years': stock.n_projection_years,
                'excpected_eps': round(stock.estimated_growth * 100.,2),
                'target_yield': round(stock.target_yield * 100.,2),
                'target_p_e': round(stock.target_pe,1),
                'expected_dividends': round(stock.expected_dividends,2),
                'expected_dividends_growth': round(stock.projected_dividends_growth * 100. ,2),
                #'projected_total_dividends': projected_total_dividends,
                #'target_price':  target_price,
                #'current_price':  current_target_price
            }
    if 'alert_price' not in watch_list_item:
        watch_list_item['alert_price'] = "no alert defined"
    if 'calculated_eps' not in watch_list_item:
        watch_list_item['calculated_eps'] = round(stock.calculated_eps,2)
    #print(watch_list_item)
    #print("Alert price "+str(watch_list_item['alert_price']))
    n_years_input = dcc.Input(id='stock-projection-table-nyear-input',
                              value=watch_list_item['projection_years'],
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Projection years"), html.Td(n_years_input)]))
    try:
        value = watch_list_item['calculated_eps']
    except Exception as e:
        print("Error:" + str(e)) 
        raise
        value = 0
    calculated_eps_input = dcc.Input(id='stock-projection-table-calculated_eps-input',
                                 value=value,
                                 **default_input_kwargs)
    rows.append(html.Tr([html.Th("Calculated EPS"), html.Td(calculated_eps_input)]))
    try:
        value = watch_list_item['excpected_eps']
    except Exception as e:
        print("Error:" + str(e)) 
        raise
        value = 0
    eps_growth_input = dcc.Input(id='stock-projection-table-eps-growth-rate-input',
                                 value=value,
                                 **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected EPS growth %"), html.Td(eps_growth_input)]))

    target_yield = dcc.Input(id='stock-projection-table-target-yield-input',
                                               value=watch_list_item['target_yield'],
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Target yield %"), html.Td(target_yield)]))

    try:
        value = watch_list_item['target_p_e']
    except Exception as e:
        print("Error" + str(e))
        raise
        value = 0
    target_pe = dcc.Input(id='stock-projection-table-target-pe-input',
                                               value=value,
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Target p/e"), html.Td(target_pe)]))

    try:
        value = watch_list_item['expected_dividends']
    except Exception as e:
        print("Error:" + str(e))
        raise
        value = 0
    expected_dividends = dcc.Input(id='stock-projection-table-expected-dividends-input',
                                                   value=value,
                                                   **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected dividends %s" % stock.currency), html.Td(expected_dividends)]))

    try:
        value = watch_list_item['expected_dividends_growth']
    except Exception as e:
        print("Error:" + str(e))
        raise
        value = 0
    projected_dividends_growth = dcc.Input(id='stock-projection-table-projected-dividends-growth-input',
                                                   value=value,
                                                   **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected dividends growth %"), html.Td(projected_dividends_growth)]))

    projected_price = dcc.Input(id='projected-price-input',disabled=True,
            style={'border': 'hidden'},
                              **default_input_kwargs)
    projected_total_dividends = dcc.Input(id='projected-total-dividends-input',disabled=True,
            style={'border': 'hidden'},
                              **default_input_kwargs)
    target_price = dcc.Input(id='target-price-input',disabled=True,
            style={'border': 'hidden'},
                              **default_input_kwargs)
    curent_price = dcc.Input(id='curent-price-input',disabled=True,
            style={'border': 'hidden'},
                              **default_input_kwargs)
    add_to_watchlist_text = 'Add to watch list'
    add_to_watchlist_td = ''
    if is_in_watch_list:
        add_to_watchlist_td = 'Company is on your watchlist'
        add_to_watchlist_text = 'Update on watch list'
    add_to_watch_list_button = html.Div([
              html.Button(id='add-to-watch-list-button', children=add_to_watchlist_text, style={'backround' : 'white'}),
              dbc.Toast([html.P(stock.company_name + "(" + stock.symbol +") has been added to watchlist", className="mb-0")], id='add-watchlist-toast', header="Completed", duration=4000, style={'opacity' : '0.5'})
            ])
    alert_price = dcc.Input(id='stock-set-target-price-input', value=round(stock.target_price,2), **default_input_kwargs)
    set_target_price_button = html.Div([
              html.Button(id='set-target-price-button', children='Set alert price', style={'backround' : 'white'}),
              dbc.Toast([html.P("Alert price has been added to watchlist in " + stock.company_name + "(" + stock.symbol +")", className="mb-0")], id='set-alert-price-toast', header="Completed", duration=4000, style={'opacity' : '0.5'}),
              dbc.Toast([html.P("Alert price is set but " + stock.company_name + "(" + stock.symbol +") is not added to watchlist ", className="mb-0")], id='set-alert-price-not-in-watchlist-toast', header="Completed", duration=4000, style={'opacity' : '0.5'})
         ])
 
    curent_target_price = dcc.Input(id='curent-target-price', value=watch_list_item['alert_price'],disabled=True,
            style={'border': 'hidden'})
    stock_projection_output_table_rows = [
        html.Tr([html.Th(add_to_watch_list_button), html.Td(html.Div(id='add-to-watchlist-td', children=add_to_watchlist_td))]),
        html.Tr([html.Th(set_target_price_button), html.Td(alert_price)]),
        html.Tr([html.Th("Current alert price"), html.Td(curent_target_price)]),
        html.Tr([html.Th("Projected price"), html.Td(projected_price)]),
        html.Tr([html.Th("Projected Total Dividends"), html.Td(projected_total_dividends)]),
        html.Tr([html.Th("Target Price"), html.Td(target_price)]),
        html.Tr([html.Th("Current Price"), html.Td(curent_price)])
    ]

   
    return rows, stock_projection_output_table_rows

def update_stock_ratios_table(stock):
    #print('update_stock_ratios_table')
    desired_keys= [ 'book-value-per-share-%s' % stock.currency,
                    'earnings-per-share-%s' % stock.currency,
                    'revenue-per-share-%s' % stock.currency,
                    'operating-cashflow-per-share-%s' % stock.currency,
                    'free-cash-flow-per-share-%s' % stock.currency,
                    'shares',
                      ]
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table_old(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]

def update_stock_returns_table(stock):
    #print('update_stock_returns_table')
    desired_keys= ['return-on-assets',
                   'return-on-equity',
                   'return-on-invested-capital']
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table_old(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]

def update_stock_debt_table(stock):
    #print('update_stock_debt_table')
    desired_keys= ['total-debt-%s' % stock.currency,
                   #'total-debt-per-share-%s' % stock.currency,
                   'debt-per-free-cashflow',
                   'debt-per-total-cash',
                   'debt-per-earnings',
                   'debt-per-asset',
                   'debt-equity']
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_5years_to_table(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]


def update_stock_margins_table(stock):
    #print('update_stock_margins_table')
    desired_keys= ['gross-margin-perc',
                   'operating-margin-perc',
                   'ebt-margin',
                    'net-margin'
                  ]
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table_old(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]

def update_owner_earning_table(stock):
    #print('update_owner_earning_table')
    desired_keys= ['devidends-%s' % stock.currency,
                   'operating-cashflow-%s' % stock.currency,
                   'operating-cashflow-growth-yc',
                    'free-cash-flow-growth-yoy',
                    'gross-property-plant-and-equipment',
                    'net-property-plant-and-equipment',
                    'cap-ex-as-a-of-sales',
                    'free-cash-flow-sales',
                    'free-cash-flow-net-income'
                  ]
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table_old(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]

def update_owner_earning_table_2(stock):
    #print('update_owner_earning_table')
    desired_keys= [
                    'net-income',
                    'depreciation-amortization',
                    'total-current-assets ',
                    'total-current-liabilities ',
                    'other-working-capital',
                    'other-non-cash-items'
                  ]
    if 'net-income' in stock.cashflow:
        stock.ratios['net-income']=stock.cashflow['net-income']
    if 'depreciation-amortization' in stock.cashflow:
        stock.ratios['depreciation-amortization']=stock.cashflow['depreciation-amortization']
    if 'other-working-capital' in stock.cashflow:
        stock.ratios['other-working-capital']=stock.cashflow['other-working-capital']
    if 'other-non-cash-items' in stock.cashflow:
        stock.ratios['other-non-cash-items']=stock.cashflow['other-non-cash-items']
    if 'total-current-assets' in stock.balancesheet:
        stock.ratios['total-current-assets ']=stock.balancesheet['total-current-assets']
    if 'total-current-liabilities' in stock.balancesheet:
        stock.ratios['total-current-liabilities ']=stock.balancesheet['total-current-liabilities']
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_5years_to_table(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]
def fundamentals_to_table_old(df,n_years=99):
    #print('fundamentals_to_table')
    #
    # [print(s.strftime("%m-%Y")) for s in df.index)]
    n_years = min(len(df.index), n_years)
    header = [ html.Tr([ html.Th('Date') ] +[html.Th()] +  list([html.Th(s.strftime("%m-%Y")) for s in df.index])[:n_years])]
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
        except OverflowError:
            pass
        try:
            output_value =  formated_number(output_value)
        except ValueError:
            pass
        except OverflowError:
            pass
        if header:
            return output_header
        return output_value

    for key in list(df):

        body.append(html.Tr([html.Th(formated_value(df, key, header=True))] +[html.Td()] + list([ html.Td(formated_value(df, key, iloc=i)) for i in range(len(df))])[:n_years] ) )
    return header + body
def fundamentals_5years_to_table(df):
    #print('fundamentals_to_table')
    #
    # [print(s.strftime("%m-%Y")) for s in df.index)]
    #n_years = min(len(df.index), n_years)
    header = [ html.Tr([ html.Th('Date') ] +[html.Th()] +  list([html.Th(s.strftime("%m-%Y")) for s in df.index])[5:10])]
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
        except OverflowError:
            pass
        try:
            output_value =  formated_number(output_value)
        except ValueError:
            pass
        except OverflowError:
            pass
        if header:
            return output_header
        return output_value

    for key in list(df):

        body.append(html.Tr([html.Th(formated_value(df, key, header=True))] +[html.Td()] + list([ html.Td(formated_value(df, key, iloc=i)) for i in range(len(df))])[5:10] ) )
    return header + body

def onsumbit_stock_company_name_label(stock):
    #print('onsumbit_stock_company_name_label')
    return  u'{name}'.format(name=stock.company_name)

def onsumbit_stock_rule1_summary_table(stock):
    #print('onsumbit_stock_rule1_summary_table')
    childTHs = []
    childTDs = []
    for s in stock.get_summary_info():
        childTHs.append(html.Th(s[0])) 
        childTDs.append(html.Td(s[1]))
    return  [html.Tr([html.Th("Growth rates"), html.Td('%')]), html.Tr(childTHs), html.Tr(childTDs)]

def onsumbit_stock_pe_table(stock):
    rows = []
    summary_infos = [
                ("currency", stock.currency),
                ("eps TTM", stock.ratios["earnings-per-share-%s" % stock.currency].iloc[-1]),
                ("min p/e", round(stock.ratios["pe"].min(), 2)),
                ("max p/e", round(stock.ratios['pe'].max(), 2)),
                ("0.75 perc p/e", round(stock.ratios["pe"].quantile(q=0.75, interpolation='linear'), 2)),
                ("average growth", round(100 * stock.estimated_growth, 2)),
                ("average free cash flow growth", round(100 * stock.estimated_free_cash_flow_growth, 2))
    ]
    rows.append(html.Tr([html.Th("currency"), html.Td(dcc.Input(value=stock.currency, disabled=True,
            style={'border': 'hidden'} ))]))
    rows.append(html.Tr([html.Th("eps TTM"), html.Td(dcc.Input(value=stock.ratios["earnings-per-share-%s" % stock.currency].iloc[-1], disabled=True,
            style={'border': 'hidden'}) )]))
    rows.append(html.Tr([html.Th("min p/e"), html.Td(dcc.Input(value=round(stock.ratios["pe"].min(), 2), disabled=True,
            style={'border': 'hidden'} ))]))
    rows.append(html.Tr([html.Th("max p/e"), html.Td(dcc.Input(value=round(stock.ratios["pe"].max(), 2), disabled=True,
            style={'border': 'hidden'} ))]))
    rows.append(html.Tr([html.Th("0.75 perc p/e"), html.Td(dcc.Input(value=round(stock.ratios["pe"].quantile(q=0.75, interpolation='linear'), 2), disabled=True,
            style={'border': 'hidden'} ))]))
    rows.append(html.Tr([html.Th("average growth"), html.Td(dcc.Input(value=round(100 * stock.estimated_growth, 2), disabled=True,
            style={'border': 'hidden'} ))]))
    rows.append(html.Tr([html.Th("average free cash flow growth"), html.Td(dcc.Input(value=round(100 * stock.estimated_free_cash_flow_growth, 2), disabled=True,
            style={'border': 'hidden'} ))]))
    return  rows

def update_growth_rate_graph(stock):
    #print('update_growth_rate_graph')
    label_map = {'free-cash-flow-ps-growth':'Free cashflow per share', 'earnings-ps-growth' : "Earnings per share",
                 'book-value-ps-growth' : "Book value per share",
                 'revenue-ps-growth' : "Revenue per share",
                 'operating-cashflow-ps-growth' : "Operating Cashflow per share"}

    growth_keys = ['free-cash-flow-ps-growth',
                   'earnings-ps-growth',
                   'book-value-ps-growth',
                   'revenue-ps-growth',
                   'operating-cashflow-ps-growth']

    return create_graph_data(stock, label_map, growth_keys, "[%]", 100)
def update_returns_graph(stock):
    #print('update_returns_graph')
    label_map = {'return-on-assets' : "Return on Assets",
                 'return-on-equity' : "Return on Equity",
                 'return-on-invested-capital' : "Return on Invested Capital"}

    growth_keys = ['return-on-assets',
                   'return-on-equity',
                   'return-on-invested-capital']
    return create_graph_data(stock, label_map, growth_keys, "[%]", 1)

def update_debt_graph(stock):
    #print('update_debt_graph')
    label_map = {'debt-per-free-cashflow' : "Debt/free Cashflow",
                 'debt-per-total-cash' : "Debt/Total Cash",
                 'debt-per-earnings' : "Debt/earnings",
                 'debt-per-asset' : "Debt/Assets",
                 'debt-equity' : "Debt/Equity",
                 }

    growth_keys = ['debt-per-free-cashflow',
                   'debt-per-total-cash',
                   'debt-per-earnings',
                   'debt-per-asset',
                   'debt-equity'
                   ]

    return create_graph_data_5_years(stock, label_map, growth_keys, "[-]", 1)

def update_margins_graph(stock):
    #print('update_margins_graph')
    label_map = {'gross-margin-perc' : "Gross Margin %",
                 'operating-margin-perc' : "Operating Margin %",
                 'ebt-margin' : "EBT Margin",
                 'net-margin': "NET Margin %"
                 }

    growth_keys = ['gross-margin-perc',
                   'operating-margin-perc',
                   'ebt-margin',
                    'net-margin'
                  ]
    return create_graph_data(stock, label_map, growth_keys, "[%]")

def create_graph_data(stock, label_map, growth_keys, title, mult=1):
    data = []
    min_val = 0
    max_val = 0
    for key in growth_keys:
        if key in stock.ratios:
            #print(type(stock.ratios[key]))
            try:
                if min(stock.ratios[key] * mult) < min_val:
                    min_val = min(stock.ratios[key] * mult)
                if max(stock.ratios[key] * mult > max_val):
                    max_val = max(stock.ratios[key] * mult)
                data.append(go.Scatter(
                            x=list(stock.ratios[key].index),
                            y=stock.ratios[key] * mult,
                            # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                            mode='lines',
                            name=label_map[key],
                            marker={
                                'size': 15,
                                'opacity': 0.5,
                                'line': {'width': 0.5, 'color': 'white'}
                            }
                           ))
            except:
                pass
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': "Date",
                'type': 'date'
            },
            yaxis={
                'title': title,
                'type': 'linear',
                'range':[min_val, max_val]
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
def create_graph_data_5_years(stock, label_map, growth_keys, title, mult=1):
    data = []
    min_val = 0
    max_val = 0
    for key in growth_keys:
        if key in stock.ratios:
            #print(type(stock.ratios[key]))
            try:
                if min(stock.ratios[key] * mult) < min_val:
                    min_val = min(stock.ratios[key] * mult)
                if max(stock.ratios[key] * mult > max_val):
                    max_val = max(stock.ratios[key] * mult)
                data.append(go.Scatter(
                            x=list(stock.ratios[key].index)[5:10],
                            y=stock.ratios[key][5:10] * mult,
                            # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                            mode='lines',
                            name=label_map[key],
                            marker={
                                'size': 15,
                                'opacity': 0.5,
                                'line': {'width': 0.5, 'color': 'white'}
                            }
                           ))
            except:
                pass
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': "Date",
                'type': 'date'
            },
            yaxis={
                'title': title,
                'type': 'linear',
                'range':[min_val, max_val]
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
def update_p_e_graph(stock):
    #print('update_p_e_graph')
    data = []
    min_val = 0
    if min(stock.ratios["pe"]) < min_val:
        min_val = min(stock.ratios["pe"])
    max_val = max(stock.ratios["pe"])
    try:
        data.append(go.Scatter(
                    x=list(stock.ratios["pe"].index),
                    y=stock.ratios["pe"],
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='lines',
                    name="p/e",
                    marker={
                        'size': 5,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                   ))
        data.append(go.Scatter(
                    x=list(stock.ratios["pe"].index),
                    y=stock.ratios["min-pe"],
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='lines',
                    name="min p/e",
                    marker={
                        'size': 5,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    line= { 'color': 'green'}
                   ))
        data.append(go.Scatter(
                    x=list(stock.ratios["pe"].index),
                    y=stock.ratios["max-pe"],
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='lines',
                    name="max p/e",
                    marker={
                        'size': 5,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    line= { 'color': 'red'}
                   ))
        data.append(go.Scatter(
                    x=list(stock.ratios["pe"].index),
                    y=stock.ratios['0.75-perc-pe'],
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='lines',
                    name="0.75 perc p/e",
                    marker={
                        'size': 5,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    line= { 'color': 'orange'}
                   ))
    except:
        pass
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': "Date",
                'type': 'date'
            },
            yaxis={
                'title': "[-]",
                'type': 'linear',
                'range':[min_val, max_val]
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
def update_price_graph(stock):
    #print('update_price_graph')
    data = []
    try:
        data.append(go.Scatter(
                    x=list(stock.historic_prices.index),
                    y=stock.historic_prices['Close'],
                    # text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='lines',
                    name="closing",
                    marker={
                        'size': 5,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                   ))
    except:
        pass
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': "Date",
                'type': 'date'
            },
            yaxis={
                'title': "stock price [%s]" % stock.currency,
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
@app.callback([Output('projected-price-input', 'value'),
               Output('projected-total-dividends-input', 'value'),
               Output('target-price-input', 'value'),
               Output('curent-price-input', 'value')
              ],
              [Input('stock-projection-table-nyear-input', 'value'),
                Input('stock-projection-table-calculated_eps-input', 'value'),
                Input('stock-projection-table-eps-growth-rate-input', 'value'),
                Input('stock-projection-table-target-yield-input', 'value'),
                Input('stock-projection-table-target-pe-input', 'value'),
                Input('stock-projection-table-expected-dividends-input', 'value'),
                Input('stock-projection-table-projected-dividends-growth-input', 'value'),
                ],
               [ State('stock-symbol-input', 'value')])
def stock_projection_output_table_on_stock_update_inputs(n_years,
                                                 calculated_eps,
                                                 estimated_growth,
                                                 target_yield,
                                                 target_pe,
                                                 expected_dividends,
                                                 projected_dividends_growth,
                                                 symbol):
    #print('TTT_sstock_projection_output_table_on_stock_update')
    stock = stock_cache.get(symbol, Stock(symbol))
    try:
        if symbol not in stock_cache:
            stock_cache[symbol] = stock
        stock.n_projection_years = int(n_years)
        stock.estimated_growth = float(estimated_growth) / 100.
        stock.target_yield = float(target_yield) / 100.
        stock.target_pe = float(target_pe)
        stock.expected_dividends = float(expected_dividends)
        stock.projected_dividends_growth = float(projected_dividends_growth) / 100.
        stock.calculated_eps = float(calculated_eps)
    except Exception as e:
        print("Error" + str(e))
    return round(stock.price_projection,2), round(stock.projected_dividend_earnings,2), round(stock.target_price,2), round(stock.current_price,2)
