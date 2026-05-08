"""
Description:This code implements a Flask-based REST API service that acts as the storage layer for the Kafka streaming pipeline.
It provides endpoints to store and retrieve trend data using HTTP requests.The API allows the processing service to send trend snapshots 
and example posts via POST requests, which are then stored in a PostgreSQL database through the DatabaseTrendStore class. 
It also provides GET endpoints to fetch the latest trends and example posts for display on the dashboard. Cross-Origin Resource Sharing (CORS) headers
are added to allow requests from different origins, enabling frontend-backend communication.The service uses structured JSON input and output for easy integration
with other components. Logging is included to track successful operations.The application runs on port 5001 and is accessible within the Docker network. 
Overall, this module acts as a bridge between the processing serviceand persistent storage, enabling scalable and modular data handling.
"""
from flask import Flask, jsonify, request  # Import Flask framework and helpers for JSON responses and HTTP requests

from services.logging_utils import get_logger  # Import custom logger utility
from services.storage.database_store import DatabaseTrendStore  # Import database storage class


logger = get_logger("services.storage.main")  # Create logger instance for this service

app = Flask(__name__)  # Create Flask application instance
store = DatabaseTrendStore()  # Initialize database storage object


@app.after_request  # Flask decorator to modify every outgoing response
def add_cors_headers(response):  # Function to add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"  # Allow requests from any origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"  # Allow Content-Type header
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"  # Allow HTTP methods
    return response  # Return modified response


@app.get("/api/latest-trends")  # Define GET endpoint for latest trends
def latest_trends():  # Function to handle request
    return jsonify(store.latest_trends() or [])  # Return trends from DB or empty list


@app.get("/api/latest-examples")  # Define GET endpoint for example posts
def latest_examples():  # Function to handle request
    return jsonify(store.latest_examples() or [])  # Return examples or empty list


@app.post("/api/trend-snapshots")  # Define POST endpoint to save trend snapshots
def save_trend_snapshot():  # Function to handle request
    payload = request.get_json(silent=True) or {}  # Read JSON request body safely
    trends = [  # Build list of (term, count) tuples
        (item.get("term"), item.get("count"))  # Extract term and count
        for item in payload.get("trends", [])  # Loop through trends list
    ]

    store.save_snapshot(payload.get("posts_processed", 0), trends)  # Save snapshot to database
    logger.info("Stored trend snapshot from API request.")  # Log operation
    return jsonify({"status": "ok"}), 201  # Return success response with HTTP 201


@app.post("/api/example-posts")  # Define POST endpoint to save example posts
def save_example_posts():  # Function to handle request
    payload = request.get_json(silent=True) or {}  # Read JSON request safely

    store.save_example_posts(  # Save example posts to database
        payload.get("posts_processed", 0),  # Number of processed posts
        payload.get("examples", []),  # Example posts list
    )
    logger.info("Stored example posts from API request.")  # Log operation
    return jsonify({"status": "ok"}), 201  # Return success response


if __name__ == "__main__":  # Entry point when file is executed directly
    app.run(host="0.0.0.0", port=5001)  # Run Flask server accessible from all network interfaces on port 5001
