"""
Description:
This code implements a database storage layer for the Kafka-based streaming pipeline. It uses PostgreSQL to store processed trend data, including snapshots,
individual terms, and example posts. The design follows separation of concerns by keeping SQL queries in external files while the Python class manages 
database connections and execution. It ensures scalability by storing structured data in relational tables instead of large JSON files. 
Fault tolerance is achieved through the use of database transactions, which prevent partial writes in case of failure. 
Security is maintained using parameterized SQL queries to avoid SQL injection. The system also provides transparency by logging successful operations with 
snapshot IDs. Additionally, it supports retrieving the latest trends and example posts for dashboard display.Overall, this module provides a reliable, scalable,
and secure persistence layer for the application.
"""

# -----------------------------------------------------
#  Store trends to Database
#
#   -- Open Design --
#   SQL statements live in sql_lib, while this Python class handles database
#   connections and maps processed trend data into database rows.
#
#   -- Scalability --
#   Trend snapshots, terms, and examples are stored in relational tables so
#   historical data can be queried without rewriting large JSON files.
#
#   -- Fault Tolerance --
#   Database writes run inside connection context managers. If an insert fails,
#   the transaction is rolled back instead of partially committing data.
#
#   -- Transparency --
#   Each successful database write logs the snapshot id created by PostgreSQL.
#
#   -- Security --
#   SQL uses parameterized values instead of string formatting, which helps
#   protect against SQL injection from user-generated post text.
# -----------------------------------------------------

from datetime import datetime, timezone  # Used to generate timestamps
from pathlib import Path  # Used for file path handling
import psycopg  # PostgreSQL database driver
from services.logging_utils import get_logger  # Custom logger import
from services.storage.config import (  # Import configuration constants
    CREATE_TABLE_SQL_PATH,  # Path to SQL for creating tables
    DATABASE_URL,  # Database connection URL
    INSERT_TREND_EXAMPLE_SQL_PATH,  # SQL path for inserting examples
    INSERT_TREND_SNAPSHOT_SQL_PATH,  # SQL path for inserting snapshot
    INSERT_TREND_TERM_SQL_PATH,  # SQL path for inserting terms
    SELECT_LATEST_EXAMPLES_SQL_PATH,  # SQL path for selecting examples
    SELECT_LATEST_TRENDS_SQL_PATH,  # SQL path for selecting trends
)


logger = get_logger("services.storage.database_store")  # Create logger instance

class DatabaseTrendStore:  # Class to manage DB operations for trends
    def __init__(  # Constructor method
        self,
        database_url=DATABASE_URL,  # Default DB URL from config
        schema_path=CREATE_TABLE_SQL_PATH,  # Path to schema SQL
        insert_snapshot_path=INSERT_TREND_SNAPSHOT_SQL_PATH,  # Path to insert snapshot SQL
        insert_term_path=INSERT_TREND_TERM_SQL_PATH,  # Path to insert term SQL
        insert_example_path=INSERT_TREND_EXAMPLE_SQL_PATH,  # Path to insert example SQL
        select_latest_trends_path=SELECT_LATEST_TRENDS_SQL_PATH,  # Path to select trends SQL
        select_latest_examples_path=SELECT_LATEST_EXAMPLES_SQL_PATH,  # Path to select examples SQL
    ):
        self.database_url = database_url  # Store DB connection string
        self.schema_path = Path(schema_path)  # Convert schema path to Path object
        self.insert_snapshot_sql = self._load_sql(insert_snapshot_path)  # Load snapshot SQL
        self.insert_term_sql = self._load_sql(insert_term_path)  # Load term SQL
        self.insert_example_sql = self._load_sql(insert_example_path)  # Load example SQL
        self.select_latest_trends_sql = self._load_sql(select_latest_trends_path)  # Load select trends SQL
        self.select_latest_examples_sql = self._load_sql(select_latest_examples_path)  # Load select examples SQL
        self._create_tables()  # Ensure tables exist

    def _connect(self):  # Internal method to connect to DB
        return psycopg.connect(self.database_url)  # Open PostgreSQL connection

    def _load_sql(self, path):  # Load SQL from file
        return Path(path).read_text(encoding="utf-8")  # Read SQL file content

    def _create_tables(self):  # Create tables if not exist
        schema_sql = self._load_sql(self.schema_path)  # Load schema SQL

        with self._connect() as connection:  # Open DB connection safely
            with connection.cursor() as cursor:  # Open DB cursor
                cursor.execute(schema_sql)  # Execute schema SQL

        logger.info("Database storage schema initialized.")  # Log success

# Save one trend snapshot and its top terms in a single database transaction
    def save_snapshot(self, posts_processed: int, trends: list):  # Save snapshot method
        timestamp = datetime.now(timezone.utc)  # Get current UTC time

        with self._connect() as connection:  # Open DB connection
            with connection.cursor() as cursor:  # Open cursor
                cursor.execute(  # Insert snapshot row
                    self.insert_snapshot_sql,
                    (timestamp, posts_processed),  # Pass values safely
                )
                snapshot_id = cursor.fetchone()[0]  # Get inserted snapshot ID

                for term, count in trends:  # Loop through trends
                    cursor.execute(  # Insert each trend term
                        self.insert_term_sql,
                        (snapshot_id, term, count),  # Link to snapshot
                    )

        logger.info("Saved trend snapshot to database: snapshot_id=%s", snapshot_id)  # Log result

# Save example posts for the latest trend terms so the dashboard can show context
    def save_example_posts(self, posts_processed: int, examples: list):  # Save examples method
        timestamp = datetime.now(timezone.utc)  # Current time

        with self._connect() as connection:  # Open DB connection
            with connection.cursor() as cursor:  # Open cursor
                cursor.execute(  # Insert snapshot
                    self.insert_snapshot_sql,
                    (timestamp, posts_processed),
                )
                snapshot_id = cursor.fetchone()[0]  # Get snapshot ID

                for item in examples:  # Loop through example items
                    example_post = item.get("example_post") or {}  # Extract example post safely

                    cursor.execute(  # Insert example post
                        self.insert_example_sql,
                        (
                            snapshot_id,  # Snapshot reference
                            item.get("term"),  # Trend term
                            item.get("count"),  # Count
                            example_post.get("post_id"),  # Post ID
                            example_post.get("author"),  # Author
                            example_post.get("timestamp"),  # Timestamp
                            example_post.get("text"),  # Post text
                        ),
                    )

        logger.info("Saved example posts to database: snapshot_id=%s", snapshot_id)  # Log success

    def latest_trends(self):  # Fetch latest trends
        with self._connect() as connection:  # Connect to DB
            with connection.cursor() as cursor:  # Open cursor
                cursor.execute(self.select_latest_trends_sql)  # Execute select query
                rows = cursor.fetchall()  # Fetch all results

        if not rows:  # If no data
            return None  # Return nothing

        first_row = rows[0]  # Get first row for metadata

        return {  # Return formatted dictionary
            "timestamp": first_row[1].isoformat(),  # Convert timestamp
            "posts_processed": first_row[2],  # Posts count
            "trends": [  # Build trends list
                {
                    "term": row[3],  # Term
                    "count": row[4],  # Count
                }
                for row in rows  # Loop through rows
            ],
        }

    def latest_examples(self):  # Fetch latest example posts
        with self._connect() as connection:  # Connect to DB
            with connection.cursor() as cursor:  # Open cursor
                cursor.execute(self.select_latest_examples_sql)  # Execute query
                rows = cursor.fetchall()  # Fetch results

        if not rows:  # If empty
            return None  # Return nothing

        first_row = rows[0]  # Get metadata row

        return {  # Return formatted data
            "timestamp": first_row[1].isoformat(),  # Timestamp
            "posts_processed": first_row[2],  # Count
            "examples": [  # List of examples
                {
                    "term": row[3],  # Term
                    "count": row[4],  # Count
                    "example_post": {  # Nested post data
                        "post_id": row[5],  # Post ID
                        "author": row[6],  # Author
                        "timestamp": row[7],  # Timestamp
                        "text": row[8],  # Content
                    },
                }
                for row in rows  # Loop
            ],
        }
