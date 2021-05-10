from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from dash.app import app
from .boards import aboutUs, rawData, watchlist, fundamentals, settings, aboutUs, noPermission

from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_awscognito import AWSCognitoAuthentication
from flask_jwt_extended import (
    JWTManager,
    set_access_cookies,
    get_jwt_identity,
)

import dash_bootstrap_components as dbc
from dash.server import get_aws_auth, decode_access_token
aws_auth = get_aws_auth(app.server)

def get_nav_menu(user_name, company):
    return html.Div([
        html.Ul([
            html.Li(
            [
            dcc.Link(user_name, href='#')
            ], className=''),
            html.Li(
            [
                dcc.Link('Fundamentals', href='/Prod/fundamentals/' + company)
            ], className=''),
            html.Li([
                dcc.Link('Watchlist', href='/Prod/watchlist/'  + company)
            ], className=''),
            html.Li([
                dcc.Link('Raw Data', href='/Prod/raw-data/'  + company)
            ], className=''),
            html.Li([
                dcc.Link('Settings', href='/Prod/settings')
            ], className=''),
            html.Li([
                dcc.Link('About 3F Tool', href='/Prod/about-us')
            ], className=''),
            html.Li([
                dcc.Link('Logout', href='/Prod/login/log-out', refresh=True)
            ], className=''),
           ], className='nav navbar-nav')
          ], className='navbar navbar-default navbar-static-top', style={'position': 'sticky', 'top': '1px'})

app.title = "3F Tool"
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <style type="text/css">
            #watchlist-tables thead tr th{
		  vertical-align:top;
	    }
            #watchlist-tables tbody tr td:nth-child(1), #watchlist-tables thead tr th:nth-child(1){
		  top: auto; left: 10px; position: absolute; background-color: white;border:0;
	    }
            #watchlist-tables tbody tr td:nth-child(2), #watchlist-tables thead tr th:nth-child(2){
		  padding-left: 100px;
	    }
        </style>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''   
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div( [html.Div(id = 'fundamental' )],
              style = {'display': 'block'})
])
@app.callback(Output('fundamental', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    token = decode_access_token(app.server)
    stock_chars = 'AAPL'
    if not pathname.split('/')[-1] in ['fundamentals','watchlist','remove-from-watch-list', 'raw-data', 'about-us', 'settings']:
        stock_chars = pathname.split('/')[-1]
        #print(stock_chars)
    if not token:
        print('Redirect to login')
        return dcc.Location(id='login', href='/Prod/login/login', refresh=True)
    if not "cognito:groups" in token or not "3frocks" in token["cognito:groups"]:
            return noPermission.get_layout()
    menu_nav = get_nav_menu(token['username'], stock_chars)
    page = get_page(pathname, stock_chars, token)
    return html.Div([
        menu_nav,
        page
    ])
def get_page(pathname, stock_chars, token):
    if 'watchlist' in pathname:
        return watchlist.get_layout(token)
    if 'remove-from-watch-list' in pathname:
        print('remove-from-watchlist:')
        print('company:' + stock_chars)
        return watchlist.remove_company(token, stock_chars)
    #if 'row-data' in pathname:
      #  return rowData.get_layout(stock_chars)
    if 'raw-data' in pathname:
        return rawData.get_layout(stock_chars)
    if 'settings' in pathname:
        return settings.get_layout(token)
    if 'about-us' in pathname:
        return aboutUs.get_layout()
    return fundamentals.get_layout(token, stock_chars)
