"""
Description:
This SQL query inserts example posts related to trending terms into the trend_examples table.
It uses parameterized placeholders to securely store data such as term, count, author, and post content.
This allows the system to link trends with real posts for better context on the dashboard.
"""
    
INSERT INTO trend_examples (  -- Insert a new record into trend_examples table
    snapshot_id,  -- Reference to the related snapshot
    term,  -- Trending keyword
    count,  -- Frequency of the term
    post_id,  -- ID of the example post
    author,  -- Author of the post
    post_timestamp,  -- Timestamp of the original post
    text  -- Content of the example post
)
VALUES (%s, %s, %s, %s, %s, %s, %s);  -- Parameterized placeholders for safe insertion
