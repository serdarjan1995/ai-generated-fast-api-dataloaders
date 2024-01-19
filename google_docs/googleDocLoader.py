from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from base import GoogleDocsReader, Document

app = FastAPI()

API_KEY_NAME = 'api_key'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == 'YOUR_API_KEY':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.post('/load_data',
          summary='Load data from Google Docs',
          description='Takes an array of Google Doc IDs and parses their text into `Document` objects')
async def load_data_from_google_docs(document_ids: List[str], api_key: str = Security(get_api_key)):
    if not document_ids:
        raise HTTPException(status_code=400, detail='Document IDs are required')
    loader = GoogleDocsReader()
    try:
        documents = loader.load_data(document_ids=document_ids)
        return {'documents': [doc.dict() for doc in documents]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
