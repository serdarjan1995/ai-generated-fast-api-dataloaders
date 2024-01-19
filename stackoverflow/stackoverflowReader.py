from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel
import os
from base import StackoverflowReader, Document

app = FastAPI()

API_KEY = os.getenv('STACKOVERFLOW_PAT')
API_KEY_NAME = 'access-token'
TEAM_NAME = os.getenv('STACKOVERFLOW_TEAM_NAME')
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API Key')
    return api_key_header

class StackOverflowPostModel(BaseModel):
    text: str
    doc_id: str
    extra_info: dict

@app.get('/stackexchange/posts/', response_model=List[StackOverflowPostModel],
    summary='List Stackexchange Posts',
    description='Fetch a list of Stackexchange posts based on your team and cache settings',
    responses={
        200: {'description': 'Successful Response'},
        403: {'description': 'Invalid API Key Provided'},
        500: {'description': 'Server Error'},
    })
async def get_stackexchange_posts(
    page: int = 1,
    doc_type: str = 'posts',
    limit: int = 50,
    api_key: str = Depends(get_api_key),
    team_name: str = TEAM_NAME
):
    try:
        reader = StackoverflowReader(api_key, team_name, cache_dir='./stackoverflow_cache')
        data = reader.load_data(page=page, doc_type=doc_type, limit=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
