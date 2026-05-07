SELECT
    s.id,
    s.timestamp,
    s.posts_processed,
    e.term,
    e.count,
    e.post_id,
    e.author,
    e.post_timestamp,
    e.text
FROM trend_snapshots s
JOIN trend_examples e ON e.snapshot_id = s.id
WHERE s.id = (
    SELECT snapshot_id
    FROM trend_examples
    ORDER BY snapshot_id DESC
    LIMIT 1
)
ORDER BY e.count DESC, e.term;
