import awsgi
from dash.index import app

def lambda_handler(event, context):
    return awsgi.response(app.server, event, context)