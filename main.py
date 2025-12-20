from sys import exit as sysexit
import logging
from src.utils.config import ConfigManager, ConfigurationError
from src.utils.error_handler import configure_logging, handle_exception


def main():
    configure_logging(log_file="main.log", level=logging.INFO)
    logger: logging.Logger = logging.getLogger(__name__)

    try:
        logger.info("Loading configuration...")
        config = ConfigManager()

        logger.debug("Retrieving bot token...")
        token = config.get("TOKEN")

        if not token:
            handle_exception(
                logger,
                ConfigurationError("Bot token not found in configuration."),
                "Configuration error",
                reraise=True
            )

        logger.info("Configuration loaded successfully.")
    except ConfigurationError as e:
        handle_exception(logger, e, "Configuration error", reraise=False)
        sysexit(1)
    except Exception as e:
        handle_exception(logger, e, "An unexpected error occurred", reraise=False)
        sysexit(1)


if __name__ == "__main__":
    main()
