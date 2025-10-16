"""Unit tests for tools.querier module."""

from unittest.mock import MagicMock, patch

import pytest

from tools.querier import retrieve_company_data_from_vectorstore


class TestRetrieveCompanyData:
    """Test suite for retrieve_company_data_from_vectorstore function."""

    def test_retrieve_company_data_basic(self):
        """Test basic similarity search with company filter."""
        # Setup mock vectorstore
        mock_vectorstore = MagicMock()
        mock_results = [
            MagicMock(page_content="Policy 1"),
            MagicMock(page_content="Policy 2"),
        ]
        mock_vectorstore.similarity_search.return_value = mock_results

        # Execute
        result = retrieve_company_data_from_vectorstore(
            "What is the pet policy?", "Delta", mock_vectorstore
        )

        # Verify similarity_search was called correctly
        mock_vectorstore.similarity_search.assert_called_once_with(
            "What is the pet policy?",
            k=10,
            filter={'company': 'Delta'},
        )
        assert result == mock_results

    def test_retrieve_company_data_custom_n_vectors(self):
        """Test similarity search with custom number of vectors."""
        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = []

        result = retrieve_company_data_from_vectorstore(
            "query", "United", mock_vectorstore, n_vectors=5
        )

        # Verify k parameter was set correctly
        call_kwargs = mock_vectorstore.similarity_search.call_args.kwargs
        assert call_kwargs['k'] == 5

    def test_retrieve_company_data_different_companies(self):
        """Test that filter changes based on company parameter."""
        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = []

        # Test with different companies
        for company in ['Delta', 'United', 'AmericanAirlines']:
            retrieve_company_data_from_vectorstore(
                "test query", company, mock_vectorstore
            )
            call_kwargs = (
                mock_vectorstore.similarity_search.call_args.kwargs
            )
            assert call_kwargs['filter'] == {'company': company}

    def test_retrieve_company_data_empty_results(self):
        """Test handling of empty search results."""
        mock_vectorstore = MagicMock()
        mock_vectorstore.similarity_search.return_value = []

        result = retrieve_company_data_from_vectorstore(
            "unknown query", "TestCo", mock_vectorstore
        )

        assert result == []
