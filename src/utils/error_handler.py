import logging
import sys

class ApplicationError(Exception):
    """Custom exception for application-specific errors."""
    pass

def handle_exception(
    logger: logging.Logger,
    exception: Exception,
    message: str = "An unexpected error occurred",
    reraise: bool = False,
):
    """
    Handles an exception by logging it and optionally re-raising it.

    Args:
        logger: The logger instance to use for logging the exception.
        exception: The exception object that was caught.
        message: A descriptive message about the context of the error.
        reraise: If True, the exception will be re-raised after logging.
    """
    error_type = type(exception).__name__
    error_message = str(exception)
    logger.error(f"{message}: {error_type} - {error_message}", exc_info=True)

    if reraise:
        raise exception

def configure_logging(
    log_file: str = "application.log", level=logging.INFO, stream_output=sys.stdout
):
    """
    Configures basic logging for the application.

    Args:
        log_file: The name of the file to log to.
        level: The minimum logging level to capture.
        stream_output: The stream to output logs to (e.g., sys.stdout, sys.stderr).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(stream_output),
        ],
    )