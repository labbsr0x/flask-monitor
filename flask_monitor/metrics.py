""" Functions for define and register metrics """
import time
import threading
from flask import request
from prometheus_client import Counter, Histogram, Gauge

#
# Request callbacks
#

METRICS_INFO = Gauge(
    "application_info",
    "records static application info such as it's semantic version number",
    ["version"]
)

DEPENDENCY_UP = Gauge(
    'dependency_up',
    'records if a dependency is up or down. 1 for up, 0 for down',
    ["name"]
)

def is_error(code):
    """
    Default status error checking
    """
    code = str(code) if isinstance(code, int) else code
    return code.startswith("5") or code.startswith("4")

#
# Metrics registration
#
def register_metrics(app, buckets=None, error_fn=None):
    """
    Register metrics middlewares

    Use in your application factory (i.e. create_app):
    register_middlewares(app, settings["version"], settings["config"])

    Flask application can register more than one before_request/after_request.
    Beware! Before/after request callback stored internally in a dictionary.
    Before CPython 3.6 dictionaries didn't guarantee keys order, so callbacks
    could be executed in arbitrary order.
    """
    buckets = [0.1, 0.3, 1.5, 10.5] if buckets is None else buckets
    # pylint: disable=invalid-name
    METRICS_REQUEST_LATENCY = Histogram(
        "request_seconds",
        "records in a histogram the number of http requests and their duration in seconds",
        ["type", "status", "isError", "method", "addr"],
        buckets=buckets
    )

    METRICS_REQUEST_SIZE = Counter(
        "response_size_bytes",
        "counts the size of each http response",
        ["type", "status", "isError", "method", "addr"],
    )
    # pylint: enable=invalid-name

    app_version = app.config.get("APP_VERSION", "0.0.0")
    METRICS_INFO.labels(app_version).set(1)

    def before_request():
        """
        Get start time of a request
        """
        # pylint: disable=protected-access
        request._prometheus_metrics_request_start_time = time.time()
        # pylint: enable=protected-access

    def after_request(response):
        """
        Register Prometheus metrics after each request
        """
        size_request = int(response.headers.get("Content-Length", 0))
        # pylint: disable=protected-access
        request_latency = time.time() - request._prometheus_metrics_request_start_time
        # pylint: enable=protected-access
        error_status = is_error(response.status_code)
        METRICS_REQUEST_LATENCY \
            .labels("http", response.status_code, error_status, request.method, request.path) \
            .observe(request_latency)
        METRICS_REQUEST_SIZE.labels(
            "http", response.status_code, error_status, request.method, request.path
        ).inc(size_request)
        return response
    if error_fn is not None:
        is_error.__code__ = error_fn.__code__
    app.before_request(before_request)
    app.after_request(after_request)

def watch_dependencies(dependency, func, time_execution=1500):
    """
    Register dependencies metrics
    """
    def thread_function():
        thread = threading.Timer(time_execution, lambda x: x + 1, args=(1,))
        thread.start()
        thread.join()
        response = func()
        DEPENDENCY_UP.labels(dependency).set(response)
        thread_function()
    thread = threading.Timer(time_execution, thread_function)
    thread.start()
