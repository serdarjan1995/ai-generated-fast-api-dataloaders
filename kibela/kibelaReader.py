
from typing import List

from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class NoteModel(BaseModel):
    content: str
    id: str
    title: str
    url: str

class DocumentModel(BaseModel):
    text: str

@app.post('/load-data', response_model=List[DocumentModel], summary='Load data from Kibela', description='Fetches article from your Kibela notes using the GraphQL API.')
async def load_data(team: str, api_key: str = Security(api_key_header)):
    # Placeholder for actual data loading logic
    # Here we should integrate the KibelaReader and its load_data method,
    # but this requires the request function and the KibelaReader class itself.
    raise HTTPException(status_code=501, detail='Not implemented')

