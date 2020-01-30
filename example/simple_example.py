
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import traceback
from flask_monitor import register_metrics, watch_dependencies
from flask import Flask
import requests as req

app = Flask(__name__)
app.config["APP_VERSION"] = "v0.1.2"

def is_error200(code):
    code = str(code) if type(code) is int else code
    return code.startswith("2")

register_metrics(app, buckets=[0.3, 0.6], error_fn=is_error200)
# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

def check_db():
    try:
        response = req.get("http://localhost:5000/database")
        if response.status_code == 200:
            return 1
    except:
        traceback.print_stack()
    return 0

watch_dependencies("database", check_db, time_execution=1)

@app.route('/teste')
def hello_teste():
    return 'Hello, World!'

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/database')
def bd_running():
    return 'I am a database working.'

if __name__ == "__main__":
    run_simple(hostname="localhost", port=5000, application=dispatcher)
    # app.run()