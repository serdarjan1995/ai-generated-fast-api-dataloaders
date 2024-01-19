from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List
from pydantic import BaseModel
from base import S3Reader, Document

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == 'EXPECTED_API_KEY':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post('/load_data/', summary='Load data from S3')
def load_data(
    bucket: str,
    key: Optional[str] = None,
    prefix: Optional[str] = '',
    required_exts: Optional[List[str]] = None,
    filename_as_id: bool = False,
    num_files_limit: Optional[int] = None,
    custom_temp_subdir: Optional[str] = None,
    aws_access_id: Optional[str] = None,
    aws_access_secret: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    s3_endpoint_url: str = 'https://s3.amazonaws.com',
    custom_reader_path: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    reader = S3Reader(
        bucket=bucket,
        key=key,
        prefix=prefix,
        required_exts=required_exts,
        filename_as_id=filename_as_id,
        num_files_limit=num_files_limit,
        aws_access_id=aws_access_id,
        aws_access_secret=aws_access_secret,
        aws_session_token=aws_session_token,
        s3_endpoint_url=s3_endpoint_url,
        custom_reader_path=custom_reader_path
    )
    documents = reader.load_data(custom_temp_subdir=custom_temp_subdir)
    return {'documents': documents}
