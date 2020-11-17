from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from dash.app import app
from .boards import stockboard


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    return stockboard.layout
