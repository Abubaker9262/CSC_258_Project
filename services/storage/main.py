from flask import Flask, jsonify, request

from services.logging_utils import get_logger
from services.storage.database_store import DatabaseTrendStore


logger = get_logger("services.storage.main")

app = Flask(__name__)
store = DatabaseTrendStore()


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.get("/api/latest-trends")
def latest_trends():
    return jsonify(store.latest_trends() or [])


@app.get("/api/latest-examples")
def latest_examples():
    return jsonify(store.latest_examples() or [])


@app.post("/api/trend-snapshots")
def save_trend_snapshot():
    payload = request.get_json(silent=True) or {}
    trends = [
        (item.get("term"), item.get("count"))
        for item in payload.get("trends", [])
    ]

    store.save_snapshot(payload.get("posts_processed", 0), trends)
    logger.info("Stored trend snapshot from API request.")
    return jsonify({"status": "ok"}), 201


@app.post("/api/example-posts")
def save_example_posts():
    payload = request.get_json(silent=True) or {}

    store.save_example_posts(
        payload.get("posts_processed", 0),
        payload.get("examples", []),
    )
    logger.info("Stored example posts from API request.")
    return jsonify({"status": "ok"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
