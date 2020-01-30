import time
import threading
import logging

LOGGER = logging.getLogger(__name__)

def test_endpoint_index(app, client):
    with app.test_request_context():
        response = client.get("/teste")
        assert b"Test" in response.data

def test_application_version(app, client):
    with app.test_request_context():
        response = client.get("/metrics")
        assert b"application_info" in response.data
        assert b"version=\"v0.1.2\"" in response.data

def test_metric_app_request_latency_seconds(app, client):
    with app.test_request_context():
        response = client.get("/metrics")
        assert b"request_seconds" in response.data
        assert b"le=\"0.1\"" in response.data
        assert b"le=\"0.3\"" in response.data
        assert b"le=\"1.5\"" in response.data
        assert b"le=\"10.5\"" in response.data

# def test_metric_dependency_up(app, client):
#     with app.test_request_context():
#         response = client.get("/teste")
#         time.sleep(5)
#         response = client.get("/metrics")
#         LOGGER.info("TESTE")
#         print("response", response.data)
#         assert b"database" in response.data
#         main_thread = threading.current_thread()
#         for t in threading.enumerate():
#             LOGGER.info('joining %s', t.getName())
#             if t is main_thread:
#                 continue


def test_metric_app_request_count(app, client):
    with app.test_request_context():
        response = client.get("/metrics")
        assert b"response_size_bytes" in response.data


def test_standard_metrics(app, client):
    with app.test_request_context():
        response = client.get("/metrics")
        assert b"python_gc_objects_collected_total" in response.data
        assert b"python_gc_objects_uncollectable_total" in response.data
        assert b"python_gc_collections_total" in response.data
        assert b"python_info" in response.data
