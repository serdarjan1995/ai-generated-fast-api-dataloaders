from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from llama_index.readers.schema.base import Document
import llama_hub.microsoft_onedrive as OneDriveReader

app = FastAPI(openapi_url="/api/v1/openapi.json")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LoadDataQueryParams(BaseModel):
    folder_id: Optional[str]
    file_ids: Optional[List[str]]
    folder_path: Optional[str]
    file_paths: Optional[List[str]]
    mime_types: Optional[List[str]]
    recursive: bool = True
    userprincipalname: Optional[str]


class RequestModel(BaseModel):
    client_id: str
    client_secret: str
    query: LoadDataQueryParams


@app.post("/load_data")
def load_data(request: RequestModel = Body(...)) -> List[Document]:
    """Load data from OneDrive using specified parameters."""

    loader = OneDriveReader(
        client_id=request.client_id, client_secret=request.client_secret
    )
    try:
        documents = loader.load_data(
            folder_id=request.query.folder_id,
            file_ids=request.query.file_ids,
            folder_path=request.query.folder_path,
            file_paths=request.query.file_paths,
            mime_types=request.query.mime_types,
            recursive=request.query.recursive,
            userprincipalname=request.query.userprincipalname,
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
