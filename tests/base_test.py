from flask import Flask, jsonify, url_for
import unittest
from prometheus_client import CollectorRegistry, Counter, make_wsgi_app
from flask_monitor import register_metrics, watch_dependencies, collect_dependency_time
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from time import sleep

class FlaskMonitorTestCase(unittest.TestCase):
    def setUp(self):
        """ setUp test """
        # self.registry = CollectorRegistry()
        self.app = Flask(__name__)
        self.prometheus = make_wsgi_app()


        @self.app.route('/')
        @self.app.route('/teste')
        @self.app.route('/database')
        def index():
            """ Home """
            return jsonify({'home':True})

        def check_db():
            """ HealthCheck """
            response = self.client.get("http://localhost:5000/database")
            collect_dependency_time(
                app=self.app,
                name='database',
                type='http',
                status=response.status_code,
                isError= 'False' if response.status_code < 400 else 'True',
                method='GET',
                addr='/database'
            )
            return True

        def is_error200(code):
            """ Check error """
            code = str(code) if type(code) is int else code
            return code.startswith("2")

        @self.app.route('/metrics')
        def metrics():
            """ Default metrics """
            return self.dispatcher.mounts['/metrics']({}, self.capture)[0]

        self.app, self.registry  = register_metrics(self.app, error_fn=is_error200)
        self.dispatcher = DispatcherMiddleware(self.app.wsgi_app, {"/metrics": make_wsgi_app(registry=self.registry)})
        # self.app.wsgi_app = DispatcherMiddleware(self.app.wsgi_app, self.registry)
        self.scheduler = watch_dependencies("database", check_db, time_execution=500, registry=self.registry, app=self.app)
        self.client = self.app.test_client()
        self.client.get('/batata')
        self.client.get('/teste')
        self.client.get('/teste')
        self.client.get('/')

    def tearDown(self):
        """ TearDown test """
        # self.scheduler.shutdown()
        pass

    def iter_responses(self, path, verbs=['get'], **kwargs):
        """ internal requests """
        for verb in verbs:
            yield self._request(verb.lower(), path, **kwargs)

    def _request(self, verb, *args, **kwargs):
        """ internal requests """
        return getattr(self.client, verb)(*args, **kwargs)

    def capture(self, status, header):
        """ internal requests headers """
        self.captured_status = status
        self.captured_headers = header

    def test_0_routes(self):
        """
        Populate metrics
        """
        for resp in self.iter_responses('/batata'):
            self.assertEqual(404, resp.status_code)

        for resp in self.iter_responses('/batata', verbs=['post', 'delete']):
            self.assertEqual(404, resp.status_code)

        for resp in self.iter_responses('/teste'):
            self.assertEqual(200, resp.status_code)

        for resp in self.iter_responses('/'):
            self.assertEqual(200, resp.status_code)
        self.assertEqual(len(self.prometheus({}, self.capture)), 1)

    def test_metrics(self):
        """
        Check metrics
        """
        resp = self.client.get('/metrics')
        # print(resp.data.decode())
        self.assertIn('request_seconds', resp.data.decode())
        self.assertIn('/batata', resp.data.decode())
        self.assertIn('response_size_bytes', resp.data.decode())
        self.assertIn('request_seconds', resp.data.decode())
        self.assertIn('response_size_bytes_total', resp.data.decode())
        self.assertIn('application_info', resp.data.decode())
        self.assertIn('dependency_up', resp.data.decode())

    def test_metrics_count(self):
        """
        Check metrics count
        """
        resp = self.client.get('/metrics')
        # 2 calls in /teste
        self.assertRegex(resp.data.decode(), r'.*count.*\/teste.*200.*2.0')
        # 1 calls in /batata
        self.assertRegex(resp.data.decode(), r'.*count.*\/batata.*404.*1.0')

    def test_watch_dependencies(self):
        """
        Check dependencies watched
        """
        sleep(3)
        resp = self.client.get('/metrics')
        print(resp.data.decode())
        self.assertIn('database', resp.data.decode())


if __name__ == "__main__":
    unittest.main(verbosity=2)