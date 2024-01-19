from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os
import base

app = FastAPI()

API_KEY = os.getenv("GITHUB_TOKEN")
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class RepositoryQuery(BaseModel):
    owner: str
    repo: str
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    filter_directories: Optional[List[str]] = Query(None)
    filter_directories_type: Optional[base.GithubRepositoryReader.FilterType] = Query(None)
    filter_file_extensions: Optional[List[str]] = Query(None)
    filter_file_extensions_type: Optional[base.GithubRepositoryReader.FilterType] = Query(None)

async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post("/load_repository_data/")
async def load_repository_data(query: RepositoryQuery, token: str = Depends(get_api_key)):
    github_client = base.GithubClient(token)
    loader = base.GithubRepositoryReader(
        github_client,
        owner=query.owner,
        repo=query.repo,
        filter_directories=(
            query.filter_directories, query.filter_directories_type
        ) if query.filter_directories and query.filter_directories_type else None,
        filter_file_extensions=(
            query.filter_file_extensions, query.filter_file_extensions_type
        ) if query.filter_file_extensions and query.filter_file_extensions_type else None
    )
    if query.branch:
        docs = loader.load_data(branch=query.branch)
    elif query.commit_sha:
        docs = loader.load_data(commit_sha=query.commit_sha)
    else:
        raise HTTPException(status_code=400, detail="Either branch or commit_sha must be provided.")
    return docs
