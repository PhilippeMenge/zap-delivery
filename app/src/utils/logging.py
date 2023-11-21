import logging

from src.config import LOGGING_LEVEL


def get_configured_logger(name: str) -> logging.Logger:
    """### Get a logger instance properly configured.

    Args:
        name (str): The logger name. (usually its the __name__ variable)

    Returns:
        logging.Logger: The logger instance.
    """
    logger = logging.getLogger(name)

    logger.setLevel(LOGGING_LEVEL)

    formatter = logging.Formatter(
        "[%(levelname)s : %(name)s] (%(asctime)s) %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
