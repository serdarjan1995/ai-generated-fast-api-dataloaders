from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel
from typing import List
from llama_index.readers.schema.base import Document
import llama_hub.huggingface.fs as HuggingFaceFSReader


app = FastAPI(openapi_url="/api/v1/openapi.json")
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


class Document(BaseModel):
    text: str


class ErrorModel(BaseModel):
    detail: str


@app.get(
    "/load-dicts",
    summary="Load JSON dictionaries",
    response_model=List[dict],
    responses={404: {"model": ErrorModel}},
)
def get_load_dicts(path: str, api_key: str = Security(api_key_header)):
    try:
        reader = HuggingFaceFSReader()
        return reader.load_dicts(path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/load-df",
    summary="Load a pandas DataFrame",
    response_model=List[dict],
    responses={404: {"model": ErrorModel}},
)
def get_load_df(path: str, api_key: str = Security(api_key_header)):
    try:
        reader = HuggingFaceFSReader()
        df = reader.load_df(path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/load-data",
    summary="Load documents",
    response_model=List[Document],
    responses={404: {"model": ErrorModel}},
)
def get_load_data(path: str, api_key: str = Security(api_key_header)):
    try:
        reader = HuggingFaceFSReader()
        docs = reader.load_data(path)
        return [{"text": doc.text} for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
