import os


# -----------------------------------------------------
# Processing service settings.
#
#   -- Scalability / Availability --
#   Bounds are used so the processor can run continuously without storing
#   unlimited topics or unlimited example posts in memory.
#
#   -- Open Design --
#   Runtime limits can be adjusted through environment variables without
#   changing processing logic.
#
#   -- Transparency --
#   Snapshot and top-term settings control how often trends are written and
#   how many results are exposed to storage/dashboard.
# -----------------------------------------------------

# Save and log a trend snapshot after this many successfully processed posts.
POSTS_LAP = 100  # occurence of print after reading number of post

# Number of top trends included in each saved snapshot.
TOP_TERMS = 20 # number of words to look at

# Maximum example posts kept in memory for each tracked topic.
MAX_EXAMPLES_PER_TOPIC = int(os.getenv("MAX_EXAMPLES_PER_TOPIC", "25"))

# Maximum total topics kept in memory before low-count topics are pruned.
MAX_TRACKED_TOPICS = int(os.getenv("MAX_TRACKED_TOPICS", "500"))

# Authors in this set are ignored during trend processing.
EXCLUDED_AUTHORS = {
    "did:plc:f4z2nftgrn75h7h3wucdyzaf",
}
