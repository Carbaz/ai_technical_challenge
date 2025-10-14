"""Chroma Vectorstore REPL querier."""

from argparse import ArgumentParser
from logging import basicConfig, getLogger
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import CHROMADB_PATH, EMBEDDING_MODEL, LOG_FORMAT, LOG_LEVEL, LOG_STYLE


# Setup the global logger.
basicConfig(level=LOG_LEVEL, style=LOG_STYLE, format=LOG_FORMAT)

# Instantiate local logger.
_logger = getLogger(__name__)


def retrieve_company_data_from_vectorstore(query, company, vectorstore, n_vectors=4):
    """Run similarity search filtered by company."""
    return vectorstore.similarity_search(query, k=n_vectors, filter={'company': company})


# Manual query function.
def query_policies(db_path, model_name):
    """Query airline policies."""
    _logger.info('LOADING VECTORSTORE')
    embedding_model = OpenAIEmbeddings(model=model_name)
    vectorstore = Chroma(embedding_function=embedding_model, persist_directory=db_path)
    _logger.info('READY FOR QUERIES')
    query = None
    quitters = ('q', 'exit')
    companies = ('AmericanAirlines', 'Delta', 'United')
    while not query or query.lower() not in quitters:
        print('===============================')
        company = input(f'Please choose a company ({companies}): ')
        if company.lower() in quitters:  # Guard clause.
            break
        elif company not in companies:
            print('Sorry, unknown company.')
        else:
            query = input('Please cast your question:\n\n\t')
            vectors = retrieve_company_data_from_vectorstore(query, company, vectorstore)
            for vector in vectors:
                print('-------------------------------')
                print(vector.page_content)
    print('Bye!')


# Instantiate local logger.
_logger = getLogger(__name__)


if __name__ == '__main__':
    # Parse input arguments.
    _logger.debug('PARSING ARGUMENTS')
    parser = ArgumentParser(description='Generate RAG embeddings.')
    parser.add_argument('-p', '--persistence', help='Database persistence path',
                        default=CHROMADB_PATH)
    args = parser.parse_args()
    _logger.debug(f'PARSED ARGUMENTS: {vars(args)}')

    # Sanitize inputs.
    # Persistence path must exist and be a folder.
    persistence_path = Path(args.persistence)
    if not Path(args.persistence).is_dir():
        print(f'Persistence path is not a valid folder: "{args.persistence}"')
        exit()

    # Retrieve vectors REPL.
    query_policies(args.persistence, model_name=EMBEDDING_MODEL)
