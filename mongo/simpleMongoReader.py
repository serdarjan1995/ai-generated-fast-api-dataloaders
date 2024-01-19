from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
from base import SimpleMongoReader, Document

app = FastAPI()

API_KEY = 'your-api-key'
API_KEY_NAME = 'access_token'

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.get('/load_data', summary='Load data from MongoDB', dependencies=[Depends(get_api_key)])
def load_data(
    db_name: str,
    collection_name: str,
    field_names: List[str],
    separator: str = '',
    query_dict: Optional[Dict] = None,
    max_docs: int = 0,
    metadata_names: Optional[List[str]] = None,
    ):    
    reader = SimpleMongoReader(uri='mongodb://localhost:27017/')
    try:
        documents = reader.load_data(db_name, collection_name, field_names, separator, query_dict, max_docs, metadata_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {'documents': documents}
