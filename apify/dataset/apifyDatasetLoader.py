from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from llama_index.readers.schema import Document
from typing import Callable, Dict, List, Optional
from pydantic import BaseModel
from apify_client import ApifyClient

X_API_KEY = APIKeyHeader(name='X-API-Key')

app = FastAPI(title='Apify Dataset Loader')


def get_api_client(api_key: str = Security(X_API_KEY)):
    return ApifyClient(api_key)


class DocumentModel(BaseModel):
    text: str
    extra_info: Dict[str, str]


class DocumentIn(BaseModel):
    url: str
    text: str


def transform_dataset_item(item: Dict) -> Document:
    return Document(text=item.get('text'), extra_info={'url': item.get('url')})


@app.post('/load-data', response_model=List[DocumentModel])
def load_data(dataset_id: str, api_client: ApifyClient = Depends(get_api_client)) -> List[DocumentModel]:
    items_list = api_client.dataset(dataset_id).list_items(clean=True)
    document_list = []
    for item in items_list['items']:
        document = transform_dataset_item(item)
        if not isinstance(document, Document):
            raise HTTPException(status_code=400, detail='Dataset mapping function must return a Document')
        document_list.append(document)
    return document_list
