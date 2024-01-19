from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from typing import List
from pydantic import BaseModel
from base import FirestoreReader, Document

app = FastAPI()

API_KEY_NAME = 'access_token'
API_KEY = 'secret-key-to-change-in-production'

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class CollectionPath(BaseModel):
    path: str

class DocumentPath(BaseModel):
    path: str

@app.post('/load_data/', response_model=List[Document])
def read_collection(collection_path: CollectionPath, api_key: APIKey = Security(get_api_key)):
    reader = FirestoreReader(project_id='Your-Google-Cloud-Project-ID')
    return reader.load_data(collection_path.path)

@app.post('/load_document/', response_model=Document)
def read_document(document_path: DocumentPath, api_key: APIKey = Security(get_api_key)):
    reader = FirestoreReader(project_id='Your-Google-Cloud-Project-ID')
    return reader.load_document(document_path.path)
