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
def get_layout():
    layout = html.Div([
        html.H1("About 3F Tool"),
        html.Div([html.P("Inspired by the most successful longterm investor Warren Buffett and his investment strategy the 3F Tool supports longterm investors during their company analysis and due diligence."),
        html.P("Based on longterm key financial data the 3F Tool supports finding wonderful companies with a unique competitive advantage and a great management."),
        html.P("By calculating a target price based on discounted cash flows the 3F Tool also provides an indication for an intrinsic value of the company, helping long term investors to estimate a margin of safety price."),
       html.P("Companies of interest and their estimated intrinsic value can be added to a watchlist and notifications will be sent out as soon as the stock price will be close to the intrinsic value.")], style={'text-align':'justify', 'padding':'20px'})
    ])
    return layout
