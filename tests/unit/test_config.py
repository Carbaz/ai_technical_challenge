"""Unit tests for app.config module."""

import os
from unittest.mock import patch

import pytest


class TestConfigModule:
    """Test suite for configuration module."""

    @patch.dict(os.environ, {}, clear=True)
    def test_config_defaults_when_no_env_file(self):
        """Test that config loads with defaults when no .env file exists."""
        # Import after patching environment to avoid side effects
        from app import config

        # Verify default values are loaded
        assert config.LOG_LEVEL == 'INFO'
        assert config.LOG_STYLE == '{'
        assert config.CHAT_MODEL == 'gpt-4.1-mini'
        assert config.CHUNKING_MODEL == 'gpt-5-mini'
        assert config.EMBEDDING_MODEL == 'text-embedding-3-small'
        assert config.PDF_PROCESSING_LEVEL == 'MEDIUM'
        assert config.CHROMADB_PORT == 8000
        assert config.CHROMADB_HOST == 'localhost'
        assert config.GRADIO_SERVER_NAME == '127.0.0.1'
        assert config.GRADIO_HTTP_PORT == 7860

    @patch.dict(
        os.environ,
        {
            'FCM_APA_LOG_LEVEL': 'DEBUG',
            'FCM_APA_CHAT_MODEL': 'gpt-4',
            'FCM_APA_CHROMADB_PORT': '9000',
            'FCM_APA_CHROMADB_HOST': 'chromadb-server',
            'FCM_APA_GRADIO_HTTP_PORT': '8080',
            'FCM_APA_LLM_API_KEY': 'test-key-123',
            'FCM_APA_LLM_API_URL': 'https://api.test.com',
        },
        clear=True,
    )
    def test_config_with_custom_environment_variables(self):
        """Test that config loads custom values from env variables."""
        # Reload config module to pick up new environment
        import importlib

        from app import config

        importlib.reload(config)

        assert config.LOG_LEVEL == 'DEBUG'
        assert config.CHAT_MODEL == 'gpt-4'
        assert config.CHROMADB_PORT == 9000
        assert config.CHROMADB_HOST == 'chromadb-server'
        assert config.GRADIO_HTTP_PORT == 8080
        assert config.LLM_API_KEY == 'test-key-123'
        assert config.LLM_API_URL == 'https://api.test.com'

    @patch.dict(
        os.environ,
        {'FCM_APA_PDF_PROCESSING_LEVEL': 'LOW'},
        clear=True,
    )
    def test_pdf_processing_level_validation_low(self):
        """Test PDF processing level accepts LOW value."""
        import importlib

        from app import config

        importlib.reload(config)
        assert config.PDF_PROCESSING_LEVEL == 'LOW'

    @patch.dict(
        os.environ,
        {'FCM_APA_PDF_PROCESSING_LEVEL': 'HIGH'},
        clear=True,
    )
    def test_pdf_processing_level_validation_high(self):
        """Test PDF processing level accepts HIGH value."""
        import importlib

        from app import config

        importlib.reload(config)
        assert config.PDF_PROCESSING_LEVEL == 'HIGH'

    def test_get_conf_excludes_sensitive_fields(self):
        """Test that get_conf() excludes sensitive API keys."""
        from app.config import get_conf

        conf = get_conf()

        # Verify sensitive fields are excluded
        assert 'FCM_APA_LLM_API_KEY' not in conf
        # Verify non-sensitive fields are included
        assert any(
            key.startswith('FCM_APA_') for key in conf.keys()
        ), 'Should have some config values'

    def test_print_conf_does_not_raise(self, capsys):
        """Test that print_conf() executes without errors."""
        from app.config import print_conf

        # Should not raise any exceptions
        print_conf()

        # Capture output to verify it printed something
        captured = capsys.readouterr()
        assert len(captured.out) > 0, 'Should print configuration'

    def test_log_conf_does_not_raise(self):
        """Test that log_conf() executes without errors."""
        from logging import DEBUG

        from app.config import log_conf

        # Should not raise any exceptions
        log_conf(level=DEBUG)

    def test_sensible_fields_contains_api_key(self):
        """Test that SENSIBLE_FIELDS includes the API key."""
        from app.config import SENSIBLE_FIELDS

        assert 'FCM_APA_LLM_API_KEY' in SENSIBLE_FIELDS
