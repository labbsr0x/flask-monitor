
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import traceback
from flask_monitor import register_metrics
from flask import Flask
import threading
app = Flask(__name__)
app.config["APP_VERSION"] = "v0.1.2"

register_metrics(app)
# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

def hello():
    print("Teste")

t = threading.Timer(3, hello)
t.start()

@app.route('/teste')
def hello_teste():
    return 'Hello, World!'

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    run_simple(hostname="localhost", port=5000, application=dispatcher)
    # app.run()