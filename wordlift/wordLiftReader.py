from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Optional

app = FastAPI()

API_KEY = 'your_api_key'
API_KEY_NAME = 'access_token'
PREFIX = 'Bearer'

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header == f'{PREFIX} {API_KEY}':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.get('/load-data',
         summary='Load data from WordLift Knowledge Graph',
         description='Fetches and transforms data from a WordLift Knowledge Graph using a WordLift Key.',
         response_model=List[Document])
async def load_data(endpoint: str,
                    query: str,
                    fields: str,
                    text_fields: Optional[List[str]] = None,
                    metadata_fields: Optional[List[str]] = None,
                    api_key: str = Depends(get_api_key)):
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    config_options = {
        'text_fields': text_fields or [],
        'metadata_fields': metadata_fields or [],
    }
    reader = WordLiftLoader(endpoint, headers, query, fields, config_options)
    try:
        documents = reader.load_data()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
