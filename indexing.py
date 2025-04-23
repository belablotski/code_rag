import logging
import os
from chromadb import Client

def index_file(file_path, db):
    with open(file_path, 'r') as f:
        content = f.read()
    db.add_document(content, metadata={"file_path": file_path})

def index(source_dir):
    db = Client()
    cnt = 0
    for root, _, files in os.walk(source_dir):
        logging.info(f"Indexing directory: {root}")
        for file in files:
            if file.endswith('.py'):
                logging.info(f"Indexing file: {file}")
                file_path = os.path.join(root, file)
                index_file(file_path, db)
                cnt += 1
    logging.info(f"Indexed {cnt} files")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    index('../heap/')