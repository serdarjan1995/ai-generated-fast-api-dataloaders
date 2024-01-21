from fastapi import FastAPI, HTTPException, Query, Security
from pydantic import BaseModel
from typing import Optional, List
from base import BotoMinioReader

app = FastAPI()

class MinioLoaderBody(BaseModel):
    bucket: str
    key: Optional[str] = None
    prefix: Optional[str] = None
    required_exts: Optional[List[str]] = None
    filename_as_id: Optional[bool] = False
    num_files_limit: Optional[int] = None
    aws_access_id: str
    aws_access_secret: str
    aws_session_token: Optional[str] = None
    s3_endpoint_url: Optional[str] = 'https://s3.amazonaws.com'

@app.post('/load-minio-data')
def load_minio_data(loader_body: MinioLoaderBody,):
    try:
        loader = BotoMinioReader(
            bucket=loader_body.bucket,
            key=loader_body.key,
            prefix=loader_body.prefix,
            required_exts=loader_body.required_exts,
            filename_as_id=loader_body.filename_as_id,
            num_files_limit=loader_body.num_files_limit,
            aws_access_id=loader_body.aws_access_id,
            aws_access_secret=loader_body.aws_access_secret,
            aws_session_token=loader_body.aws_session_token,
            s3_endpoint_url=loader_body.s3_endpoint_url
        )
        documents = loader.load_data()
        return {'documents': documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
