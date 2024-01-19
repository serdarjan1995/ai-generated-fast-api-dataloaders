from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

from base import GoogleDriveReader, Document

app = FastAPI()

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != 'YOUR_API_KEY':
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header

class FolderID(BaseModel):
    folder_id: str

@app.post("/load_data/from_folder_id/", response_model=List[Document])
def load_data_from_folder_id(folder_id: FolderID, mime_types: Optional[List[str]] = None, api_key: str = Security(get_api_key)):
    loader = GoogleDriveReader()
    return loader.load_data(folder_id=folder_id.folder_id, mime_types=mime_types)

@app.post("/load_data/from_file_ids/", response_model=List[Document])
def load_data_from_file_ids(file_ids: List[str], mime_types: Optional[List[str]] = None, api_key: str = Security(get_api_key)):
    loader = GoogleDriveReader()
    return loader.load_data(file_ids=file_ids, mime_types=mime_types)