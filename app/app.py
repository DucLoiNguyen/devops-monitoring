import random
import socket
import time

from flask import Flask, Response, abort, request
from prometheus_client import (CONTENT_TYPE_LATEST, Counter, Histogram,
                               generate_latest)

app = Flask(__name__)

REQUESTS = Counter(
    "app_requests_total", "Tổng số request", ["method", "endpoint", "status"]
)
LATENCY = Histogram(
    "app_request_duration_seconds", "Thời gian xử lý request", ["endpoint"]
)


@app.before_request
def start_timer():
    request._start = time.time()


@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        LATENCY.labels(request.path).observe(time.time() - request._start)
        REQUESTS.labels(request.method, request.path, response.status_code).inc()
    return response


@app.route("/")
def home():
    return f"Xin chào! Mình là container: {socket.gethostname()}\n"


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/slow")
def slow():
    time.sleep(random.uniform(0.2, 1.5))
    return "Phản hồi chậm (giả lập)\n"


@app.route("/error")
def error():
    abort(500)


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
