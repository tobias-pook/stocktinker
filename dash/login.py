import awsgi
from dash.server import server

def lambda_handler(event, context):
    return awsgi.response(server, event, context)
