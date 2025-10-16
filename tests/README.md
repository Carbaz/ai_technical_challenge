# Unit Tests

This directory contains the unit test suite for the Airline Policy Assistant
Service.

## Structure

```txt
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Shared pytest fixtures and configuration
└── unit/                 # Unit tests
    ├── __init__.py
    ├── test_config.py    # Tests for app.config module
    ├── test_embeddings.py # Tests for app.embeddings.embeddings
    ├── test_llm_chunker.py # Tests for app.embeddings.llm_chunker
    └── test_querier.py   # Tests for tools.querier module
```

## Running Tests

### Locally with Pipenv

1. **Install development dependencies:**

   ```bash
   pipenv install --dev
   ```

2. **Run all tests:**

   ```bash
   pipenv run pytest tests/unit -v
   ```

3. **Run specific test file:**

   ```bash
   pipenv run pytest tests/unit/test_config.py -v
   ```

4. **Run specific test class:**

   ```bash
   pipenv run pytest tests/unit/test_config.py::TestConfigModule -v
   ```

5. **Run specific test function:**

   ```bash
   pipenv run pytest \
       tests/unit/test_config.py::TestConfigModule::\
       test_config_defaults_when_no_env_file -v
   ```

### With Coverage

Use the provided scripts to run tests with coverage reporting:

**On Linux/Mac:**

```bash
bash tools/run_test_coverage.sh
```

**On Windows (PowerShell):**

```powershell
.\tools\run_test_coverage.ps1
```

**Manual coverage command:**

```bash
pipenv run coverage run -m pytest tests/unit -v
pipenv run coverage report -m
pipenv run coverage html
```

The HTML coverage report will be generated in `htmlcov/index.html`.

### In Docker

You can run tests inside a Docker container:

```bash
docker-compose run --rm backend pipenv run pytest tests/unit -v
```

With coverage:

```bash
docker-compose run --rm backend bash tools/run_test_coverage.sh
```

## Test Configuration

Test configuration is defined in `pytest.ini`:

* Test discovery: `tests/` directory
* Pattern: `test_*.py` files
* Coverage source: `app/` and `tools/` directories
* Coverage omits: test files, `__pycache__`, `__main__.py`

## Fixtures

Shared fixtures are defined in `conftest.py`:

* `mock_document`: Single mock Document object
* `mock_documents`: List of mock Document objects
* `mock_openai_client`: Mock OpenAI client
* `mock_vectorstore`: Mock Chroma vectorstore
* `clean_environment`: Clean environment without config variables
* `reset_modules`: Auto-fixture to reset modules between tests

## Test Coverage

Current test coverage includes:

### app.config (test_config.py)

* Default configuration loading
* Custom environment variable handling
* PDF processing level validation
* Sensitive field exclusion in `get_conf()`
* Print and log configuration functions

### app.embeddings.embeddings (test_embeddings.py)

* `load_text_from_directory()`: Text/Markdown loading
* `load_pdf_from_directory()`: PDF loading without OCR
* `load_pdf_from_directory_with_ocr()`: PDF loading with OCR
* `update_metadata()`: Metadata updates and sanitization
* `chunk_documents()`: Document chunking
* `embed_documents()`: Vector embedding creation
* `chunk_directory_text()`: Text directory processing
* `chunk_directory_pdf()`: PDF directory processing (all levels)
* `embed_directory()`: Complete embedding workflow
* `cleanup_embeddings()`: Database cleanup

### app.embeddings.llm_chunker (test_llm_chunker.py)

* `_chunk` and `_response_format` Pydantic models
* `chunk_using_llm()`: LLM-based file chunking
* `chunk_from_directory_using_llm()`: Directory processing with LLM

### tools.querier (test_querier.py)

* `retrieve_company_data_from_vectorstore()`: Similarity search

## Writing New Tests

When adding new tests, follow these guidelines:

1. **Organize by module**: Create test files matching source module names
2. **Use descriptive names**: `test_function_name_scenario()`
3. **Use test classes**: Group related tests in classes
4. **Add docstrings**: Explain what each test validates
5. **Use fixtures**: Leverage shared fixtures from `conftest.py`
6. **Mock external dependencies**: Use `unittest.mock` for external calls
7. **Test edge cases**: Cover normal, edge, and error cases
8. **Keep tests isolated**: Each test should be independent

### Example Test Structure

```python
class TestMyFunction:
    """Test suite for my_function."""

    def test_my_function_normal_case(self):
        """Test my_function with normal inputs."""
        result = my_function(valid_input)
        assert result == expected_output

    def test_my_function_edge_case(self):
        """Test my_function with edge case input."""
        result = my_function(edge_case_input)
        assert result == edge_case_output

    @patch('module.external_dependency')
    def test_my_function_with_mock(self, mock_dep):
        """Test my_function with mocked dependencies."""
        mock_dep.return_value = mock_data
        result = my_function()
        assert result == expected
        mock_dep.assert_called_once()
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: pipenv install --dev

- name: Run tests with coverage
  run: pipenv run coverage run -m pytest tests/unit -v

- name: Generate coverage report
  run: pipenv run coverage report -m
```

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running from the project root:

```bash
cd ai_technical_challenge
pipenv run pytest tests/unit -v
```

### Module Not Found

Install all development dependencies:

```bash
pipenv install --dev
```

### Configuration Errors

Some tests modify environment variables. If you see unexpected configuration
errors, the `reset_modules` fixture should handle cleanup, but you can manually
clear the environment:

```bash
unset $(env | grep FCM_APA_ | cut -d= -f1)
```

### Coverage Not Working

Ensure coverage is installed:

```bash
pipenv install --dev coverage pytest-cov
```
