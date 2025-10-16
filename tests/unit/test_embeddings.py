"""Unit tests for app.embeddings.embeddings module."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from langchain_core.documents import Document

from app.embeddings.embeddings import (
    chunk_directory_pdf,
    chunk_directory_text,
    chunk_documents,
    cleanup_embeddings,
    embed_directory,
    embed_documents,
    load_pdf_from_directory,
    load_pdf_from_directory_with_ocr,
    load_text_from_directory,
    update_metadata,
)


class TestLoadTextFromDirectory:
    """Test suite for load_text_from_directory function."""

    @patch('app.embeddings.embeddings.DirectoryLoader')
    def test_load_text_with_default_glob(self, mock_loader_class):
        """Test loading text files with default glob patterns."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = [Document(page_content='test')]
        mock_loader_class.return_value = mock_loader

        result = load_text_from_directory('/test/dir')

        # Verify DirectoryLoader was called with correct parameters
        mock_loader_class.assert_called_once()
        call_kwargs = mock_loader_class.call_args.kwargs
        assert call_kwargs['path'] == '/test/dir'
        assert call_kwargs['glob'] == ('**/*.txt', '**/*.md')
        assert call_kwargs['loader_kwargs'] == {'encoding': 'utf-8'}

    @patch('app.embeddings.embeddings.DirectoryLoader')
    def test_load_text_with_custom_glob(self, mock_loader_class):
        """Test loading text files with custom glob pattern."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_class.return_value = mock_loader

        load_text_from_directory('/test/dir', glob='**/*.custom')

        call_kwargs = mock_loader_class.call_args.kwargs
        assert call_kwargs['glob'] == '**/*.custom'


class TestLoadPDFFromDirectory:
    """Test suite for PDF loading functions."""

    @patch('app.embeddings.embeddings.DirectoryLoader')
    def test_load_pdf_basic(self, mock_loader_class):
        """Test basic PDF loading without OCR."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = [
            Document(page_content='pdf content')
        ]
        mock_loader_class.return_value = mock_loader

        result = load_pdf_from_directory('/test/dir')

        mock_loader_class.assert_called_once()
        call_kwargs = mock_loader_class.call_args.kwargs
        assert call_kwargs['path'] == '/test/dir'
        assert call_kwargs['glob'] == '**/*.pdf'
        assert call_kwargs['loader_kwargs'] == {"mode": "hi_res"}

    @patch('app.embeddings.embeddings.DirectoryLoader')
    def test_load_pdf_with_ocr(self, mock_loader_class):
        """Test PDF loading with OCR enabled."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_class.return_value = mock_loader

        load_pdf_from_directory_with_ocr('/test/dir')

        call_kwargs = mock_loader_class.call_args.kwargs
        assert call_kwargs['path'] == '/test/dir'
        assert call_kwargs['loader_kwargs'] == {
            "unstructured_kwargs": {"strategy": "hi_res"}
        }

    @patch('app.embeddings.embeddings.DirectoryLoader')
    def test_load_pdf_custom_glob(self, mock_loader_class):
        """Test PDF loading with custom glob pattern."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_class.return_value = mock_loader

        load_pdf_from_directory('/test/dir', glob='**/special/*.pdf')

        call_kwargs = mock_loader_class.call_args.kwargs
        assert call_kwargs['glob'] == '**/special/*.pdf'


class TestUpdateMetadata:
    """Test suite for update_metadata function."""

    @patch('app.embeddings.embeddings.filter_complex_metadata')
    def test_update_metadata_adds_to_documents(
        self, mock_filter
    ):
        """Test that metadata is added to all documents."""
        docs = [
            Document(
                page_content='doc1', metadata={'source': 'file1.txt'}
            ),
            Document(
                page_content='doc2', metadata={'source': 'file2.txt'}
            ),
        ]
        mock_filter.return_value = docs

        metadata = {'company': 'TestCo', 'type': 'policy'}
        result = update_metadata(docs, metadata)

        # Verify metadata was updated
        assert docs[0].metadata['company'] == 'TestCo'
        assert docs[0].metadata['type'] == 'policy'
        assert docs[1].metadata['company'] == 'TestCo'
        # Verify filter was called
        mock_filter.assert_called_once_with(docs)

    @patch('app.embeddings.embeddings.filter_complex_metadata')
    def test_update_metadata_empty_list(self, mock_filter):
        """Test update_metadata with empty document list."""
        docs = []
        mock_filter.return_value = docs

        result = update_metadata(docs, {'company': 'TestCo'})

        assert result == []
        mock_filter.assert_called_once()


class TestChunkDocuments:
    """Test suite for chunk_documents function."""

    @patch('app.embeddings.embeddings.RecursiveCharacterTextSplitter')
    def test_chunk_documents_default_params(self, mock_splitter_class):
        """Test chunking with default parameters."""
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [
            Document(page_content='chunk1'),
            Document(page_content='chunk2'),
        ]
        mock_splitter_class.return_value = mock_splitter

        docs = [Document(page_content='long document content')]
        result = chunk_documents(docs)

        # Verify splitter was created with defaults
        mock_splitter_class.assert_called_once_with(
            chunk_size=1000, chunk_overlap=100
        )
        # Verify split_documents was called
        mock_splitter.split_documents.assert_called_once_with(docs)
        assert len(result) == 2

    @patch('app.embeddings.embeddings.RecursiveCharacterTextSplitter')
    def test_chunk_documents_custom_params(self, mock_splitter_class):
        """Test chunking with custom chunk size and overlap."""
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = []
        mock_splitter_class.return_value = mock_splitter

        docs = [Document(page_content='text')]
        chunk_documents(docs, chunk_size=500, chunk_overlap=50)

        mock_splitter_class.assert_called_once_with(
            chunk_size=500, chunk_overlap=50
        )


class TestEmbedDocuments:
    """Test suite for embed_documents function."""

    @patch('app.embeddings.embeddings.Chroma')
    def test_embed_documents_creates_vectorstore(self, mock_chroma_class):
        """Test that embed_documents creates Chroma vectorstore."""
        mock_vectorstore = MagicMock()
        mock_chroma_class.from_documents.return_value = mock_vectorstore

        docs = [Document(page_content='content')]
        mock_model = MagicMock()

        result = embed_documents(docs, mock_model, 'localhost', 8000)

        # Verify Chroma.from_documents was called correctly
        mock_chroma_class.from_documents.assert_called_once_with(
            documents=docs, embedding=mock_model, host='localhost', port=8000
        )
        assert result == mock_vectorstore


class TestChunkDirectoryText:
    """Test suite for chunk_directory_text function."""

    @patch('app.embeddings.embeddings.chunk_documents')
    @patch('app.embeddings.embeddings.load_text_from_directory')
    def test_chunk_directory_text(
        self, mock_load, mock_chunk
    ):
        """Test text directory chunking workflow."""
        mock_docs = [Document(page_content='text doc')]
        mock_load.return_value = mock_docs
        mock_chunk.return_value = [
            Document(page_content='chunk1'),
            Document(page_content='chunk2'),
        ]

        result = chunk_directory_text('/test/dir', 1000, 100)

        mock_load.assert_called_once_with('/test/dir')
        mock_chunk.assert_called_once_with(mock_docs, 1000, 100)
        assert len(result) == 2


class TestChunkDirectoryPDF:
    """Test suite for chunk_directory_pdf function."""

    @patch('app.embeddings.embeddings.PDF_PROCESSING_LEVEL', 'LOW')
    @patch('app.embeddings.embeddings.chunk_documents')
    @patch('app.embeddings.embeddings.load_pdf_from_directory')
    def test_chunk_directory_pdf_low_level(
        self, mock_load, mock_chunk
    ):
        """Test PDF chunking with LOW processing level."""
        mock_docs = [Document(page_content='pdf content')]
        mock_load.return_value = mock_docs
        mock_chunk.return_value = [Document(page_content='chunk')]

        result = chunk_directory_pdf('/test/dir', 1000, 100)

        mock_load.assert_called_once_with('/test/dir')
        mock_chunk.assert_called_once_with(mock_docs, 1000, 100)

    @patch('app.embeddings.embeddings.PDF_PROCESSING_LEVEL', 'MEDIUM')
    @patch('app.embeddings.embeddings.chunk_documents')
    @patch('app.embeddings.embeddings.load_pdf_from_directory_with_ocr')
    def test_chunk_directory_pdf_medium_level(
        self, mock_load_ocr, mock_chunk
    ):
        """Test PDF chunking with MEDIUM processing level (OCR)."""
        mock_docs = [Document(page_content='ocr content')]
        mock_load_ocr.return_value = mock_docs
        mock_chunk.return_value = [Document(page_content='chunk')]

        result = chunk_directory_pdf('/test/dir', 1000, 100)

        mock_load_ocr.assert_called_once_with('/test/dir')
        mock_chunk.assert_called_once()

    @patch('app.embeddings.embeddings.PDF_PROCESSING_LEVEL', 'HIGH')
    @patch('app.embeddings.embeddings.chunk_from_directory_using_llm')
    def test_chunk_directory_pdf_high_level(
        self, mock_llm_chunk
    ):
        """Test PDF chunking with HIGH processing level (LLM)."""
        mock_llm_chunk.return_value = [Document(page_content='llm chunk')]

        result = chunk_directory_pdf('/test/dir', 1000, 100)

        mock_llm_chunk.assert_called_once_with(
            '/test/dir', chunk_size=1000, chunk_overlap=100
        )


class TestEmbedDirectory:
    """Test suite for embed_directory function."""

    @patch('app.embeddings.embeddings.embed_documents')
    @patch('app.embeddings.embeddings.OpenAIEmbeddings')
    @patch('app.embeddings.embeddings.update_metadata')
    @patch('app.embeddings.embeddings.chunk_directory_pdf')
    @patch('app.embeddings.embeddings.chunk_directory_text')
    def test_embed_directory_success(
        self,
        mock_text_chunk,
        mock_pdf_chunk,
        mock_update_meta,
        mock_embeddings_class,
        mock_embed,
    ):
        """Test complete embed_directory workflow."""
        # Setup mocks
        mock_text_chunk.return_value = [
            Document(page_content='text chunk')
        ]
        mock_pdf_chunk.return_value = [Document(page_content='pdf chunk')]
        mock_update_meta.return_value = [
            Document(
                page_content='chunk', metadata={'company': 'TestCo'}
            )
        ]
        mock_embedding_model = MagicMock()
        mock_embeddings_class.return_value = mock_embedding_model

        # Execute
        embed_directory(
            '/test/dir',
            {'company': 'TestCo'},
            'test-model',
            1000,
            100,
            'localhost',
            8000,
        )

        # Verify workflow
        mock_text_chunk.assert_called_once_with('/test/dir', 1000, 100)
        mock_pdf_chunk.assert_called_once_with('/test/dir', 1000, 100)
        mock_update_meta.assert_called_once()
        mock_embeddings_class.assert_called_once()
        mock_embed.assert_called_once()

    @patch('app.embeddings.embeddings.chunk_directory_pdf')
    @patch('app.embeddings.embeddings.chunk_directory_text')
    def test_embed_directory_no_documents(
        self, mock_text_chunk, mock_pdf_chunk
    ):
        """Test embed_directory when no documents are found."""
        # Return empty lists
        mock_text_chunk.return_value = []
        mock_pdf_chunk.return_value = []

        # Should return early without embedding
        result = embed_directory(
            '/empty/dir', {}, 'model', 1000, 100, 'localhost', 8000
        )

        assert result is None


class TestCleanupEmbeddings:
    """Test suite for cleanup_embeddings function."""

    @patch('app.embeddings.embeddings.Chroma')
    def test_cleanup_all_embeddings(self, mock_chroma_class):
        """Test cleaning up all embeddings without filter."""
        mock_vectorstore = MagicMock()
        mock_vectorstore.get.return_value = {
            'ids': ['id1', 'id2', 'id3']
        }
        mock_chroma_class.return_value = mock_vectorstore

        cleanup_embeddings('localhost', 8000)

        # Verify vectorstore was created
        mock_chroma_class.assert_called_once_with(
            host='localhost', port=8000
        )
        # Verify delete was called with all ids
        mock_vectorstore.delete.assert_called_once_with(
            ids=['id1', 'id2', 'id3']
        )

    @patch('app.embeddings.embeddings.Chroma')
    def test_cleanup_with_filter(self, mock_chroma_class):
        """Test cleaning up embeddings with a filter."""
        mock_vectorstore = MagicMock()
        mock_chroma_class.return_value = mock_vectorstore

        cleanup_embeddings(
            'localhost', 8000, filter={'company': 'TestCo'}
        )

        # Verify delete was called with filter
        mock_vectorstore.delete.assert_called_once_with(
            where={'company': 'TestCo'}
        )

    @patch('app.embeddings.embeddings.Chroma')
    def test_cleanup_empty_database(self, mock_chroma_class):
        """Test cleanup when database is empty."""
        mock_vectorstore = MagicMock()
        mock_vectorstore.get.return_value = {'ids': []}
        mock_chroma_class.return_value = mock_vectorstore

        cleanup_embeddings('localhost', 8000)

        # Should not call delete if no ids
        mock_vectorstore.delete.assert_not_called()
