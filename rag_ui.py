import logging
import os

from functools import partial
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

class ChromaDBSession(object):
    def __init__(self, collection_name: str):
        logging.debug(f"Initializing ChromaDBSession with collection_name={collection_name}...")
        self.__collection_name = collection_name
        self.__client = None
        self.__vectorstore = None

    def __enter__(self):
        logging.debug(f"Entering ChromaDBSession context with collection_name={self.__collection_name}...")
        self.__client = chromadb.HttpClient(settings=chromadb.config.Settings(anonymized_telemetry=False))
        self.__vectorstore = Chroma(collection_name=self.__collection_name, client=self.__client)
        logging.info(f"Connected to {self.__collection_name}.")
        return self.__vectorstore

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug(f"Exiting ChromaDBSession context with collection_name={self.__collection_name}...")
        self.__client = None
        self.__vectorstore = None

class LangChainAI(object):
    def __init__(self, retriever, prompt, llm):
        self.__rag_chain = (
            {"context": retriever | self._fmt_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

    def _fmt_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def answer(self, q: str) -> str:
        return f'Answer: {q} !!!'
    

class AISession(object):
    def __init__(self, retriever, prompt_name, model_name):
        logging.debug(f"Initializing AISession with prompt_name={prompt_name}...")
        self.__prompt_name = prompt_name
        logging.info(f"Pulling prompt {self.__prompt_name}...")
        # https://smith.langchain.com/hub/search?q=rag-prompt.
        prompt = hub.pull(self.__prompt_name)
        logging.info(f"Prompt name {self.__prompt_name} resolved as '{prompt}'")
        llm = ChatOpenAI(model_name=model_name, temperature=0)
        self.__ai = LangChainAI(retriever, prompt, llm)

    def __enter__(self):
        logging.debug(f"Entering AISession context...")
        return self.__ai

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug(f"Exiting AISession context...")

# Theme: dark, sketchy, minty, yeti
@config(theme='dark', css_style='width: 100%')
def chat(ai, q: str = None, iter: int = 0, clear=True) -> None:
    set_env(output_max_width = '100%')
    with use_scope('chat', clear=clear):
        if q is None:
            toast(f'Welcome to Code RAG app...', 3)
        else:
            put_text(ai.answer(q))
        put_textarea(f'user_input_{iter}', label='Enter your query:', rows=5, placeholder='Type your query here...')
        put_row([
            put_button('Submit', onclick=lambda: chat(ai, pin[f'user_input_{iter}'], iter+1, False)),
            put_button('Reset', onclick=lambda: chat(ai, None, 0, True))
        ], size='90px')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    openai.api_key = os.environ['OPENAI_API_KEY']
    with ChromaDBSession('code_index') as vectorstore:
        retriever = vectorstore.as_retriever()
        with AISession(retriever, "jclemens24/rag-prompt", "gpt-4o-mini") as ai:
            chat_ai = partial(chat, ai=ai)
            start_server(chat_ai, port=8080, debug=True)
