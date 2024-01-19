from fastapi import FastAPI, Security, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.security.api_key import APIKeyHeader
import base64
import os
import requests
from llama_index.readers.schema.base import Document

app = FastAPI()

BITBUCKET_API_KEY_NAME = 'X-BITBUCKET-API-KEY'
api_key_header = APIKeyHeader(name=BITBUCKET_API_KEY_NAME, auto_error=False)


class BitbucketReader(BaseModel):
    base_url: str
    project_key: str
    branch: Optional[str] = "refs/heads/develop"
    repository: Optional[str] = None
    extensions_to_skip: Optional[List[str]] = []

    def get_headers(self, api_key: str):
        username = os.getenv("BITBUCKET_USERNAME")
        auth = base64.b64encode(f"{username}:{api_key}".encode()).decode()
        return {"Authorization": f"Basic {auth}"}

    # ... Include other methods here without docstrings ...


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.getenv('BITBUCKET_API_KEY'):
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.post('/load-data/', summary='Load data from Bitbucket repository.')
def load_data(bitbucket_reader: BitbucketReader, api_key: str = Security(get_api_key)):
    try:
        reader = BitbucketReader(
            base_url=bitbucket_reader.base_url,
            project_key=bitbucket_reader.project_key,
            branch=bitbucket_reader.branch,
            repository=bitbucket_reader.repository,
            extensions_to_skip=bitbucket_reader.extensions_to_skip
        )
        documents = reader.load_data()
        return {'documents': [doc.dict() for doc in documents]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
