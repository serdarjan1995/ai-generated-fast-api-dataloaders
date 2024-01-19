from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from typing import List

from base import TrelloReader
from llama_index.readers.schema.base import Document

app = FastAPI()

API_KEY_NAME = 'api_key'
API_TOKEN_NAME = 'api_token'

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_token_header = APIKeyHeader(name=API_TOKEN_NAME, auto_error=False)

async def get_api_key(
    api_key: str = Security(api_key_header),
    api_token: str = Security(api_token_header)
):
    return {'api_key': api_key, 'api_token': api_token}

@app.get('/load_data/', response_model=List[Document], summary='Load data from Trello board', description='Loads the documents from the specified Trello board ID.')
async def load_data(
    board_id: str,
    credentials: dict = Depends(get_api_key)
):
    if not credentials['api_key'] or not credentials['api_token']:
        raise HTTPException(status_code=401, detail='API key or token is missing')
    try:
        reader = TrelloReader(credentials['api_key'], credentials['api_token'])
        documents = reader.load_data(board_id=board_id)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
