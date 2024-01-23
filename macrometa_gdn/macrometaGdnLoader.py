from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
import llama_hub.macrometa_gdn as MacrometaGDNReader

app = FastAPI(openapi_url="/api/v1/openapi.json")

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key_header: str = Depends(API_KEY_HEADER)):
    return api_key_header


class Document(BaseModel):
    text: str
    extra_info: dict


@app.post("/load_data/", response_model=List[Document])
async def load_data_endpoint(
    collection_names: List[str], api_key: APIKey = Depends(get_api_key)
):
    reader = MacrometaGDNReader("https://api-macrometa.io", apikey=api_key)
    try:
        return reader.load_data(collection_list=collection_names)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
