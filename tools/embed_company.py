"""Company Document Embedding tool."""

from argparse import ArgumentParser
from logging import basicConfig, getLogger
from pathlib import Path

from app.config import CHROMADB_HOST, CHROMADB_PORT, EMBEDDING_MODEL, LOG_FORMAT
from app.config import LOG_LEVEL, LOG_STYLE
from app.embeddings import embed_directory


# Setup the global logger.
basicConfig(level=LOG_LEVEL, style=LOG_STYLE, format=LOG_FORMAT)

# Instantiate local logger.
_logger = getLogger(__name__)


if __name__ == '__main__':
    # Parse input arguments.
    _logger.debug('PARSING ARGUMENTS')
    parser = ArgumentParser(description='Generate RAG embeddings.')
    parser.add_argument('-s', '--sources', help='Source data folder', required=True)
    parser.add_argument('-c', '--company', help='Company name', required=True)
    parser.add_argument('-z', '--size', help='Chunk size', default=1000, type=int)
    parser.add_argument('-o', '--overlap', help='Chunk overlap', default=100, type=int)
    args = parser.parse_args()
    _logger.debug(f'PARSED ARGUMENTS: {vars(args)}')
    # Sanitize input: Sources path must exist and be a folder.
    sources_path = Path(args.sources)
    if not sources_path.is_dir():
        print(f'Sources path is not a valid folder: "{args.sources}"')
        exit()
    # Embed documents.
    metadata = {'company': args.company}
    embed_directory(sources_path, metadata, model_name=EMBEDDING_MODEL,
                    chunk_size=args.size, chunk_overlap=args.overlap,
                    db_host=CHROMADB_HOST, db_port=CHROMADB_PORT)
