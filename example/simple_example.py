
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import traceback
from flask_monitor import register_metrics, watch_dependencies, collect_dependency_time
from flask import Flask
import requests as req
from prometheus_client import CollectorRegistry
from time import time, sleep
from random import random

registry = CollectorRegistry()

## create a flask app
app = Flask(__name__)

## APP_VERSION should be set to output it on metrics
app.config["APP_VERSION"] = "v0.1.2"

## a handle function to return what is a http status code failure
def is_error200(code):
    code = str(code) if type(code) is int else code
    return code.startswith("2")

## register metrics
# app is a flask instance and mandatory parameter.
# buckets is the internavals for histogram parameter. buckets is a optional parameter
# error_fn is a function to define what http status code is a error. By default errors are
# 400 and 500 status code. error_fn is a option parameter
register_metrics(app, buckets=[0.3, 0.6], error_fn=is_error200, registry=registry)

# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app(registry=registry)})

# a dependency healthcheck
def check_db():
    try:
        response = req.get("http://localhost:5000/database")
        app.logger.info(response)
        return response.status_code < 400
    except:
        return 0
    

# watch dependency
# first parameter is the dependency's name. It's a mandatory parameter.
# second parameter is the health check function. It's a mandatory parameter.
# time_execution is used to set the interval of running the healthchec function.
# time_execution is a optional parameter
scheduler = watch_dependencies('database', check_db, app=app, time_execution=500)

# endpoint
@app.route('/teste')
def hello_teste():
    return 'Hello, World!'

# endpoint
@app.route('/')
def hello_world():
    return 'Hello, World!'

# endpoint
@app.route('/database')
def bd_running():
    start = time()
    # checks the database
    sleep(random()/10)
    # compute the elapsed time
    elapsed = time() - start
    # register the dependency time
    collect_dependency_time(
        app=app,
        name='database',
        rtype='http',
        status=200,
        is_error= 'False',
        method='GET',
        addr='external/database',
        elapsed=elapsed
    )
    return 'I am a database working.'

if __name__ == "__main__":
    run_simple(hostname="localhost", port=5000, application=dispatcher)
    # app.run()