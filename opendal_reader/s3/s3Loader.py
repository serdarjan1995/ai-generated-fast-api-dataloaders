from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, Union, List

app = FastAPI()

X_API_KEY = APIKeyHeader(name='X-Api-Key')


class Document(BaseModel):
    data: str


class S3LoaderCredentials(BaseModel):
    access_key_id: str
    secret_access_key: str
    bucket: str
    path: str
    endpoint: Optional[str]
    region: Optional[str]


@app.post('/load', summary='Load data from S3', response_model=List[Document])
async def load_data(credentials: S3LoaderCredentials, token: str = Security(X_API_KEY)):
    try:
        from llama_hub.utils import import_loader

        OpendalReader = import_loader("OpendalReader")
    except ImportError:
        OpendalReader = download_loader("OpendalReader")
    loader = OpendalReader(
        scheme="s3",
        path=credentials.path,
        file_extractor=None,
        access_key=credentials.access_key_id,
        secret_key=credentials.secret_access_key,
        endpoint=credentials.endpoint,
        region=credentials.region,
        bucket=credentials.bucket
    )
    return loader.load_data()
