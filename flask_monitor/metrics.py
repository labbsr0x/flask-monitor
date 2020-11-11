""" Functions for define and register metrics """
import time
import atexit
from flask import request, current_app
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from apscheduler.schedulers.background import BackgroundScheduler

#
# Request callbacks
#
def _is_error_(code):
    """
    Default status error checking
    """
    code = str(code) if isinstance(code, int) else code
    return code.startswith("5") or code.startswith("4")

#
# Metrics registration
#
def register_metrics(app=current_app, buckets=None, error_fn=None, registry=None):
    """
    Register metrics middlewares

    Use in your application factory (i.e. create_app):
    register_middlewares(app, settings["version"], settings["config"])

    Flask application can register more than one before_request/after_request.
    Beware! Before/after request callback stored internally in a dictionary.
    Before CPython 3.6 dictionaries didn't guarantee keys order, so callbacks
    could be executed in arbitrary order.
    """

    if app.config.get("METRICS_ENABLED", False):
        return app, app.extensions.get("registry", registry)
    app.config["METRICS_ENABLED"] = True
    if not registry:
        registry = app.extensions.get("registry", CollectorRegistry())
    app.extensions["registry"] = registry
    app.logger.info('Metrics enabled')

    buckets = [0.1, 0.3, 1.5, 10.5] if buckets is None else buckets


    # pylint: disable=invalid-name
    metrics_info = Gauge(
        "application_info",
        "records static application info such as it's semantic version number",
        ["version", "name"],
        registry=registry
    )

    # pylint: disable=invalid-name
    metrics_request_latency = Histogram(
        "request_seconds",
        "records in a histogram the number of http requests and their duration in seconds",
        ["type", "status", "isError", "errorMessage", "method", "addr"],
        buckets=buckets,
        registry=registry
    )

    # pylint: disable=invalid-name
    metrics_request_size = Counter(
        "response_size_bytes",
        "counts the size of each http response",
        ["type", "status", "isError", "errorMessage", "method", "addr"],
        registry=registry
    )
    # pylint: enable=invalid-name

    app_version = app.config.get("APP_VERSION", "0.0.0")
    metrics_info.labels(app_version, app.name).set(1)

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
        error_status = _is_error_(response.status_code)
        metrics_request_latency \
            .labels("http", response.status_code, error_status, "", request.method, request.path) \
            .observe(request_latency)
        metrics_request_size.labels(
            "http", response.status_code, error_status, "", request.method, request.path
        ).inc(size_request)
        return response

    if error_fn is not None:
        _is_error_.__code__ = error_fn.__code__
    app.before_request(before_request)
    app.after_request(after_request)
    return app, registry


def watch_dependencies(dependency, func, time_execution=15000, registry=None, app=current_app):
    """
    Register dependencies metrics up
    """

    if not registry:
        registry = app.extensions.get("registry", CollectorRegistry())
        app.extensions["registry"] = registry

    # pylint: disable=invalid-name
    DEPENDENCY_UP = Gauge(
        'dependency_up',
        'records if a dependency is up or down. 1 for up, 0 for down',
        ["name"],
        registry=registry
    )
    def register_dependecy():
        DEPENDENCY_UP.labels(dependency).set(func())

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=register_dependecy,
        trigger="interval",
        seconds=time_execution/1000,
        max_instances=1,
        name='dependency',
        misfire_grace_time=2,
        replace_existing=True
        )
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(scheduler.shutdown)
    return scheduler

# pylint: disable=too-many-arguments
def collect_dependency_time(
    app, name, rtype='http', status=200,
    is_error=False, error_message='',
    method='GET', addr='/',
    elapsed=0,
    registry=None
):
    """
    Register dependencies metrics
    """

    if not registry:
        registry = app.extensions.get("registry", CollectorRegistry())
        app.extensions["registry"] = registry

    dependency_up_latency = app.extensions.get(
        "dependency_latency"
    )
    if not dependency_up_latency:
        app.extensions['dependency_latency'] = dependency_up_latency = Histogram(
                "dependency_request_seconds",
                "records in a histogram the number of requests to dependency",
                ["name", "type", "status", "isError", "errorMessage", "method", "addr"],
                registry=registry
            )

    dependency_up_latency \
        .labels(
            name,
            rtype.lower(),
            status,
            "False" if is_error else "True",
            error_message,
            method.upper(),
            addr) \
        .observe(elapsed)
