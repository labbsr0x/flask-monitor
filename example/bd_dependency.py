from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import traceback
from flask_monitor import register_metrics
from flask import Flask


app = Flask(__name__)

@app.route('/bd')
def bd_running():
    return 'I am a bd working.'

if __name__ == "__main__":
    app.run(port=7000)
    # app.run()