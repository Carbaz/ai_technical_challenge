"""Airline Policy Assistant Service configuration module.

    NOTE: Any variable that we want to omit from the automated configuration log
    output, as passwords or secret credentials, must be added, using its system name
    (with any prefixes required) to the "SENSIBLE_FIELDS" variable at the bottom of
    this file.
"""

from logging import _nameToLevel, getLogger

from environs import Env, validate, ValidationError


# Instantiate local logger.
_logger = getLogger(__name__)

env = Env()
env.read_env('.env', recurse=False)

try:
    with env.prefixed('FCM_APA_'):

        # ##################### LOGGER CONFIGURATION:

        # Application log level.
        LOG_LEVEL = env.log_level('LOG_LEVEL', 'INFO')
        # Application log messages format style.
        LOG_STYLE = env.str('LOG_STYLE', '{')
        # Application log messages format.
        LOG_FORMAT = env.str('LOG_FORMAT',
                            '{asctime} {levelname:<8} {processName}({process})'
                            ' {threadName} {name} {lineno} > {message}')

        # ##################### API CONFIGURATION:

        # Base URL for the LLM API.
        LLM_API_URL = env.str('LLM_API_URL', None)
        # API key for the LLM service.
        LLM_API_KEY = env.str('LLM_API_KEY', None)

        # ##################### MODELS CONFIGURATION:

        # Chat model for user interactions.
        CHAT_MODEL = env.str('CHAT_MODEL', 'gpt-4.1-mini')
        # Chunking model for document splitting.
        CHUNKING_MODEL = env.str('CHUNKING_MODEL', 'gpt-5-mini')
        # Embedding model for text representation.
        EMBEDDING_MODEL = env.str('EMBEDDING_MODEL', 'text-embedding-3-small')
        # Level of PDF processing: LOW: Just text, MEDIUM: With OCR, HIGH: LLM Processing.
        PDF_PROCESSING_LEVEL = env.str('PDF_PROCESSING_LEVEL', default='MEDIUM',
                                        validate=validate.OneOf(['LOW', 'MEDIUM', 'HIGH']))

        # ##################### VECTORSTORE SERVICE CONFIGURATION:

        # Port for the ChromaDB database.
        CHROMADB_PORT = env.int('CHROMADB_PORT', 8000)
        # Hostname for the ChromaDB database.
        CHROMADB_HOST = env.str('CHROMADB_HOST', 'localhost')

        # ##################### GRADIO SERVICE CONFIGURATION:

        # Enable/disable Gradio exposure.
        GRADIO_SERVER_NAME = env.str('GRADIO_SERVER_NAME', '127.0.0.1')
        # HTTP port for the Gradio service.
        GRADIO_HTTP_PORT = env.int('GRADIO_HTTP_PORT', 7860)
except Exception as ex:
    _logger.error(f'ERROR LOADING CONFIGURATION: {ex}')
    exit(1)


# Define set of configuration fields that MUST NOT BE LOGGED/PRINTED
SENSIBLE_FIELDS = ('FCM_APA_LLM_API_KEY')


def get_conf():
    """Return configuration dict."""
    return {key: value for key, value in env.dump().items()
            if key not in SENSIBLE_FIELDS}


def log_conf(level=_nameToLevel['DEBUG']):
    """Print out current configuration values."""
    for var, value in sorted(get_conf().items()):
        _logger.log(level, f'{var} = {repr(value)}')


def print_conf():
    """Print out current configuration values."""
    for var, value in sorted(get_conf().items()):
        print(f'{var} = {repr(value)}')


if __name__ == '__main__':
    print_conf()
