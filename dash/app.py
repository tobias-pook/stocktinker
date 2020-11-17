import dash

stock_cache = {}
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, compress=False, requests_pathname_prefix='/Prod/', external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True