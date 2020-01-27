from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_monitor import register_metrics

app = Flask(__name__)
app.config["APP_VERSION"] = "v0.1.2"

def is_error200(code):
    code = str(code) if type(code) is int else code
    return code.startswith("2")

register_metrics(app,buckets=[0.3, 0.6], error_fn=is_error200)
# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

@app.route('/teste')
def hello_teste():
    return 'Hello, World!'

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    run_simple(hostname="localhost", port=5000, application=dispatcher)
    # app.run()