from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Optional
from pydantic import BaseModel
from base import OpendalReader, download_file_from_opendal, download_dir_from_opendal

app = FastAPI()

X_API_KEY = APIKeyHeader(name='X-API-Key', auto_error=False)


class Document(BaseModel):
    title: str
    text: str


def get_api_key(api_key_header: str = Security(X_API_KEY)):
    if api_key_header != 'expected_key_here':
        raise HTTPException(status_code=403, detail='Could not validate credentials')


@app.post('/load_data',
          summary='Loads data from a specified OpenDAL source.',
          response_model=List[Document],
          tags=['OpenDAL Reader'])
async def load_data_endpoint(
    scheme: str = 's3',
    bucket: Optional[str] = None,
    path: str = '/',
    api_key: str = Security(get_api_key),
    file_extractor: Optional[dict] = None):
    """Load data from OpenDAL source."
    if not bucket:
        raise HTTPException(status_code=400, detail='Bucket name is required')
    loader = OpendalReader(scheme=scheme, bucket=bucket, path=path, file_extractor=file_extractor)
    return loader.load_data()


@app.get('/service_health',
         summary='Checks the health of the service.',
         tags=['System'])
async def get_service_health():
    """Returns a message indicating that the service is running."
    return {'status': 'Service is UP and running!'}