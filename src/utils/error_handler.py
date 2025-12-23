from aiologger import Logger

class ApplicationError(Exception):
    """Custom exception for application-specific errors."""
    pass

def handle_exception(
    logger: Logger,
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