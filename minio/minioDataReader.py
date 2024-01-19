from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from base import MinioReader

app = FastAPI()


@app.post('/read_minio', summary='Read files from Minio')
def read_minio(
        bucket: str,
        key: Optional[str] = None,
        prefix: Optional[str] = '',
        file_extractor: Optional[dict] = None,
        required_exts: Optional[List[str]] = None,
        filename_as_id: bool = False,
        num_files_limit: Optional[int] = None,
        file_metadata: Optional[str] = None,  # Changed to string to serialize callable definition
        minio_endpoint: Optional[str] = None,
        minio_secure: bool = False,
        minio_access_key: Optional[str] = None,
        minio_secret_key: Optional[str] = None,
        minio_session_token: Optional[str] = None
):    if minio_endpoint is None or minio_access_key is None or minio_secret_key is None:
        raise HTTPException(status_code=400, detail='Minio credentials are required')

    reader = MinioReader(
        bucket=bucket,
        key=key,
        prefix=prefix,
        file_extractor=file_extractor,
        required_exts=required_exts,
        filename_as_id=filename_as_id,
        num_files_limit=num_files_limit,
        file_metadata=None if file_metadata is None else eval(file_metadata),  # Unsafe, for illustration only
        minio_endpoint=minio_endpoint,
        minio_secure=minio_secure,
        minio_access_key=minio_access_key,
        minio_secret_key=minio_secret_key,
        minio_session_token=minio_session_token
    )

    try:
        data = reader.load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return data
