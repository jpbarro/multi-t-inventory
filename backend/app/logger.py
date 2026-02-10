"""
Global logger for the multi-t-inventory backend.
Import `logger` or use `get_logger(__name__)` in any module.
"""
import logging
import os
import sys

# Logger name used across the app
LOG_NAME = "multi-t-inventory"

# Default level; override with LOG_LEVEL env (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _setup_logger() -> logging.Logger:
    """Create and configure the global application logger."""
    log = logging.getLogger(LOG_NAME)
    if log.handlers:
        return log 

    log.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    log.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    log.addHandler(handler)

    return log


# Global logger instance — use this or get_logger(__name__)
logger = _setup_logger()


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a child logger for a module. Use in other files:
        from logger import get_logger
        log = get_logger(__name__)
    """
    if name is None:
        return logger
    return logger.getChild(name)
