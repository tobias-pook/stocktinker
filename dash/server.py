import json
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_awscognito import AWSCognitoAuthentication
from jwt.algorithms import RSAAlgorithm
import jwt
from flask_jwt_extended import (
    JWTManager,
    set_access_cookies,
    unset_access_cookies,
    get_jwt_identity,
)
stock_cache = {}
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"]
server = Flask(__name__)
def get_aws_auth(server):
    server.config['COGNITO_AUTH_CLIENT_ID'] = os.getenv("COGNITO_AUTH_CLIENT_ID")
    server.config['COGNITO_AUTH_CLIENT_SECRET'] = os.getenv("COGNITO_AUTH_CLIENT_SECRET")
    server.config['AWS_DEFAULT_REGION'] = os.getenv("DEFAULT_REGION")
    server.config['AWS_COGNITO_DOMAIN'] = os.getenv("AWS_COGNITO_DOMAIN")
    server.config['AWS_COGNITO_USER_POOL_ID'] = os.getenv("AWS_COGNITO_USER_POOL_ID")
    server.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = os.getenv("COGNITO_AUTH_CLIENT_ID")
    server.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = os.getenv("COGNITO_AUTH_CLIENT_SECRET")
    server.config['AWS_COGNITO_REDIRECT_URL'] = os.getenv("AWS_COGNITO_REDIRECT_URL")
    server.config['JWT_TOKEN_LOCATION'] = ["cookies"]
    server.config['JWT_IDENTITY_CLAIM'] = "sub"
    server.config['JWT_ACCESS_COOKIE_NAME'] = "aws_token"
    server.config['JWT_ACCESS_COOKIE_PATH'] = "/"
    server.config['JWT_COOKIE_DOMAIN'] = os.getenv("JWT_COOKIE_DOMAIN")
    server.config['JWT_COOKIE_SECURE'] = True
    server.config['JWT_COOKIE_SAMESITE'] = 'None'
    server.config['JWT_COOKIE_CSRF_PROTECT'] = False
    server.config['JWT_COOKIE_CSRF_PROTECT'] = False
    server.config['JWT_CSRF_IN_COOKIE'] = False
    server.config['JWT_ACCESS_CSRF_FIELD_NAME'] = 'csrf-token'
    server.config['JWT_ALGORITHM'] = "RS256"
    server.config["JWT_PUBLIC_KEY"] = RSAAlgorithm.from_jwk(get_cognito_public_keys())
    return AWSCognitoAuthentication(server)

def get_cognito_public_keys():
    region = server.config["AWS_DEFAULT_REGION"]
    pool_id = server.config["AWS_COGNITO_USER_POOL_ID"]
    url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"

    resp = requests.get(url)
    #print(resp)
    #print(json.dumps(json.loads(resp.text)["keys"][1]))
    return json.dumps(json.loads(resp.text)["keys"][1])
aws_auth = get_aws_auth(server)
jwt_man = JWTManager(server)
def decode_access_token(server):
    #jwt = JWTManager(server)
    access_token = request.cookies.get(server.config['JWT_ACCESS_COOKIE_NAME'])
    if access_token:
        print("access_token:" + access_token)
        decoded = jwt.decode(access_token, server.config["JWT_PUBLIC_KEY"], algorithms='RS256')   
        return decoded
    return None
def access_token(server):
    #jwt = JWTManager(server)
    access_token = request.cookies.get(server.config['JWT_ACCESS_COOKIE_NAME'])
    return access_token

@server.route("/", defaults={'path':''})
@server.route('/<path:path>')
def MyDashApp(path):
    #print('_____path_'+path)
    if(path=='login/loggedin'):
        #print(request.args)
        token_url = f'{os.getenv("AWS_COGNITO_DOMAIN")}oauth2/token'
        # Prepare the data to send in the POST request
        data = {
            'grant_type': 'authorization_code',
            'client_id': os.getenv("COGNITO_AUTH_CLIENT_ID"),
            'redirect_uri': os.getenv("AWS_COGNITO_REDIRECT_URL"),
            'code': request.args['code']
        }
       # print(data)
        credentials = base64.b64encode(f'{os.getenv("COGNITO_AUTH_CLIENT_ID")}:{os.getenv("COGNITO_AUTH_CLIENT_SECRET")}'.encode()).decode()
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(token_url, data=data, headers=headers)
        print(response)
        # Check if the request was successful
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f'Access Token: {access_token}')
        else:
            print(f'Error: {response.status_code} - {response.text}')
        
        access_token = response.json()['access_token']
        #print(access_token)
        resp = make_response(redirect(url_for("MyDashApp1")))
        set_access_cookies(resp, access_token, max_age=30 * 60)
        return resp
    if(path=='login/log-out'):
        resp = make_response(redirect(url_for("dash_login")))
       # print('unset_access_cookies(resp)')
        unset_access_cookies(resp)
        return resp
    #print(server.config["JWT_PUBLIC_KEY"])
    token = decode_access_token(server)
    #print(token)
    if not token:
        #print('redirect to cognito Dash')
        return redirect(aws_auth.get_sign_in_url())
    #print('app.index redirect')
    return redirect(url_for("MyDashApp1"))
@server.route("/Prod/login/login")
def dash_login():
    #if not get_jwt_identity():
    #    print('redirect to cognito Dash')
    #    return redirect(aws_auth.get_sign_in_url())
    #print('app.index redirect')
    return app.index()
@server.route("/Prod/fundamentals")
def MyDashApp1():
    #if not get_jwt_identity():
    #    print('redirect to cognito Dash')
    #    return redirect(aws_auth.get_sign_in_url())
   # print('app.index redirect')
    return app.index()
#auth = cognito_oauth.CognitoOAuth(app, domain='stocktinker-dev', region='eu-central-1')
