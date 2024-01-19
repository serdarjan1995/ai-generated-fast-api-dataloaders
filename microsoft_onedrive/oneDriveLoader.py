from fastapi import FastAPI, HTTPException, Query, Depends, Path
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from base import OneDriveReader, Document

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class LoadDataQueryParams(BaseModel):
    folder_id: Optional[str]
    file_ids: Optional[List[str]]
    folder_path: Optional[str]
    file_paths: Optional[List[str]]
    mime_types: Optional[List[str]]
    recursive: bool = True
    userprincipalname: Optional[str]


@app.post('/load_data')
def load_data(query_params: LoadDataQueryParams = Depends(), token: str = Depends(oauth2_scheme)) -> List[Document]:
    """Load data from OneDrive using specified parameters."""
    if not token:
        raise HTTPException(status_code=400, detail='Missing authentication token.')

    loader = OneDriveReader(client_id='your_client_id', client_secret='your_client_secret')
    try:
        documents = loader.load_data(
            folder_id=query_params.folder_id,
            file_ids=query_params.file_ids,
            folder_path=query_params.folder_path,
            file_paths=query_params.file_paths,
            mime_types=query_params.mime_types,
            recursive=query_params.recursive,
            userprincipalname=query_params.userprincipalname
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
