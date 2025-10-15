"""LLM Based File chunking module."""

from logging import getLogger
from pathlib import Path

from langchain_core.documents import Document
from openai import OpenAI
from pydantic import BaseModel, Field

from app.config import CHUNKING_MODEL, LLM_API_KEY, LLM_API_URL


# Define Pydantic model classes for response format parsing.
class _chunk(BaseModel):
    page_content: str = Field(..., max_length=1000)


class _response_format(BaseModel):
    chunks: list[_chunk]


def chunk_using_llm(file_path, client: OpenAI, chunk_size=1000, chunk_overlap=100):
    """Send the file to the LLM and return it chunked."""
    prompt = f"""
    Analyze this document and return its content ready to be embedded for RAG.

    You must return a list of strings, in python format,
    one for each chunk of text you think is appropriate.

    Be sure not to omit information not to create new one, stick to the actual
    information in the document.

    The chunks must be as long as possible, up to {chunk_size} characters,
    and some overlap, up to {chunk_overlap} characters, is welcome.

    Response must be encapsulated as JSON:

    {{
        "chunks": [
            {{"page_content": "first_chunk ..."}},
            {{"page_content": "second_chunk ..."}},
            {{"page_content": "third_chunk ..."}}
    }}
    """
    # Open and load file into the client.
    with open(file_path, 'rb') as file:
        file_obj = client.files.create(file=file, purpose='user_data')
    # Request the model to parse the file.
    response = client.chat.completions.parse(
        model=CHUNKING_MODEL,
        response_format=_response_format,
        messages=[{"role": "user",
                   "content": [{'type': 'text', 'text': prompt},
                               {'type': 'file', 'file': {'file_id': file_obj.id}}]}])
    # Cast response to Documents and return.
    return [Document(page_content=chunk.page_content, metadata={'source': file_path})
            for chunk in response.choices[0].message.parsed.chunks]


def chunk_from_directory_using_llm(directory, glob='**/*.pdf',
                                   chunk_size=1000, chunk_overlap=100):
    """Process all documents from directory using an LLM and return them chunked."""
    all_chunks = []
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_URL)
    for file_path in Path(directory).rglob(glob):
        _logger.info(f'CHUNKING WITH LLM: {file_path}')
        chunks = chunk_using_llm(str(file_path), client, chunk_size, chunk_overlap)
        all_chunks.extend(chunks)
    return all_chunks


# Instantiate local logger.
_logger = getLogger(__name__)
