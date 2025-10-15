"""ChromaDB Embeddings clean up tool."""

from argparse import ArgumentParser
from logging import getLogger

from app.config import CHROMADB_HOST, CHROMADB_PORT
from app.embeddings import cleanup_embeddings


# Instantiate local logger.
_logger = getLogger(__name__)


if __name__ == '__main__':
    # Parse input arguments.
    _logger.debug('PARSING ARGUMENTS')
    parser = ArgumentParser(description='Clean up ChromaDB embeddings.')
    args = parser.parse_args()
    _logger.debug(f'PARSED ARGUMENTS: {vars(args)}')
    cleanup_embeddings(db_host=CHROMADB_HOST, db_port=CHROMADB_PORT)
