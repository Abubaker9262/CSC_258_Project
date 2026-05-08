"""
Description:
This query inserts a new trend snapshot into the trend_snapshots table with a timestamp and the number of processed posts.
It uses parameterized inputs for security and efficiency. The query returns the generated snapshot ID, which is used to
link related trend terms and example posts.
"""

INSERT INTO trend_snapshots (timestamp, posts_processed)  -- Insert a new trend snapshot record
VALUES (%s, %s)  -- Parameterized values for timestamp and processed posts
RETURNING id;  -- Return the generated snapshot ID after insertion
