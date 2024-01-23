from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Union
import llama_hub.jsondata as JsonDataReader


app = FastAPI(openapi_url="/api/v1/openapi.json")


@app.post("/load_json/", summary="Load JSON data", response_model=List[str])
def load_json(
    data: Union[str, dict],
    api_key: APIKeyHeader = Security(
        APIKeyHeader(name="access_token", auto_error=True)
    ),
):
    """Load JSON data from a JSON string or a dictionary.

    - **data**: JSON string or dict to be processed.
    - **access_token**: API key for secure access.
    """
    try:
        reader = JsonDataReader()
        documents = reader.load_data(data)
        return [doc.text for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
