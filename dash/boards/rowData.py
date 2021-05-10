import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

import numpy as np

from dash.stock import Stock

from ..app import app
from ..app import stock_cache
def get_layout(company_name):
    layout = html.Div([
        html.Div([
            html.Div(
                [dcc.Input(id='stock-symbol-input-row', type="text", value=company_name),
                 html.Button(id='submit-button-row', n_clicks=0, children='Submit', style={'backround' : 'white'})],
                style={'width': '49%', 'display': 'inline-block'}
            ),
            html.Div(
                [html.Div(id='stock-company-name-label-row', style={'fontSize': 14})],
                style={'width': '49%', 'display': 'inline-block', }
            ),
            ],style={'position': 'sticky', 'top' : 1, 'background': 'white'}
        ),
        html.H1("Row Data"),
        html.Div([ html.Table(id='stock-ratios-table-row')],
                 style={'width': '65%', 'display': 'inline-block'}
        ),
    ])
    return layout

@app.callback([
			  Output('stock-ratios-table-row', 'children'),
			  Output('stock-company-name-label-row', 'children')
			  ],
              [Input('submit-button-row', 'n_clicks')
                ],
              [ State('stock-symbol-input-row', 'value')])
def on_stock_update(n_clicks,
                    symbol):
    stock = stock_cache.get(symbol, Stock(symbol))
    stock_projection_input_table_output = stock_projection_input_table_on_stock_update(stock)
    stock_ratios_table_output = update_stock_ratios_table(stock)
    stock_company_name_output = onsumbit_stock_company_name_label(stock)
    return stock_ratios_table_output, stock_company_name_output

def update_stock_ratios_table(stock):
    print('update_stock_ratios_table')
   
    #desired_keys= [ 'earnings-per-share-%s' % stock.currency,
    #                'dividends-%s' % stock.currency,
    #                'book-value-per-share-%s' % stock.currency,
    #                'free-cash-flow-per-share-%s' % stock.currency,
    #                'operating-cash-flow-growth-yoy',
    #                'free-cash-flow-growth-yoy',
    #                'shares',
    #                'operating-cash-flow-%s' % stock.currency,
    #                'free-cash-flow-%s' % stock.currency,
    #                'net-income-%s' % stock.currency,
    #                'revenue-%s' % stock.currency,
    #                'working-capital-%s' % stock.currency,
    #                'return-on-invested-capital',
    #                'return-on-equity',
    #                'debt-equity',
    #                'long-term-debt',
    #                'short-term-debt',
    #                'total-debt-%s' % stock.currency,
    #                'debt-per-earnings',
    #                'debt-per-bookvalue',
    #                ]
    desired_keys=['dividends-usd', 'free-cash-flow-usd',  'shares', 'long-term-debt-ps', 'cogs', 'total-current-liabilities', 'debt-equity', 'cash-conversion-cycle', 'asset-turnover', 'current-ratio', 'free-cash-flow-growth-yoy', 'intangibles', 'taxes-payable', 'book-value-per-share-usd', 'debt-per-earnings', 'short-term-debt', 'free-cash-flow-sales', 'net-int-inc-other', 'tax-rate', 'profitability', 'free-cash-flow-net-income', 'accrued-liabilities', 'revenue-ps-growth', 'debt-per-bookvalue', 'total-assets', 'net-pp-e', 'total-debt-growth', 'inventory-turnover', 'return-on-equity', 'other-long-term-liabilities', 'ebt-margin', 'operating-cashflow-per-share-usd', 'short-term-debt-ps-growth', 'working-capital-usd', 'fixed-assets-turnover', 'operating-margin-perc', 'total-debt-per-share-usd', 'quick-ratio', 'balance-sheet-items-in', 'operating-income-usd', 'payout-ratio', 'total-debt-usd', 'asset-turnover-average', 'efficiency', 'dividends-ps-growth', 'total-liabilities', 'receivables-turnover', 'net-margin', 'other-current-assets', 'debt-per-asset', 'operating-cashflow-ps-growth', 'liquidity-financial-health', 'earnings-per-share-usd', 'cap-spending-usd', 'days-inventory', 'cash-flow-ratios', 'revenue-per-share-usd', 'total-current-assets', 'other-long-term-assets', 'short-term-debt-ps', 'earnings-ps-growth', 'debt-per-free-cashflow', 'financial-leverage-average', 'operating-cash-flow-usd', 'accounts-payable', 'total-stockholders-equity', 'financial-leverage', 'interest-coverage', 'cap-ex-as-a-of-sales', 'net-income-usd', 'inventory', 'long-term-debt', 'return-on-invested-capital', 'gross-margin-perc', 'operating-margin-val', 'cash-short-term-investments', 'pe', 'days-sales-outstanding', 'r-d', 'operating-cash-flow-growth-yoy', 'margins-of-sales', 'total-liabilities-equity', 'book-value-ps-growth', 'revenue', 'return-on-assets', 'debt-per-total-cash', 'long-term-debt-ps-growth', 'payables-period', 'accounts-receivable', 'free-cash-flow-per-share-usd', 'revenue-usd', 'sg-a', 'other-short-term-liabilities']
    existing_keys = set(list(stock.ratios))
    keys = [k for k in desired_keys if k in existing_keys]
    return fundamentals_to_table(stock.ratios[keys]) + [html.Tr([html.Th("Error"), html.Td(e)]) for e in stock.error_log ]
def stock_projection_input_table_on_stock_update(stock):
    print('stock_projection_input_table_on_stock_update')

    rows = []
    default_input_kwargs = {"type" : "number",
                            "inputMode" : "numeric",
                            }

    n_years_input = dcc.Input(id='stock-projection-table-nyear-input',
                              value=stock.n_projection_years,
                              **default_input_kwargs)
    rows.append(html.Tr([html.Th("Projection years"), html.Td(n_years_input)]))

    try:
        value = round(stock.estimated_growth * 100.,2)
    except Exception as e:
        print("Error:" + str(e)) 
        raise
        value = 0
    eps_growth_input = dcc.Input(id='stock-projection-table-eps-growth-rate-input',
                                 value=value,
                                 **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected EPS growth %"), html.Td(eps_growth_input)]))

    target_yield = dcc.Input(id='stock-projection-table-target-yield-input',
                                               value=round(stock.target_yield * 100.,2),
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Target yield %"), html.Td(target_yield)]))

    try:
        value = round(stock.target_pe,1)
    except Exception as e:
        print("Error" + str(e))
        raise
        value = 0
    target_pe = dcc.Input(id='stock-projection-table-target-pe-input',
                                               value=value,
                                               **default_input_kwargs)
    rows.append(html.Tr([html.Th("Target p/e"), html.Td(target_pe)]))

    try:
        value = round(stock.expected_dividends,2)
    except Exception as e:
        print("Error:" + str(e))
        raise
        value = 0
    expected_dividends = dcc.Input(id='stock-projection-table-expected-dividends-input',
                                                   value=value,
                                                   **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected dividends %s" % stock.currency), html.Td(expected_dividends)]))

    try:
        value = round(stock.projected_dividends_growth * 100. ,2)
    except Exception as e:
        print("Error:" + str(e))
        raise
        value = 0
    projected_dividends_growth = dcc.Input(id='stock-projection-table-projected-dividends-growth-input',
                                                   value=value,
                                                   **default_input_kwargs)
    rows.append(html.Tr([html.Th("Expected dividends growth %"), html.Td(projected_dividends_growth)]))

    return rows

def fundamentals_to_table(df,n_years=99):
    print('fundamentals_to_table')
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
            if int(output_value) == float(output_value):
                decimals = 0
            else:
                decimals = 2 # Assumes 2 decimal places for money
            output_value = '{0:.{1}f}'.format(output_value, decimals)
        except ValueError:
            pass
        except OverflowError:
            pass
        if header:
            return output_header
        return output_value

    for key in list(df):
        print(key)
        #print(type())
        body.append(html.Tr([html.Th(formated_value(df, key, header=True))] +[html.Td()] + list([ html.Td(formated_value(df, key, iloc=i)) for i in range(len(df))])[:n_years] ) )
    return header + body

def onsumbit_stock_company_name_label(stock):
    print('onsumbit_stock_company_name_label')
    return  u'{name}'.format(name=stock.company_name)
