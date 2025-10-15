"""Document Embeddings package."""

from logging import getLogger

from .embeddings import chunk_documents, cleanup_embeddings, embed_directory
from .embeddings import embed_documents, load_pdf_from_directory
from .embeddings import load_pdf_from_directory_with_ocr, load_text_from_directory
from .embeddings import update_metadata
from .llm_chunker import chunk_from_directory_using_llm, chunk_using_llm


__all__ = ['chunk_documents', 'cleanup_embeddings', 'embed_directory',
           'embed_documents', 'load_pdf_from_directory',
           'load_pdf_from_directory_with_ocr', 'load_text_from_directory',
           'update_metadata',
           'chunk_from_directory_using_llm', 'chunk_using_llm']

# Instantiate local logger.
_logger = getLogger(__name__)

# Initial embedders log.
_logger.info('EMBEDDERS SET UP')
