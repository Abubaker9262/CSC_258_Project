import os

TREND_SNAPSHOT_PATH = "services/storage/logs/trends.json"
TREND_EXAMPLE_POSTS_PATH = "services/storage/logs/example_posts.json"


CREATE_TABLE_SQL_PATH = "services/storage/sql_lib/create_tables.sql"
INSERT_TREND_SNAPSHOT_SQL_PATH = "services/storage/sql_lib/insert_trend_snapshot.sql"
INSERT_TREND_TERM_SQL_PATH = "services/storage/sql_lib/insert_trend_term.sql"
INSERT_TREND_EXAMPLE_SQL_PATH = "services/storage/sql_lib/insert_trend_example.sql"
DATABASE_URL = os.getenv("DATABASE_URL","postgresql://trend_user:trend_password@localhost:5432/trends_db")
