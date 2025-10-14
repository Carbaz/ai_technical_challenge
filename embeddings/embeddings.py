"""Document Embeddings module."""

from argparse import ArgumentParser
from logging import basicConfig, getLogger
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from .llm_chunker import chunk_from_directory_using_llm


def load_text_from_directory(directory, glob=('**/*.txt', '**/*.md')):
    """Load text documents from directory."""
    return DirectoryLoader(
        path=directory,
        glob=glob,
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}).load()


def load_pdf_from_directory(directory, glob='**/*.pdf'):
    """Load PDF documents from directory."""
    return DirectoryLoader(
        path=directory,
        glob=glob,
        loader_cls=UnstructuredPDFLoader,
        loader_kwargs={"mode": "hi_res"}).load()


def load_pdf_from_directory_with_ocr(directory, glob='**/*.pdf'):
    """Load PDF documents from directory, using OCR for embedded images."""
    return DirectoryLoader(
        path=directory,
        glob=glob,
        loader_cls=UnstructuredFileLoader,
        loader_kwargs={"unstructured_kwargs": {"strategy": "hi_res"}}).load()


def update_metadata(docs: list[Document], metadata: dict):
    """Update and sanitize documents metadata."""
    for doc in docs:
        doc.metadata.update(metadata)
    return filter_complex_metadata(docs)


def chunk_documents(docs: list[Document], chunk_size=1000, chunk_overlap=100):
    """Split documents into chunks while preserving metadata."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap).split_documents(docs)


def embed_documents(docs: list[Document], embedding_model: Embeddings, persist_path):
    """Embed documents into Chroma vector storage."""
    return Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_path)


def embed_directory(directory, metadata, db_path, model_name, chunk_size, chunk_overlap):
    """Embed documents from directory."""
    embedding_model = OpenAIEmbeddings(model=model_name)

    _logger.info(f'LOADING TEXT DOCUMENTS FROM "{directory}"')
    text_documents = load_text_from_directory(directory)

    _logger.info(f'CHUNKING TEXT DOCUMENTS')
    text_chunks = chunk_documents(text_documents, chunk_size, chunk_overlap)

    _logger.info(f'LOADING PDF DOCUMENTS FROM "{directory}"')
    pdf_chunks = chunk_from_directory_using_llm(directory, chunk_size=chunk_size,
                                                chunk_overlap=chunk_overlap)

    chunks = text_chunks + pdf_chunks
    if not chunks:
        _logger.info(f'NO DOCUMENTS FOUND AT "{directory}"')
        return

    _logger.info(f'UPDATING METADATA')
    chunks = update_metadata(chunks, metadata)

    _logger.info(f'EMBEDDING DOCUMENTS')
    embed_documents(chunks, embedding_model, db_path)


# Instantiate local logger.
_logger = getLogger(__name__)


if __name__ == '__main__':
    # Application log messages format style.
    LOG_STYLE = '{'
    # Application log level.
    LOG_LEVEL = 'INFO'
    # Application log messages format.
    LOG_FORMAT = ('{asctime} {levelname:<8} {processName}({process})'
                  ' {threadName} {name} {lineno} "{message}"')
    # Define Embedding model.
    EMBEDDING_MODEL = 'text-embedding-3-small'

    # Setup the global logger.
    basicConfig(level=LOG_LEVEL, style=LOG_STYLE, format=LOG_FORMAT)

    # Parse input arguments.
    _logger.debug('PARSING ARGUMENTS')
    parser = ArgumentParser(description='Generate RAG embeddings.')
    parser.add_argument('-s', '--sources', help='Source data files folder',
                        required=True)
    parser.add_argument('-c', '--company', help='Company name',
                        required=True)
    parser.add_argument('-p', '--persistence', help='Database persistence path',
                        required=True)
    parser.add_argument('-z', '--size', help='Chunk size', default=1000, type=int)
    parser.add_argument('-o', '--overlap', help='Chunk overlap', default=100, type=int)
    args = parser.parse_args()
    _logger.debug(f'PARSED ARGUMENTS: {vars(args)}')

    # Sanitize inputs.
    # Sources path must exist and be a folder.
    sources_path = Path(args.sources)
    if not sources_path.is_dir():
        print(f'Sources path is not a valid folder: "{args.sources}"')
        exit()
    # Persistence path if exists must be a folder. (If not exists will be created later)
    persistence_path = Path(args.persistence)
    if Path(args.persistence).exists() and not Path(args.persistence).is_dir():
        print(f'Persistence path is not a valid folder: "{args.persistence}"')
        exit()

    # Embed documents.
    metadata = {'company': args.company}
    embed_directory(args.sources, metadata, args.persistence, model_name=EMBEDDING_MODEL,
                    chunk_size=args.size, chunk_overlap=args.overlap)
