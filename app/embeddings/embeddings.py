"""Document Embeddings module."""

from logging import getLogger

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.config import LLM_API_KEY, LLM_API_URL, PDF_PROCESSING_LEVEL

from .llm_chunker import chunk_from_directory_using_llm
from .pdf_loader import MyPDFLoader


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
        loader_cls=PyPDFLoader).load()


def load_pdf_from_directory_with_ocr(directory, glob='**/*.pdf'):
    """Load PDF documents from directory, using OCR for embedded images."""
    return DirectoryLoader(
        path=directory,
        glob=glob,
        loader_cls=MyPDFLoader).load()


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


def embed_documents(docs: list[Document], model: Embeddings, db_host, db_port):
    """Embed documents into Chroma vector storage."""
    return Chroma.from_documents(documents=docs, embedding=model,
                                 host=db_host, port=db_port)


def chunk_directory_text(directory, chunk_size, chunk_overlap):
    """Chunk text documents from directory."""
    _logger.info(f'LOADING TEXT DOCUMENTS FROM "{directory}"')
    text_documents = load_text_from_directory(directory)
    _logger.info(f'CHUNKING TEXT DOCUMENTS')
    return chunk_documents(text_documents, chunk_size, chunk_overlap)


def chunk_directory_pdf(directory, chunk_size, chunk_overlap):
    """Chunk PDF documents from directory."""
    _logger.info(f'LOADING PDF DOCUMENTS FROM "{directory}"'
                 f' AT {PDF_PROCESSING_LEVEL} LEVEL')
    match PDF_PROCESSING_LEVEL:
        case 'LOW':
            _logger.info(f'LOADING PDF DOCUMENTS FROM "{directory}"')
            pdf_documents = load_pdf_from_directory(directory)
            _logger.info(f'CHUNKING PDF DOCUMENTS')
            return chunk_documents(pdf_documents, chunk_size, chunk_overlap)
        case 'MEDIUM':
            _logger.info(f'LOADING PDF DOCUMENTS WITH OCR FROM "{directory}"')
            pdf_documents = load_pdf_from_directory_with_ocr(directory)
            _logger.info(f'CHUNKING PDF DOCUMENTS')
            return chunk_documents(pdf_documents, chunk_size, chunk_overlap)
        case 'HIGH':
            _logger.info(f'LOADING AND CHUNKING WITH LLM FROM "{directory}')
            return chunk_from_directory_using_llm(directory, chunk_size=chunk_size,
                                                  chunk_overlap=chunk_overlap)


def embed_directory(directory, metadata, model_name,
                    chunk_size, chunk_overlap, db_host, db_port):
    """Embed documents from directory."""
    # Process text and Markdown documents.
    text_chunks = chunk_directory_text(directory, chunk_size, chunk_overlap)
    # Process PDF documents.
    pdf_chunks = chunk_directory_pdf(directory, chunk_size, chunk_overlap)
    # Combine all chunks.
    chunks = text_chunks + pdf_chunks
    if not chunks:
        _logger.info(f'NO DOCUMENTS FOUND AT "{directory}"')
        return
    # Update metadata and embed all chunks.
    _logger.info(f'UPDATING METADATA')
    chunks = update_metadata(chunks, metadata)
    embedding_model = OpenAIEmbeddings(model=model_name,
                                       api_key=LLM_API_KEY, base_url=LLM_API_URL)
    _logger.info(f'EMBEDDING DOCUMENTS')
    embed_documents(chunks, embedding_model, db_host, db_port)


def cleanup_embeddings(db_host, db_port, filter=None):
    """Clean up all embeddings from the vector storage."""
    vectorstore = Chroma(host=db_host, port=db_port)
    if filter:
        vectorstore.delete(where=filter)
    else:
        if all_ids := vectorstore.get()['ids']:
            vectorstore.delete(ids=all_ids)


# Instantiate local logger.
_logger = getLogger(__name__)
