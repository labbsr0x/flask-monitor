"""
Package usage example

Make sure `flask_prometheus_metrics` installed  first.
Run script as follows:

$ python example.py
"""
from flask import Blueprint, Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from flask_monitor import register_metrics

#
# Constants
#


def create_app():
    """
    Application factory
    """
    app = Flask(__name__)
    app.config["VERSION"] = "v1.2.0"

    @app.route('/teste')
    def hello_teste():
        return 'Test'

    register_metrics(app)
    return app


#
# Dispatcher
#


def create_dispatcher(app) -> DispatcherMiddleware:
    """
    App factory for dispatcher middleware managing multiple WSGI apps
    """
    return DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})


#
# Run
#

if __name__ == "__main__":
    run_simple(
        "localhost",
        5000,
        create_dispatcher(),
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
    )
