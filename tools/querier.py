"""Chroma Vectorstore REPL querier."""

from argparse import ArgumentParser
from logging import getLogger

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import CHROMADB_HOST, CHROMADB_PORT, EMBEDDING_MODEL, LLM_API_KEY
from app.config import LLM_API_URL


# Instantiate local logger.
_logger = getLogger(__name__)


def retrieve_company_data_from_vectorstore(query, company, vectorstore, n_vectors=10):
    """Run similarity search filtered by company."""
    return vectorstore.similarity_search(query, k=n_vectors, filter={'company': company})


# Manual query function.
def query_policies(model_name):
    """Query airline policies."""
    _logger.info('LOADING VECTORSTORE')
    embedding_model = OpenAIEmbeddings(model=model_name,
                                       api_key=LLM_API_KEY, base_url=LLM_API_URL)
    vectorstore = Chroma(embedding_function=embedding_model,
                         host=CHROMADB_HOST, port=CHROMADB_PORT)
    _logger.info('READY FOR QUERIES')
    query = None
    quitters = ('q', 'exit')
    companies = ('AmericanAirlines', 'Delta', 'United')
    while not query or query.lower() not in quitters:
        print('===============================')
        company = input(f'Please choose a company ({companies}) or {quitters} to quit: ')
        if company.lower() in quitters:  # Guard clause.
            break
        elif company not in companies:
            print('Sorry, unknown company.')
        else:
            query = input(f'Please cast your question or {quitters} to quit:\n\n\t')
            if query.lower() in quitters:  # Guard clause.
                break
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
    parser = ArgumentParser(description='Query RAG embeddings.')
    args = parser.parse_args()
    _logger.debug(f'PARSED ARGUMENTS: {vars(args)}')
    # Retrieve vectors REPL.
    query_policies(model_name=EMBEDDING_MODEL)
