"""
Script scans a local codbase and stores embeddings in ChromaDB (localhost:8000).

On the first run it automatically installs https://huggingface.co/onnx-models/all-MiniLM-L6-v2-onnx (79MB)
and caching it in /home/beloblotskiy/.cache/chroma/
"""

import logging
import os
import chromadb

class CodeIndexer(object):

    def __init__(self, collection):
        self.__collection = collection
        
    def _index_file(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            self.__collection.add(documents=[content], metadatas=[{"source": file_path}], ids=[str(hash(file_path))])

    def index(self, source_dir):
        cnt = 0
        for root, _, files in os.walk(source_dir):
            logging.info(f"Indexing directory: {root}")
            for file in files:
                if file.endswith('.py'):
                    logging.info(f"Indexing file: {file}")
                    file_path = os.path.join(root, file)
                    self._index_file(file_path)
                    cnt += 1
        logging.info(f"Indexed {cnt} files")

    def retrieval(self, query):
        results = self.__collection.query(
            query_texts=[query],
            n_results=2,
            # where={"metadata_field": "is_equal_to_this"}, # optional filter
            # where_document={"$contains":"search_string"}  # optional filter
        )
        return results

def query(code_indexer, query):
    print(f"Query: '{query}'")
    res = code_indexer.retrieval(query)
    print(f"ids: {res['ids']}")
    print(f"distances: {res['distances']}")
    #print(f"embeddings: {res['embeddings']}")
    print(f"metadatas: {res['metadatas']}")
    #print(f"documents: {res['documents']}")
    #print(f"uris: {res['uris']}")
    #print(f"data: {res['data']}")
    #print(f"included: {res['included']}")
    print('*' * 30)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    client = chromadb.HttpClient()
    collection = client.get_or_create_collection("code_index")

    code_indexer = CodeIndexer(collection)
    code_indexer.index('../heap/')
    
    query(code_indexer, 'cource shedule')
    query(code_indexer, 'meeting schedule')
    query(code_indexer, 'stack implementation')
    query(code_indexer, 'heap implementation')
    query(code_indexer, 'dijkstra algorithm')
