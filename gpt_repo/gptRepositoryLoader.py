from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import List, Optional
from base import GPTRepoReader, Document

app = FastAPI()
X_API_KEY = APIKeyHeader(name='X-API-Key')

@api_key_validator(api_key: str = Depends(X_API_KEY))
def validate_api_key(api_key: str):
    if api_key != 'expected_api_key':
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.post('/load_data/', response_model=List[Document])
def load_data(
        repo_path: str,
        preamble_str: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        token: str = Depends(api_key_validator)
    ):
    gpt_repo_reader = GPTRepoReader()
    try:
        documents = gpt_repo_reader.load_data(repo_path=repo_path, preamble_str=preamble_str, extensions=extensions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return documents
