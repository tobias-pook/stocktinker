import json
import requests
from dash import Dash

stock_cache = {}
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"]

app = Dash(__name__, compress=False, requests_pathname_prefix='/Prod/', external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True
