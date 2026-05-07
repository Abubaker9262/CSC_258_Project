# ---------------------
# Configuration file for processing service
# --------------------

import os

# Save and log a trend snapshot after this many successfully processed posts.
POSTS_LAP = int(os.getenv("POSTS_LAP","100"))  # occurence of print after reading number of post

# Number of top trends included in each saved snapshot.
TOP_TERMS = int(os.getenv("TOP_TERMS","20")) # number of words to look at

# Maximum example posts kept in memory for each tracked topic
MAX_EXAMPLES_PER_TOPIC = int(os.getenv("MAX_EXAMPLES_PER_TOPIC", "25"))

# Maximum total topics kept in memory before low-count topics are pruned
MAX_TRACKED_TOPICS = int(os.getenv("MAX_TRACKED_TOPICS", "500"))



# Authors ignored 
EXCLUDED_AUTHORS = {
    "did:plc:f4z2nftgrn75h7h3wucdyzaf",
}
# USer plc:f4z2nftgrn75h7h3wucdyzaf was translating words and posting them :/

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "this", "to", "was", "were", "will", "with", "you", "your",
    "i", "me", "my", "we", "our", "they", "them", "their", "but", "if",
    "so", "not", "just", "about", "what", "when", "how", "why", "can",
    "bsky","social", "one", "have", "like", "all", "now", "out","get",
    "from", "our", "your", "their", "have", "has", "had", "but", "not",
    "you", "they", "we", "he", "she", "i", "me", "my", "us", "them",
    "if", "so", "all", "too", "just", "out", "up", "down", "into", "about",
    "when", "what", "where", "there", "then", "than", "more", "most",
    "also", "through", "current", "currently", "another", "some", "like",
    "around", "friend", "thanks", "email", "customer", "apologies",
    "que","hundred","his","people","two","com","don","who","think",
    "time","would","know","eight","good","him","words","million","her","thousand"
}