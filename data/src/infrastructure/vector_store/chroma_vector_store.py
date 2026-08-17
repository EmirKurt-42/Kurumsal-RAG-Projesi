"""
Adapter: IVectorStore'un ChromaDB ile gerceklestirimi.
"""
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.utils import embedding_functions
from src.application.interfaces import IVectorStore


class ChromaVectorStore(IVectorStore):
    def __init__(self, db_folder, collection_name, embedding_model):
        self._collection_name = collection_name
        self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self._client = chromadb.PersistentClient(path=db_folder)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedding_function,
        )

    def reset(self):
        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            embedding_function=self._embedding_function,
        )

    def delete_by_file(self, file_id):
        existing = self._collection.get(where={'file_id': file_id})
        if existing and existing['ids']:
            self._collection.delete(ids=existing['ids'])

    def add(self, ids, texts, metadatas):
        self._collection.upsert(ids=ids, documents=texts, metadatas=metadatas)

    def query(self, question, n_results=5, where: Optional[Dict[str, Any]] = None):
        kwargs = {
            'query_texts': [question],
            'n_results': n_results,
            'include': ['documents', 'metadatas', 'distances'],
        }
        if where:
            kwargs['where'] = where
        return self._collection.query(**kwargs)