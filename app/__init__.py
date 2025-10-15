"""Airline Policy Assistant Service package."""

from logging import basicConfig, getLogger

from .config import LOG_FORMAT, LOG_LEVEL, LOG_STYLE, log_conf


# Setup the global logger.
basicConfig(level=LOG_LEVEL, style=LOG_STYLE, format=LOG_FORMAT)

getLogger(__name__).info('Initialized Service')
log_conf(LOG_LEVEL)
