"""Airline Policy Assistant Service configuration module.

    NOTE: Any variable that we want to omit from the automated configuration log
    output, as passwords or secret credentials, must be added, using its system name
    (with any prefixes required) to the "SENSIBLE_FIELDS" variable at the bottom of
    this file.
"""

from logging import getLogger

from environs import Env


env = Env()
env.read_env('.env', recurse=False)


with env.prefixed('FCM_APA_'):

    # ##################### LOGGER CONFIGURATION:

    # Application log messages format style.
    LOG_STYLE = env.str('LOG_STYLE', '{')
    # Application log messages format.
    LOG_FORMAT = env.str('LOG_FORMAT',
                         '{asctime} {levelname:<8} {processName}({process})'
                         ' {threadName} {name} {lineno} "{message}"')

    # ##################### LOG LEVELS CONFIGURATION:

    # Application log level.
    LOG_LEVEL = env.log_level('LOG_LEVEL', 'INFO')
    # Database service log level.
    DATABASE_LOG_LEVEL = env.log_level('DATABASE_LOG_LEVEL', 'ERROR')

    # ##################### VECTORSTORE SERVICE CONFIGURATION:

    # Path to the ChromaDB database.
    CHROMADB_PATH = env.str('CHROMADB_PATH', 'chromadb')

    # ##################### VECTORSTORE SERVICE CONFIGURATION:

    # Chat model for user interactions.
    CHAT_MODEL = env.str('CHAT_MODEL', 'gpt-5-mini')
    # Chunking model for document splitting.
    CHUNKING_MODEL = env.str('CHUNKING_MODEL', 'gpt-5-mini')
    # Embedding model for text representation.
    EMBEDDING_MODEL = env.str('EMBEDDING_MODEL', 'text-embedding-3-small')


# Define set of configuration fields that MUST NOT BE LOGGED/PRINTED
SENSIBLE_FIELDS = ()
# SENSIBLE_FIELDS = ('DATABASE_PASS', 'DATABASE_URI')


def get_conf():
    """Return configuration dict."""
    return {key: value for key, value in env.dump().items()
            if key not in SENSIBLE_FIELDS}


def log_conf():
    """Print out current configuration values."""
    for var, value in sorted(get_conf().items()):
        _logger.debug(f'{var} = {repr(value)}')


def print_conf():
    """Print out current configuration values."""
    for var, value in sorted(get_conf().items()):
        print(f'{var} = {repr(value)}')


# Instantiate local logger.
_logger = getLogger(__name__)


if __name__ == '__main__':
    print_conf()
