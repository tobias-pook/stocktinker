from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from .app import app
from .boards import screenerboard, stockboard


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/screener':
         return screenerboard.layout
    elif pathname == '/stock':
         return stockboard.layout
    else:
        return '404'
