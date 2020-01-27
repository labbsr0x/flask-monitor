
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import traceback
from flask_monitor import register_metrics, watch_dependencies
from flask import Flask
import requests as req

app = Flask(__name__)
app.config["APP_VERSION"] = "v0.1.2"

register_metrics(app)
# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

def check_db():
    try:
        response = req.get("http://localhost:7000/bd")
        if response.status_code == 200:
            return 1
    except:
        traceback.print_stack()
    return 0

watch_dependencies("Bd", check_db)

@app.route('/teste')
def hello_teste():
    return 'Hello, World!'

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    run_simple(hostname="localhost", port=5000, application=dispatcher)
    # app.run()