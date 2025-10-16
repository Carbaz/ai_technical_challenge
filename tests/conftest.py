"""Pytest configuration and shared fixtures."""

import os
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document


@pytest.fixture
def mock_document():
    """Create a mock Document object."""
    return Document(
        page_content="Sample document content",
        metadata={'source': 'test.txt', 'company': 'TestCo'},
    )


@pytest.fixture
def mock_documents():
    """Create a list of mock Document objects."""
    return [
        Document(
            page_content="First document",
            metadata={'source': 'doc1.txt'},
        ),
        Document(
            page_content="Second document",
            metadata={'source': 'doc2.txt'},
        ),
        Document(
            page_content="Third document",
            metadata={'source': 'doc3.md'},
        ),
    ]


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    client = MagicMock()
    client.files.create.return_value = MagicMock(id='file-123')
    return client


@pytest.fixture
def mock_vectorstore():
    """Create a mock Chroma vectorstore."""
    vectorstore = MagicMock()
    vectorstore.similarity_search.return_value = []
    vectorstore.get.return_value = {'ids': []}
    return vectorstore


@pytest.fixture
def clean_environment(monkeypatch):
    """Provide a clean environment without FCM_APA_ variables."""
    # Remove all FCM_APA_ environment variables
    for key in list(os.environ.keys()):
        if key.startswith('FCM_APA_'):
            monkeypatch.delenv(key, raising=False)
    return monkeypatch


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset imported modules before each test to avoid state pollution."""
    import sys

    # Store modules to potentially reload
    modules_to_reload = [
        'app.config',
        'app.embeddings.embeddings',
        'app.embeddings.llm_chunker',
    ]

    # Remove from sys.modules if present
    for module in modules_to_reload:
        if module in sys.modules:
            del sys.modules[module]

    yield

    # Clean up again after test
    for module in modules_to_reload:
        if module in sys.modules:
            del sys.modules[module]
