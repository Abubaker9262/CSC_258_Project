INSERT INTO trend_snapshots (timestamp, posts_processed)
VALUES (%s, %s)
RETURNING id;
