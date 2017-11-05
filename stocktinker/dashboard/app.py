import dash

app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
server = app.server
app.config.supress_callback_exceptions = True

stock_cache = {}
