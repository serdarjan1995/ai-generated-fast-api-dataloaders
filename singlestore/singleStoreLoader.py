from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from base import SingleStoreReader

api_key_header = APIKeyHeader(name='Authorization', auto_error=False)

app = FastAPI(title='SingleStore Loader')

@app.on_event('startup')
def initialize_reader():
    global reader
    reader = SingleStoreReader(
        scheme='mysql',
        host='localhost',
        port='3306',
        user='username',
        password='password',
        dbname='database_name',
        table_name='table_name',
        content_field='text',
        vector_field='embedding'
    )

@app.get('/load-data',
    summary='Load data based on search embedding',
    description='Fetches documents from the SingleStore database that are similar to the search_embedding.')
def load_data(search_embedding: List[float] = Query(..., description='Embedding representation of the query.'),
              top_k: int = Query(5, description='Number of top similar documents to return.'),
              authorization: str = Security(api_key_header)):
    if authorization != 'ExpectedAPIKey':
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    try:
        documents = reader.load_data(search_embedding=str(search_embedding), top_k=top_k)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
