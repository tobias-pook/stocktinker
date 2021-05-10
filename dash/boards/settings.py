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
from dash.server import access_token, decode_access_token

from dash.app import app
from dash.app import stock_cache
import boto3
client = boto3.client('cognito-idp')
def get_layout(token):
    old_password = dcc.Input(id='old-password-input', type='password', placeholder='Password')
    new_password = dcc.Input(id='new-password-input', type='password', placeholder='New Password')
    email = token['username']
    userInfo = UserInfo(token['username'])
    settings = userInfo.get_settings()
    email = settings['email']

    email_input = dcc.Input(id='email-input', value=email, type='text', placeholder='Email')
    layout = html.Div([
        html.Div(token['username']),
       # html.Div(token),
        html.Div("Old password:"),
        html.Div(old_password),
        html.Div("New password:"),
        html.Div(new_password),
        html.Div([html.Button(id='change-psw-button', children='Change password', style={'backround' : 'white'}),
          dbc.Toast([html.P("Password has been changed")], id='change-pass-toast', header="Completed", duration=4000, style={'opacity' : '0.5'})
        ]),
        html.Div("Email:"),
        html.Div(email_input),
        html.Div([html.Button(id='settings-save-button', children='Change email', style={'backround' : 'white'}),
          dbc.Toast([html.P("Settings has been saved", className="mb-0")], id='settings-toast', header="Completed", duration=4000, style={'opacity' : '0.5'})
        ])
    ])
    return layout
@app.callback(Output('settings-toast', 'is_open'),
              [Input('settings-save-button', 'n_clicks')],
              [State('email-input', 'value')]
)
def on_save_settings(n_clicks,
                         email):
    if n_clicks:
        token = decode_access_token(app.server)
        userInfo = UserInfo(token['username'])
        userInfo.put_settings({'email':email})
        print('on_settings_save'+str(n_clicks))
        return True
    return False
@app.callback(Output('change-pass-toast', 'is_open'),
              [Input('change-psw-button', 'n_clicks')],
              [State('old-password-input', 'value'),
               State('new-password-input', 'value')
                ]
)
def on_channge_password(n_clicks,
                         old_password,
                         new_password):

    if n_clicks:
        token = access_token(app.server)
        response = client.change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=token
        )
        print('on_password_changed'+str(n_clicks))
        return True
    return False
