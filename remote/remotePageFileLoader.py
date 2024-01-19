from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from typing import List
from base import RemoteReader, Document

app = FastAPI(title='Remote Page/File Loader')

API_KEY = '1234567asdfgh'
API_KEY_NAME = 'access_token'

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


@app.get('/load-data/', summary='Load data from a URL', response_model=List[Document])
async def load_data(url: str, api_key: APIKey = Security(get_api_key)):
    reader = RemoteReader()
    documents = reader.load_data(url=url)
    return documents
