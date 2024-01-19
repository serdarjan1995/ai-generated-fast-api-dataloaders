from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional, Dict, Set
from pydantic import BaseModel
from elasticsearch import Elasticsearch

app = FastAPI()


class Document(BaseModel):
    text: str
    extra_info: Dict
    embedding: Optional[str] = None


class ElasticsearchReader:
    def __init__(self, endpoint: str, index: str, basic_auth: Optional[Set[str]] = None):
        self._es_client = Elasticsearch(endpoint, basic_auth=basic_auth)
        self._index = index

    def load_data(self, field: str, query: Optional[Dict] = None, embedding_field: Optional[str] = None, size: Optional[int] = 10) -> List[Document]:
        query = query.get('query') if query else None
        res = self._es_client.search(index=self._index, query=query, size=size)
        documents = []
        for hit in res['hits']['hits']:
            value = hit['_source'][field]
            _ = hit['_source'].pop(field)
            embedding = hit['_source'].get(embedding_field or '', None)
            documents.append(Document(text=value, extra_info=hit['_source'], embedding=embedding))
        return documents


@app.post('/load_data/', response_model=List[Document], summary='Load data from Elasticsearch', description='This endpoint retrieves documents from an Elasticsearch index based on the given query.')
def async_load_data(field: str, query: Optional[Dict] = None, embedding_field: Optional[str] = None, size: int = 10, endpoint: str, index: str, basic_auth: Optional[Set[str]] = Depends()):
    reader = ElasticsearchReader(endpoint=endpoint, index=index, basic_auth=basic_auth)
    return reader.load_data(field, query, embedding_field, size)

