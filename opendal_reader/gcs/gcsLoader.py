from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN
from typing import List, Optional, Dict, Union
from pydantic import BaseModel

app = FastAPI()

API_KEY = "YOUR_API_KEY"
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


from llama_index.readers.schema.base import Document
class DocumentModel(BaseModel):
    id: Optional[str]
    text: str

def download_loader(loader_name):
    # This should be implemented with the actual logic to load the necessary loader
    raise NotImplementedError('download_loader function needs to be implemented.')

def import_loader(loader_name):
    # This should be implemented with the actual logic to import the necessary loader
    raise NotImplementedError('import_loader function needs to be implemented.')

class OpendalGcsReader:
    def __init__(self, bucket: str, path: str, endpoint: str, credentials: str, file_extractor: Optional[Dict[str, Union[str, BaseReader]]]):
        pass  # Replace with actual initialisation
    def load_data(self) -> List[Document]:
        pass  # Replace with actual data loading logic

@app.post('/load_data/', response_model=List[DocumentModel])
def load_data_from_gcs(
    bucket: str = Depends(get_api_key),
    path: str,
    endpoint: Optional[str] = None,
    credentials: Optional[str] = None,
    file_extractor: Optional[Dict[str, Union[str, str]]] = None
):
    """
    Load file(s) from Google Cloud Storage.
    - **bucket**: GCS bucket name
    - **path**: Path in the GCS bucket
    - **endpoint**: GCS endpoint (optional)
    - **credentials**: Credentials to authenticate with GCS (optional)
    - **file_extractor**: Mapping of file extension to loader (optional)
    """
    gcs_reader = OpendalGcsReader(bucket, path, endpoint, credentials, file_extractor)
    documents = gcs_reader.load_data()
    return [DocumentModel(id=doc.id, text=doc.text) for doc in documents]
