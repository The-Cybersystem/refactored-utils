from sys import exit as sysexit
from src.utils.config import ConfigManager, ConfigurationError
from src.utils.error_handler import handle_exception
from src.utils.logger import setup_async_logger, setup_sync_logger

from src.core.application import Application
from src.core.container import Container


def main():
    sync_logger = setup_sync_logger()  # Synchronous logger for main.py

    try:
        sync_logger.info("Loading configuration...")
        config = ConfigManager()

        sync_logger.debug("Retrieving bot token...")
        token = config.get("TOKEN")

        if not token:
            handle_exception(
                sync_logger,  # type: ignore
                ConfigurationError("Bot token not found in configuration."),
                "Configuration error",
                reraise=True,
            )
        sync_logger.info("Configuration loaded successfully.")

        sync_logger.debug("Initializing application...")
        container = Container()
        async_logger = setup_async_logger()  # Asynchronous logger for the Application
        app = Application(
            container.bot, container, async_logger, sync_logger
        )  # Pass both loggers
        sync_logger.info("Application initialized successfully.")

        app.run(token)

    except ConfigurationError as e:
        handle_exception(
            sync_logger,  # type: ignore
            e,
            "Configuration error",
            reraise=False,
        )
        sysexit(1)
    except Exception as e:
        handle_exception(
            sync_logger,  # type: ignore
            e,
            "An unexpected error occurred",
            reraise=False,
        )
        sysexit(1)


if __name__ == "__main__":
    main()
