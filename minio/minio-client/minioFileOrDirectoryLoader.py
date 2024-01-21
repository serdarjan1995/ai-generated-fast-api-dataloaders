from typing import Optional, List
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyQuery, APIKey
from base import MinioReader

app = FastAPI()

API_KEY_NAME = 'access_token'
API_KEY = 'your_api_key_here'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

def get_api_key(
    api_key_query: str = Security(api_key_query),
):
    if api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post('/load', summary='Load data from Minio',
          description='Loads files from a specified Minio bucket. Can load a single file or entire bucket contents filtered by prefix.')
def load_minio_data(
    bucket: str,
    key: Optional[str] = None,
    prefix: Optional[str] = '',
    minio_endpoint: Optional[str] = None,
    minio_secure: bool = False,
    minio_access_key: Optional[str] = None,
    minio_secret_key: Optional[str] = None,
    minio_session_token: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key)
):
    loader = MinioReader(
        bucket=bucket,
        key=key,
        prefix=prefix,
        minio_endpoint=minio_endpoint,
        minio_secure=minio_secure,
        minio_access_key=minio_access_key,
        minio_secret_key=minio_secret_key,
        minio_session_token=minio_session_token
    )
    try:
        documents = loader.load_data()
        return {'status': 'success', 'data': documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))