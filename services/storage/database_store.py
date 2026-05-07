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
    ):
        self.database_url = database_url
        self.schema_path = Path(schema_path)
        self.insert_snapshot_sql = self._load_sql(insert_snapshot_path)
        self.insert_term_sql = self._load_sql(insert_term_path)
        self.insert_example_sql = self._load_sql(insert_example_path)
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
