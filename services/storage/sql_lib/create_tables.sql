"""
Description:This SQL script defines the database schema used to store processed trend data in a PostgreSQL database.
It creates three main tables: trend_snapshots, trend_terms, and trend_examples. The trend_snapshots table stores metadata
such as the timestamp and number of processed posts. The trend_terms table stores individual trending keywords along with
their frequency and links them to a specific snapshot using a foreign key. The trend_examples table stores sample posts
related to each trend, including metadata such as author and post content. Referential integrity is maintained using foreign key
constraints with cascading deletes, ensuring that related records are removed automatically when a snapshot is deleted.
This design supports efficient querying and avoids duplication of data. Overall, it provides a structured and scalable way to persist
trend data for analysis and visualization.
"""

--------------------------------------
-- DDL create tables for storing trends and sample post
-------------------------------------

CREATE TABLE IF NOT EXISTS trend_snapshots (  -- Create table to store trend snapshots (if not already exists)
    id SERIAL PRIMARY KEY,  -- Auto-incrementing unique ID
    timestamp TIMESTAMPTZ NOT NULL,  -- Timestamp with timezone, cannot be null
    posts_processed INTEGER NOT NULL  -- Number of posts processed in snapshot
);

CREATE TABLE IF NOT EXISTS trend_terms (  -- Create table for individual trend terms
    id SERIAL PRIMARY KEY,  -- Unique ID for each term record
    snapshot_id INTEGER NOT NULL REFERENCES trend_snapshots(id) ON DELETE CASCADE,  -- Foreign key linking to snapshot, deletes if snapshot deleted
    term TEXT NOT NULL,  -- The trending keyword
    count INTEGER NOT NULL  -- Frequency of the term
);

CREATE TABLE IF NOT EXISTS trend_examples (  -- Create table for example posts
    id SERIAL PRIMARY KEY,  -- Unique ID for each example record
    snapshot_id INTEGER NOT NULL REFERENCES trend_snapshots(id) ON DELETE CASCADE,  -- Foreign key linking to snapshot
    term TEXT NOT NULL,  -- Associated trend term
    count INTEGER NOT NULL,  -- Frequency count of the term
    post_id TEXT,  -- ID of the example post
    author TEXT,  -- Author of the post
    post_timestamp TEXT,  -- Timestamp of the post
    text TEXT  -- Content/text of the post
);
