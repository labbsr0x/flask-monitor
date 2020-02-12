# flask-monitor
A Prometheus middleware to add basic but very useful metrics for your Python Flask app.

# Metrics

As valid Big Brother library it exposes the following metrics:

```
request_seconds_bucket{type, status, isError, method, addr, le}
request_seconds_count{type, status, isError, method, addr}
request_seconds_sum{type, status, isError, method, addr}
response_size_bytes{type, status, isError, method, addr}
dependency_up{name}
application_info{version}
```

In detail:

1. The `request_seconds_bucket` metric defines the histogram of how many requests are falling into the well defined buckets represented by the label `le`;

2. The `request_seconds_count` is a counter that counts the overall number of requests with those exact label occurrences;

3. The `request_seconds_sum` is a counter that counts the overall sum of how long the requests with those exact label occurrences are taking;

4. The `response_size_bytes` is a counter that computes how much data is being sent back to the user for a given request type. It captures the response size from the `content-length` response header. If there is no such header, the value exposed as metric will be zero;

5. The `dependency_up` is a metric to register weather a specific dependency is up (1) or down (0). The label `name` registers the dependency name;

6. Finally, `application_info` holds static info of an application, such as it's semantic version number;

## Labels

For a specific request:

1. `type` tells which request protocol was used (e.g. `grpc`, `http`, `<your custom protocol>`);
2. `status` registers the response status code; 
3. `isError` let you know if the request's response status is considered an error;
4. `method` registers the request method (e.g. `GET` for http get requests);
5. `addr` registers the requested endpoint address;
6. and `version` tells which version of your service has handled the request;

# How to

Add this package as a dependency:

```
pip install bb-flask-monitor
```

or

```
pipenv install bb-flask-monitor
```

## HTTP Metrics

Use it as middleware:

```python

from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_monitor import register_metrics

app = Flask(__name__)
app.config["APP_VERSION"] = "v0.1.2"

register_metrics(app)
# Plug metrics WSGI app to your main app with dispatcher
dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

```

One can optionally define the buckets of observation for the `request_second` histogram by doing:

```python
register_metrics(app, buckets=[0.1]); // where only one bucket (of 100ms) will be given as output in the /metrics endpoint
```

Other optional parameters are also:

1. `error_fn`: an error callback to define what **you** consider as error. `4**` and `5**` considered as errors by default;


## Dependency Metrics

For you to know when a dependency is up or down, just provide a health check callback to be `watch_dependencies` function:

```python
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
```

Other optional parameters are also:

watch_dependencies has the following parameters:

1. `dependency`: the name of the dependency;

2. `func`: the health check callback function;

3. `time_execution`: the interval time in seconds that `func` will be called.

Now run your app and point prometheus to the defined metrics endpoint of your server.

More details on how Prometheus works, you can find it [here](https://medium.com/ibm-ix/white-box-your-metrics-now-895a9e9d34ec).

# Example

In the `example` folder, you'll find a very simple but useful example to get you started. On your terminal, navigate to the project's root folder and type:

```bash
cd example
pipenv install
```

and then

```bash
python app.py
```

On your browser, go to `localhost:5000` and then go to `localhost:5000/metrics` to see the exposed metrics.

# Big Brother

This is part of a more large application called [Big Brother](https://github.com/labbsr0x/big-brother).