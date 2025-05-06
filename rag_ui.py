import json
import logging
import os

from functools import partial
from turtle import width
from pywebio import start_server, config
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from pywebio.session import set_env

import chromadb
import openai
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChromaDBSession:
    def __init__(self, collection_name: str, api_url: str = None):
        logging.debug(f"Initializing ChromaDBSession with collection_name={collection_name}, api_url={api_url}")
        self.api_url = api_url
        self.collection_name = collection_name
        self.client = None
        self.collection = None

    def __enter__(self):
        logging.debug(f"Entering context with collection_name={self.collection_name}, api_url={self.api_url}")
        self.client = chromadb.HttpClient(settings=chromadb.config.Settings(anonymized_telemetry=False))
        self.collection = self.client.get_collection(self.collection_name)
        logging.info(f"Connected to {self.collection_name} with {self.collection.count()} elements.")
        return self.collection

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug(f"Exiting context with collection_name={self.collection_name}, api_url={self.api_url}")
        self.client = None
        self.collection = None

# Theme: dark, sketchy, minty, yeti
@config(theme='dark', css_style='width: 100%')
def chat(collection, q: str = None, iter: int = 0, clear=True) -> None:
    set_env(output_max_width = '100%')
    with use_scope('chat', clear=clear):
        if q is None:
            toast(f'Welcome to Code RAG app...', 3)
        else:
            put_text(q)
        put_textarea(f'user_input_{iter}', label='Enter your query:', rows=5, placeholder='Type your query here...')
        put_row([
            put_button('Submit', onclick=lambda: chat(pin[f'user_input_{iter}'], iter+1, False)),
            put_button('Reset', onclick=lambda: chat(None, 0, True))
        ], size='90px')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    openai.api_key = os.environ['OPENAI_API_KEY']
    with ChromaDBSession('code_index', 'localhost:8000') as collection:
        chat_with_collection = partial(chat, collection=collection)
        start_server(chat_with_collection, port=8080, debug=True)
