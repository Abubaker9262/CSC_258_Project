"""
Description:This query retrieves example posts for the most recent trend snapshot by joining snapshot and example tables.
It selects relevant fields such as term, count, and post details. The results are sorted by term frequency in descending order for better analysis.
"""
SELECT
    s.id,  -- Snapshot ID
    s.timestamp,  -- Timestamp of the snapshot
    s.posts_processed,  -- Number of posts processed
    e.term,  -- Trending term
    e.count,  -- Frequency of the term
    e.post_id,  -- ID of the example post
    e.author,  -- Author of the post
    e.post_timestamp,  -- Timestamp of the post
    e.text  -- Content of the post
FROM trend_snapshots s  -- Main snapshots table (aliased as s)
JOIN trend_examples e ON e.snapshot_id = s.id  -- Join examples linked to snapshot
WHERE s.id = (  -- Filter to only the latest snapshot
    SELECT snapshot_id  -- Get latest snapshot ID from examples table
    FROM trend_examples
    ORDER BY snapshot_id DESC  -- Order by newest snapshot
    LIMIT 1  -- Take only the latest one
)
ORDER BY e.count DESC, e.term;  -- Sort by highest frequency, then alphabetically
