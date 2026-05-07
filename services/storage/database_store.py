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

from datetime import datetime, timezone
from pathlib import Path
import psycopg
from services.logging_utils import get_logger
from services.storage.config import (
    CREATE_TABLE_SQL_PATH,
    DATABASE_URL,
    INSERT_TREND_EXAMPLE_SQL_PATH,
    INSERT_TREND_SNAPSHOT_SQL_PATH,
    INSERT_TREND_TERM_SQL_PATH,
    SELECT_LATEST_EXAMPLES_SQL_PATH,
    SELECT_LATEST_TRENDS_SQL_PATH,
)


logger = get_logger("services.storage.database_store")

class DatabaseTrendStore:
    def __init__(
        self,
        database_url=DATABASE_URL,
        schema_path=CREATE_TABLE_SQL_PATH,
        insert_snapshot_path=INSERT_TREND_SNAPSHOT_SQL_PATH,
        insert_term_path=INSERT_TREND_TERM_SQL_PATH,
        insert_example_path=INSERT_TREND_EXAMPLE_SQL_PATH,
        select_latest_trends_path=SELECT_LATEST_TRENDS_SQL_PATH,
        select_latest_examples_path=SELECT_LATEST_EXAMPLES_SQL_PATH,
    ):
        self.database_url = database_url
        self.schema_path = Path(schema_path)
        self.insert_snapshot_sql = self._load_sql(insert_snapshot_path)
        self.insert_term_sql = self._load_sql(insert_term_path)
        self.insert_example_sql = self._load_sql(insert_example_path)
        self.select_latest_trends_sql = self._load_sql(select_latest_trends_path)
        self.select_latest_examples_sql = self._load_sql(select_latest_examples_path)
        self._create_tables()

    def _connect(self):
        return psycopg.connect(self.database_url)

    def _load_sql(self, path):
        return Path(path).read_text(encoding="utf-8")

    def _create_tables(self):
        schema_sql = self._load_sql(self.schema_path)

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(schema_sql)

        logger.info("Database storage schema initialized.")

# Save one trend snapshot and its top terms in a single database transaction
    def save_snapshot(self, posts_processed: int, trends: list):
        timestamp = datetime.now(timezone.utc)

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.insert_snapshot_sql,
                    (timestamp, posts_processed),
                )
                snapshot_id = cursor.fetchone()[0]

                for term, count in trends:
                    cursor.execute(
                        self.insert_term_sql,
                        (snapshot_id, term, count),
                    )

        logger.info("Saved trend snapshot to database: snapshot_id=%s", snapshot_id)

# Save example posts for the latest trend terms so the dashboard can show context
    def save_example_posts(self, posts_processed: int, examples: list):
        timestamp = datetime.now(timezone.utc)

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    self.insert_snapshot_sql,
                    (timestamp, posts_processed),
                )
                snapshot_id = cursor.fetchone()[0]

                for item in examples:
                    example_post = item.get("example_post") or {}

                    cursor.execute(
                        self.insert_example_sql,
                        (
                            snapshot_id,
                            item.get("term"),
                            item.get("count"),
                            example_post.get("post_id"),
                            example_post.get("author"),
                            example_post.get("timestamp"),
                            example_post.get("text"),
                        ),
                    )

        logger.info("Saved example posts to database: snapshot_id=%s", snapshot_id)

    def latest_trends(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(self.select_latest_trends_sql)
                rows = cursor.fetchall()

        if not rows:
            return None

        first_row = rows[0]

        return {
            "timestamp": first_row[1].isoformat(),
            "posts_processed": first_row[2],
            "trends": [
                {
                    "term": row[3],
                    "count": row[4],
                }
                for row in rows
            ],
        }

    def latest_examples(self):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(self.select_latest_examples_sql)
                rows = cursor.fetchall()

        if not rows:
            return None

        first_row = rows[0]

        return {
            "timestamp": first_row[1].isoformat(),
            "posts_processed": first_row[2],
            "examples": [
                {
                    "term": row[3],
                    "count": row[4],
                    "example_post": {
                        "post_id": row[5],
                        "author": row[6],
                        "timestamp": row[7],
                        "text": row[8],
                    },
                }
                for row in rows
            ],
        }
