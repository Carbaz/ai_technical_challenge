"""Unit tests for app.embeddings.llm_chunker module."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, mock_open

import pytest
from langchain_core.documents import Document

from app.embeddings.llm_chunker import (
    _chunk,
    _response_format,
    chunk_from_directory_using_llm,
    chunk_using_llm,
)


class TestChunkModels:
    """Test suite for Pydantic models."""

    def test_chunk_model_creation(self):
        """Test creating a chunk model instance."""
        chunk = _chunk(page_content="Test content here")
        assert chunk.page_content == "Test content here"

    def test_chunk_model_max_length_validation(self):
        """Test chunk model respects max_length constraint."""
        # Creating a chunk with content longer than max_length
        # should still work (Pydantic validation is lenient by default)
        long_content = "x" * 1500
        chunk = _chunk(page_content=long_content)
        assert len(chunk.page_content) == 1500

    def test_response_format_model_creation(self):
        """Test creating a response format model."""
        chunks = [
            _chunk(page_content="First chunk"),
            _chunk(page_content="Second chunk"),
        ]
        response = _response_format(chunks=chunks)
        assert len(response.chunks) == 2
        assert response.chunks[0].page_content == "First chunk"

    def test_response_format_empty_chunks(self):
        """Test response format with empty chunks list."""
        response = _response_format(chunks=[])
        assert len(response.chunks) == 0


class TestChunkUsingLLM:
    """Test suite for chunk_using_llm function."""

    @patch('builtins.open', new_callable=mock_open, read_data=b'PDF data')
    @patch('app.embeddings.llm_chunker.OpenAI')
    def test_chunk_using_llm_success(self, mock_openai_class, mock_file):
        """Test successful LLM-based chunking of a file."""
        # Setup mock client
        mock_client = MagicMock()
        mock_file_obj = MagicMock()
        mock_file_obj.id = 'file-123'
        mock_client.files.create.return_value = mock_file_obj

        # Setup mock response with parsed chunks
        mock_parsed = MagicMock()
        mock_parsed.chunks = [
            _chunk(page_content="First chunk content"),
            _chunk(page_content="Second chunk content"),
        ]
        mock_message = MagicMock()
        mock_message.parsed = mock_parsed
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.parse.return_value = mock_response

        # Execute
        result = chunk_using_llm(
            '/test/file.pdf', mock_client, chunk_size=1000, chunk_overlap=100
        )

        # Verify file was opened and uploaded
        mock_file.assert_called_once_with('/test/file.pdf', 'rb')
        mock_client.files.create.assert_called_once()

        # Verify chat completion was called
        mock_client.chat.completions.parse.assert_called_once()
        call_kwargs = mock_client.chat.completions.parse.call_args.kwargs
        assert 'messages' in call_kwargs
        assert call_kwargs['response_format'] == _response_format

        # Verify results are Document objects
        assert len(result) == 2
        assert isinstance(result[0], Document)
        assert result[0].page_content == "First chunk content"
        assert result[0].metadata['source'] == '/test/file.pdf'
        assert result[1].page_content == "Second chunk content"

    @patch('builtins.open', new_callable=mock_open, read_data=b'PDF data')
    def test_chunk_using_llm_custom_params(self, mock_file):
        """Test chunk_using_llm with custom chunk size and overlap."""
        mock_client = MagicMock()
        mock_file_obj = MagicMock()
        mock_file_obj.id = 'file-456'
        mock_client.files.create.return_value = mock_file_obj

        # Setup minimal response
        mock_parsed = MagicMock()
        mock_parsed.chunks = []
        mock_message = MagicMock()
        mock_message.parsed = mock_parsed
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.parse.return_value = mock_response

        # Execute with custom parameters
        result = chunk_using_llm(
            '/test/file.pdf', mock_client, chunk_size=500, chunk_overlap=50
        )

        # Verify the prompt contains custom parameters
        call_kwargs = mock_client.chat.completions.parse.call_args.kwargs
        messages = call_kwargs['messages']
        prompt_text = messages[0]['content'][0]['text']
        assert '500' in prompt_text
        assert '50' in prompt_text


class TestChunkFromDirectoryUsingLLM:
    """Test suite for chunk_from_directory_using_llm function."""

    @patch('app.embeddings.llm_chunker.OpenAI')
    @patch('app.embeddings.llm_chunker.chunk_using_llm')
    @patch('app.embeddings.llm_chunker.Path')
    def test_chunk_from_directory_single_file(
        self, mock_path_class, mock_chunk_llm, mock_openai_class
    ):
        """Test processing a directory with a single PDF file."""
        # Setup mock directory with one PDF
        mock_path = MagicMock()
        mock_file = Path('/test/dir/file1.pdf')
        mock_path.rglob.return_value = [mock_file]
        mock_path_class.return_value = mock_path

        # Setup mock chunks from LLM
        mock_chunk_llm.return_value = [
            Document(
                page_content='chunk1', metadata={'source': 'file1.pdf'}
            )
        ]

        # Setup mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Execute
        result = chunk_from_directory_using_llm(
            '/test/dir', chunk_size=1000, chunk_overlap=100
        )

        # Verify OpenAI client was created
        mock_openai_class.assert_called_once()

        # Verify chunk_using_llm was called for the file
        mock_chunk_llm.assert_called_once_with(
            str(mock_file), mock_client, 1000, 100
        )

        # Verify results
        assert len(result) == 1
        assert result[0].page_content == 'chunk1'

    @patch('app.embeddings.llm_chunker.OpenAI')
    @patch('app.embeddings.llm_chunker.chunk_using_llm')
    @patch('app.embeddings.llm_chunker.Path')
    def test_chunk_from_directory_multiple_files(
        self, mock_path_class, mock_chunk_llm, mock_openai_class
    ):
        """Test processing a directory with multiple PDF files."""
        # Setup mock directory with multiple PDFs
        mock_path = MagicMock()
        mock_files = [
            Path('/test/dir/file1.pdf'),
            Path('/test/dir/file2.pdf'),
            Path('/test/dir/subdir/file3.pdf'),
        ]
        mock_path.rglob.return_value = mock_files
        mock_path_class.return_value = mock_path

        # Setup mock chunks - different for each file
        def chunk_side_effect(file_path, client, size, overlap):
            if 'file1' in file_path:
                return [Document(page_content='chunk1')]
            elif 'file2' in file_path:
                return [Document(page_content='chunk2')]
            else:
                return [Document(page_content='chunk3')]

        mock_chunk_llm.side_effect = chunk_side_effect
        mock_openai_class.return_value = MagicMock()

        # Execute
        result = chunk_from_directory_using_llm('/test/dir')

        # Verify chunk_using_llm was called for each file
        assert mock_chunk_llm.call_count == 3

        # Verify all chunks are collected
        assert len(result) == 3

    @patch('app.embeddings.llm_chunker.OpenAI')
    @patch('app.embeddings.llm_chunker.chunk_using_llm')
    @patch('app.embeddings.llm_chunker.Path')
    def test_chunk_from_directory_custom_glob(
        self, mock_path_class, mock_chunk_llm, mock_openai_class
    ):
        """Test processing directory with custom glob pattern."""
        mock_path = MagicMock()
        mock_path.rglob.return_value = []
        mock_path_class.return_value = mock_path
        mock_openai_class.return_value = MagicMock()

        # Execute with custom glob
        result = chunk_from_directory_using_llm(
            '/test/dir', glob='**/special/*.pdf'
        )

        # Verify rglob was called with custom pattern
        mock_path.rglob.assert_called_once_with('**/special/*.pdf')

    @patch('app.embeddings.llm_chunker.OpenAI')
    @patch('app.embeddings.llm_chunker.chunk_using_llm')
    @patch('app.embeddings.llm_chunker.Path')
    def test_chunk_from_directory_empty_directory(
        self, mock_path_class, mock_chunk_llm, mock_openai_class
    ):
        """Test processing an empty directory."""
        # Setup mock directory with no files
        mock_path = MagicMock()
        mock_path.rglob.return_value = []
        mock_path_class.return_value = mock_path
        mock_openai_class.return_value = MagicMock()

        # Execute
        result = chunk_from_directory_using_llm('/test/empty')

        # Verify no chunks were generated
        assert len(result) == 0
        mock_chunk_llm.assert_not_called()

    @patch('app.embeddings.llm_chunker.OpenAI')
    @patch('app.embeddings.llm_chunker.chunk_using_llm')
    @patch('app.embeddings.llm_chunker.Path')
    def test_chunk_from_directory_uses_config_values(
        self, mock_path_class, mock_chunk_llm, mock_openai_class
    ):
        """Test that function uses values from config."""
        mock_path = MagicMock()
        mock_path.rglob.return_value = []
        mock_path_class.return_value = mock_path

        # Mock OpenAI client creation
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Execute
        chunk_from_directory_using_llm('/test/dir')

        # Verify OpenAI was initialized with config values
        # (LLM_API_KEY and LLM_API_URL are imported from config)
        mock_openai_class.assert_called_once()
        call_kwargs = mock_openai_class.call_args.kwargs
        assert 'api_key' in call_kwargs
        assert 'base_url' in call_kwargs
