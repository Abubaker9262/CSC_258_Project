INSERT INTO trend_examples (
    snapshot_id,
    term,
    count,
    post_id,
    author,
    post_timestamp,
    text
)
VALUES (%s, %s, %s, %s, %s, %s, %s);
