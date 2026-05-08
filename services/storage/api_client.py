Description:
#//This code defines a client that interacts with a storage API to save processed data from the Kafka pipeline.
It is responsible for sending trend snapshots and example posts to an external service using HTTP POST requests.
The class uses JSON to format the data before sending it over the network. The save_snapshot method prepares and sends trending keyword data,
while the save_example_posts method sends representative sample posts. A helper function _post_json handles the actual HTTP communication,
ensuring the payload is correctly encoded and transmitted. The use of a configurable base URL allows flexibility in targeting different storage endpoints.
This component acts as a bridge between the processing service and an external storage system. 
Overall, it enables persistent storage of processed data in a structured and scalable way.//#

import json  # Used to convert Python objects into JSON format
from urllib import request  # Used to send HTTP requests

from services.storage.config import STORAGE_API_URL  # Imports base API URL from config


class StorageApiClient:  # Defines a client to communicate with storage API
    def __init__(self, base_url=STORAGE_API_URL):  # Constructor with default API URL
        self.base_url = base_url.rstrip("/")  # Removes trailing slash from URL

    def save_snapshot(self, posts_processed: int, trends: list):  # Saves trend snapshot data
        payload = {  # Creates payload dictionary
            "posts_processed": posts_processed,  # Number of processed posts
            "trends": [  # List of trending terms
                {
                    "term": term,  # Trend keyword
                    "count": count,  # Frequency count
                }
                for term, count in trends  # Loop over trends list
            ],
        }
        self._post_json("/api/trend-snapshots", payload)  # Sends data to API endpoint

    def save_example_posts(self, posts_processed: int, examples: list):  # Saves example posts
        payload = {  # Creates payload dictionary
            "posts_processed": posts_processed,  # Number of processed posts
            "examples": examples,  # List of example posts
        }
        self._post_json("/api/example-posts", payload)  # Sends data to API endpoint

    def _post_json(self, path: str, payload: dict):  # Helper method to send POST request
        body = json.dumps(payload).encode("utf-8")  # Converts payload to JSON bytes
        api_request = request.Request(  # Creates HTTP request
            f"{self.base_url}{path}",  # Full API URL
            data=body,  # Request body
            headers={"Content-Type": "application/json"},  # Sets content type
            method="POST",  # HTTP method
        )

        with request.urlopen(api_request, timeout=10) as response:  # Sends request and waits for response
            response.read()  # Reads response (ensures request completes)
