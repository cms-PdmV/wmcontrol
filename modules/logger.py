"""
Manages the logger configuration.

Most of the modules in this code base are used in embedding
batch jobs, therefore, only enable handlers to
the standard output.
"""
import logging
import sys

def create_logger(level=logging.INFO):
    """
    Creates a logger.

    Args:
        level (int): Logger's level
    Returns:
        logging.Logger: Logger to records events in
            the standard output.
    """
    logger = logging.getLogger(__name__)
    date_fmt = '%Y-%m-%d %H:%M:%S %z'
    logging_fmt = (
        '[%(levelname)s][%(filename)s]'
        '[%(asctime)s]: %(message)s'
    )
    logger_format = logging.Formatter(fmt=logging_fmt, datefmt=date_fmt)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level=level)
    console_handler.setFormatter(fmt=logger_format)

    logger.handlers = []
    logger.addHandler(console_handler)
    return logger
