from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from typing import List
from pydantic import BaseModel
from enum import Enum
import os

app = FastAPI()

token_header = APIKeyHeader(name='Authorization', auto_error=False)

async def get_api_key(token: str = Depends(token_header)):
    if token != os.getenv('GITHUB_TOKEN'):
        raise HTTPException(status_code=403, detail='Invalid API Key')
    return token

class FilterType(str, Enum):
    EXCLUDE = 'exclude'
    INCLUDE = 'include'


class Document(BaseModel):
    doc_id: str
    text: str
    title: str = None
    extra_info: dict


class GitHubCollaboratorsClient:
    # Placeholder for the actual GitHubCollaboratorsClient implementation
    pass


@app.get('/load_collaborators/', summary='Load GitHub repository collaborators', response_model=List[Document])
def load_data(owner: str, repo: str, verbose: bool = False, api_key: APIKey = Depends(get_api_key)):
    # Placeholder for the actual data loading implementation
    return []
