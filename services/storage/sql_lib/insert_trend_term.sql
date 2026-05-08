"""
Description:
This query inserts individual trending terms into the trend_terms table and links them to a specific snapshot using snapshot_id. 
It stores the term and its frequency count. Parameterized values ensure safe and efficient database operations.
"""
INSERT INTO trend_terms (snapshot_id, term, count)  -- Insert a trend term linked to a snapshot
VALUES (%s, %s, %s);  -- Parameterized values for snapshot ID, term, and count
