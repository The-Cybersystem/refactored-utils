from sys import stdout
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler(stdout)],
)

logger = logging.getLogger(__name__)

logger.info("Starting bot...")

logger.debug("Retrieving bot token...")
token = config.get("TOKEN")
