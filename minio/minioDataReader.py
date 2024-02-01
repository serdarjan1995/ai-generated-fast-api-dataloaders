from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import llama_hub.minio as MinioReader

app = FastAPI(openapi_url="/api/v1/openapi.json")


class RequestModel(BaseModel):
    bucket: str
    key: Optional[str] = None
    prefix: Optional[str] = ""
    file_extractor: Optional[dict] = None
    required_exts: Optional[List[str]] = None
    filename_as_id: bool = False
    num_files_limit: Optional[int] = None
    file_metadata: Optional[str] = None
    minio_endpoint: Optional[str] = None
    minio_secure: bool = False
    minio_access_key: Optional[str] = None
    minio_secret_key: Optional[str] = None
    minio_session_token: Optional[str] = None


@app.post("/read_minio", summary="Read files from Minio")
def read_minio(request: RequestModel = Body(...)):
    if (
        request.minio_endpoint is None
        or request.minio_access_key is None
        or request.minio_secret_key is None
    ):
        raise HTTPException(status_code=400, detail="Minio credentials are required")

    reader = MinioReader(
        bucket=request.bucket,
        key=request.key,
        prefix=request.prefix,
        file_extractor=request.file_extractor,
        required_exts=request.required_exts,
        filename_as_id=request.filename_as_id,
        num_files_limit=request.num_files_limit,
        file_metadata=None
        if request.file_metadata is None
        else eval(request.file_metadata),  # Unsafe, for illustration only
        minio_endpoint=request.minio_endpoint,
        minio_secure=request.minio_secure,
        minio_access_key=request.minio_access_key,
        minio_secret_key=request.minio_secret_key,
        minio_session_token=request.minio_session_token,
    )

    try:
        data = reader.load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return data
