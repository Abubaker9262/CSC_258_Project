SELECT
    s.id,
    s.timestamp,
    s.posts_processed,
    t.term,
    t.count
FROM trend_snapshots s
JOIN trend_terms t ON t.snapshot_id = s.id
WHERE s.id = (
    SELECT snapshot_id
    FROM trend_terms
    ORDER BY snapshot_id DESC
    LIMIT 1
)
ORDER BY t.count DESC, t.term;
