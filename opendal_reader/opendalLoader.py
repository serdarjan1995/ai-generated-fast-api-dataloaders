from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from typing import Optional, List
from pydantic import BaseModel
from base import OpendalReader

app = FastAPI()

API_KEY = "secret"
API_KEY_NAME = "access_token"
COOKIE_DOMAIN = "localtest.me"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


def get_api_key(
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
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )

class Document(BaseModel):
    content: str
    path: str
    name: str
    source: str

@app.post('/readData/', response_model=List[Document], summary='Load and parse data from a storage service', description='Reads data using OpendalReader from the specified storage service and returns a list of documents.')
def read_data(
    scheme: str = Query(..., description='The scheme of the storage service (e.g. s3, azblob, gcs)'),
    path: str = Query(..., description='The path of the data to read'),
    api_key: APIKey = Depends(get_api_key)
):
    loader = OpendalReader(scheme=scheme, path=path)
    try:
        documents = loader.load_data()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
