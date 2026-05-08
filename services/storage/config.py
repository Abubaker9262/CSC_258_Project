""" 
Description:
This code defines configuration constants used by the storage component of the project.
It specifies file paths for storing processed trend data and example posts in JSON format.
Additionally, it includes paths to various SQL scripts that are used to create tables and perform insert and query operations in a database.
The code also manages environment-based configuration for connecting to external services.
The DATABASE_URL variable allows the application to connect to a PostgreSQL database, either from an environment variable or a default local connection string.
Similarly, the STORAGE_API_URL defines the endpoint for interacting with a storage API service. By using environment variables, the system becomes flexible
and can easily switch between local and cloud environments.Overall, this configuration file centralizes all storage-related paths and connection settings,
making the system more maintainable and scalable."""

import os  # Provides access to environment variables and OS-related functions

TREND_SNAPSHOT_PATH = "services/storage/logs/trends.json"  # File path where trend snapshots are stored as JSON
TREND_EXAMPLE_POSTS_PATH = "services/storage/logs/example_posts.json"  # File path where example posts are stored

# Paths to SQL scripts used for database operations
CREATE_TABLE_SQL_PATH = "services/storage/sql_lib/create_tables.sql"  # SQL script to create database tables
INSERT_TREND_SNAPSHOT_SQL_PATH = "services/storage/sql_lib/insert_trend_snapshot.sql"  # SQL script to insert trend snapshot
INSERT_TREND_TERM_SQL_PATH = "services/storage/sql_lib/insert_trend_term.sql"  # SQL script to insert individual trend terms
INSERT_TREND_EXAMPLE_SQL_PATH = "services/storage/sql_lib/insert_trend_example.sql"  # SQL script to insert example posts
SELECT_LATEST_TRENDS_SQL_PATH = "services/storage/sql_lib/select_latest_trends.sql"  # SQL script to fetch latest trends
SELECT_LATEST_EXAMPLES_SQL_PATH = "services/storage/sql_lib/select_latest_examples.sql"  # SQL script to fetch latest examples

DATABASE_URL = os.getenv("DATABASE_URL","postgresql://trend_user:trend_password@localhost:5432/trends_db")  
# Gets database connection URL from environment variable, or uses default PostgreSQL connection

STORAGE_API_URL = os.getenv("STORAGE_API_URL", "http://localhost:5001")  
# Gets storage API base URL from environment variable, or defaults to local API endpoint
