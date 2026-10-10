import logging
import time

from pipeline import run

INTERVAL_SECONDS = 300  # every 5 minutes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    logging.info("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            try:
                run()
            except Exception:
                logging.exception("Pipeline run failed, will retry next cycle")
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")