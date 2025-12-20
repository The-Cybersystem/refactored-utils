from sys import stdout, exit as sysexit
import logging
from utils.config import ConfigManager


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler("main.log"), logging.StreamHandler(stdout)],
    )
    try:
        logger: logging.Logger = logging.getLogger(__name__)

        logger.info("Loading configuration...")
        config = ConfigManager()

        logger.debug("Retrieving bot token...")
        token = config.get("TOKEN")

        if not token:
            logger.error("Bot token not found in configuration.")
            sysexit(1)

        logger.info("Configuration loaded successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sysexit(1)


if __name__ == "__main__":
    main()
