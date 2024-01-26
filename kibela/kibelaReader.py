from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
import llama_hub.kibela as KibelaReader
from llama_index.readers.schema.base import Document


app = FastAPI(openapi_url="/api/v1/openapi.json")

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


@app.post("/load_data", response_model=List[Document])
async def load_data(team: str, api_key: str = Security(api_key_header)):
    try:
        kibelaReader = KibelaReader(team, api_key)
        return kibelaReader.load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
