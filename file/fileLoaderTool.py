from fastapi import FastAPI, Path, Query, HTTPException, Depends
from typing import List, Optional
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader, APIKey
from base import SimpleDirectoryReader

app = FastAPI()

async def get_api_key(
    api_key_query: str = Depends(APIKeyQuery(name='api_key_query', auto_error=False)),
    api_key_header: str = Depends(APIKeyHeader(name='api_key_header', auto_error=False))
) -> APIKey:
    if api_key_query == 'secret' or api_key_header == 'secret':
        return api_key_query or api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.post('/load-directory-data/', summary='Load documents from a directory')
async def load_directory_data(
    directory: str = Query(..., description='Path to the directory to load', alias='input_dir'),
    exclude_hidden: Optional[bool] = Query(True, description='Whether to exclude hidden files'),
    errors: Optional[str] = Query('ignore', description='How to handle encoding/decoding errors'),
    recursive: Optional[bool] = Query(False, description='Whether to search recursively in subdirectories'),
    required_exts: Optional[List[str]] = Query(None, description='List of required file extensions'),
    num_files_limit: Optional[int] = Query(None, description='Max number of files to read'),
    api_key: APIKey = Depends(get_api_key)
):
    loader = SimpleDirectoryReader(directory, exclude_hidden, errors, recursive, required_exts, num_files_limit=num_files_limit)
    documents = loader.load_data()
    return {'documents': documents}
