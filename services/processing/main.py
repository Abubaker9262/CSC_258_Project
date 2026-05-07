#-----------------------------------------------------
# Main Entry for processor service
#
# Read the normalized post from Kafka, extract and process trends(counts), save trend snapshot
#
#   -- Fault Tolerant --
#       Invalid posts are skipped instead of crashing the service.
#       The exception is re-raised so container restart policy can restart the service. (availabilty)
# 
#-----------------------------------------------------

from services.logging_utils import get_logger
from services.processing.consumer import KafkaPostConsumer
from services.processing.processor import TrendProcessor
from services.processing.config import POSTS_LAP, TOP_TERMS
from services.storage.trend_save import TrendStore


logger = get_logger("services.processing.main")

# logs the top trends with their counts
def print_top_terms(posts_processed: int, trends: list):
    logger.info("Processed %s posts", posts_processed)
    for term, count in trends:
        logger.info("Top trending term: %s=%s", term, count)


if __name__ == "__main__":

    consumer = KafkaPostConsumer()      # reads post from Kafka
    processor = TrendProcessor()        # extracts and counts trends
    store = TrendStore()                # stores the results

    try:
        logger.info("Starting processing service.")

        for post in consumer.read_posts():                  # keep reading from kafka
            processed = processor.process_post(post)        # passes post from kafka to processor.
                
        # processed = False if the post was invalid, empty, excluded, or had no useful topics
            if not processed:
                logger.warning("Skipped invalid or unusable post during processing.")
                continue

        # processed = True if the post was usable and added to trend counts
            if processor.posts_processed % POSTS_LAP == 0:              # number of post to go through to save snapshot
                trends = processor.top_terms(limit=TOP_TERMS)           # the top trending terms
                examples = processor.top_examples(limit=TOP_TERMS)      # actual post that have top trending terms
                print_top_terms(processor.posts_processed, trends)      # log it

                store.save_snapshot(processor.posts_processed, trends)          # Save the trends
                store.save_example_posts(processor.posts_processed, examples)   # Save the post examples

    except Exception:
        logger.exception("Processing service stopped because of an unexpected error.")
        raise               # Docker can see the process crashed and restart it if configured
    
    finally:
        if consumer.invalid_messages_skipped:
            logger.warning(
                "Invalid Kafka messages skipped: %s",
                consumer.invalid_messages_skipped,
            )

        if processor.invalid_posts_skipped:
            logger.warning(
                "Invalid posts skipped during processing: %s",
                processor.invalid_posts_skipped,
            )

        if processor.pruned_topics:
            logger.warning("Tracked topics pruned from memory: %s", processor.pruned_topics)

        consumer.close()
        logger.info("Processing service shut down.")
