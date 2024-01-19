from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == 'YOUR_ACTUAL_SECRET_API_KEY':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Invalid API Key')

class Document(BaseModel):
    text: str
    embedding: Optional[List[float]] = None

@app.post('/load_data/', response_model=List[Document])
async def load_data(
    api_key: str = Security(get_api_key),
    index_name: str,
    id_to_text_map: Dict[str, str],
    vector: List[float],
    top_k: int,
    separate_documents: Optional[bool] = True
):
    from base import PineconeReader
    reader = PineconeReader(api_key=api_key, environment='us-west1-gcp')
    try:
        documents = reader.load_data(
            index_name=index_name,
            id_to_text_map=id_to_text_map,
            top_k=top_k,
            vector=vector,
            separate_documents=separate_documents
        )
        return documents
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))