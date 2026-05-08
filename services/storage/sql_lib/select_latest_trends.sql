"""
Description:This query retrieves trending terms from the most recent snapshot by joining the snapshot and term tables.
It selects term names and their frequencies along with snapshot details. The results are sorted by highest frequency to highlight the most important trends.
"""

SELECT
    s.id,  -- Snapshot ID
    s.timestamp,  -- Timestamp of the snapshot
    s.posts_processed,  -- Number of posts processed
    t.term,  -- Trending term
    t.count  -- Frequency of the term
FROM trend_snapshots s  -- Snapshot table (alias s)
JOIN trend_terms t ON t.snapshot_id = s.id  -- Join trend terms linked to snapshot
WHERE s.id = (  -- Filter to only the latest snapshot
    SELECT snapshot_id  -- Get latest snapshot ID
    FROM trend_terms
    ORDER BY snapshot_id DESC  -- Order by newest snapshot
    LIMIT 1  -- Select most recent snapshot
)
ORDER BY t.count DESC, t.term;  -- Sort by highest frequency, then alphabetically
