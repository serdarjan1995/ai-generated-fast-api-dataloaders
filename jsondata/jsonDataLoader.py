from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Union
import llama_hub.jsondata as JsonDataReader
from llama_index.readers.schema.base import Document

app = FastAPI(openapi_url="/api/v1/openapi.json")


@app.post("/load_json/", summary="Load JSON data", response_model=List[Document])
def load_json(
    data: Union[str, dict],
):
    try:
        reader = JsonDataReader()
        return reader.load_data(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
