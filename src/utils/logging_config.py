import logging
import sys

from src.config import settings


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Logs are written to stdout so Docker and external
    log collectors can capture them.
    """

    logging.basicConfig(
        level=getattr(
            logging,
            settings.log_level.upper(),
            logging.INFO,
        ),
        format=LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )