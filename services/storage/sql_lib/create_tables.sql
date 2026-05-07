
--------------------------------------
-- DDL create tables for storing trends and sample post
-------------------------------------

CREATE TABLE IF NOT EXISTS trend_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    posts_processed INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS trend_terms (
    id SERIAL PRIMARY KEY,
    snapshot_id INTEGER NOT NULL REFERENCES trend_snapshots(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS trend_examples (
    id SERIAL PRIMARY KEY,
    snapshot_id INTEGER NOT NULL REFERENCES trend_snapshots(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    count INTEGER NOT NULL,
    post_id TEXT,
    author TEXT,
    post_timestamp TEXT,
    text TEXT
);