"""Airline Policy Assistant Service main module."""

from logging import getLogger

import gradio as gr
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .config import CHAT_MODEL, CHROMADB_HOST, CHROMADB_PORT, EMBEDDING_MODEL
from .config import GRADIO_HTTP_PORT, GRADIO_SERVER_NAME, LLM_API_KEY, LLM_API_URL


# Instantiate local logger.
_logger = getLogger(__name__)

# Set up vector storage and retriever.
_logger.info('LOADING VECTORSTORE')
embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL,
                                   api_key=LLM_API_KEY, base_url=LLM_API_URL)
vectorstore = Chroma(embedding_function=embedding_model,
                     host=CHROMADB_HOST, port=CHROMADB_PORT)
retriever = vectorstore.as_retriever()

# Create a new Chat.
llm = ChatOpenAI(temperature=0.7, model_name=CHAT_MODEL,
                 api_key=LLM_API_KEY, base_url=LLM_API_URL)

# Set up the conversation memory.
memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)


# Set up the conversation chain with the Chat LLM, the vectorstore and the memory.
conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever,
                                                           memory=memory)


# ## ############## Chat functions for Gradio interface.
# * "history" isn't used as the memory is included on the ConversationalRetrievalChain.

def _chat(message, history):
    result = conversation_chain.invoke({"question": message})
    return result["answer"]


def _clear():
    _logger.info('Clearing conversation memory...')
    conversation_chain.memory.clear()
    return '', []


class myChatInterface(gr.ChatInterface):
    """Custom Gradio ChatInterface to clear chain memory when using the clear button."""
    def __init__(self, chat_fn, reset_fn, *args, **kwargs):
        """Initialize the custom chat interface."""
        super().__init__(chat_fn, *args, **kwargs)
        self.reset_fn = reset_fn

    def _delete_conversation(self, *args, **kwargs):
        """Override to clear chain memory before deleting conversation."""
        self.reset_fn()
        return super()._delete_conversation(*args, **kwargs)


try:
    view = myChatInterface(_chat, _clear, type="messages").launch(
        server_name=GRADIO_SERVER_NAME, server_port=GRADIO_HTTP_PORT)
except Exception as ex:
    _logger.critical(f'CRITICAL ERROR ON GRADIO SERVICE: {ex}')
    exit(1)
