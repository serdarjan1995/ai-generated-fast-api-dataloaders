from fastapi import FastAPI, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel
import llama_hub.linear as LinearReader

app = FastAPI(openapi_url="/api/v1/openapi.json")

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class Document(BaseModel):
    text: str
    extra_info: dict


@app.post("/load_data/", response_model=List[Document])
async def load_data(query: str, api_key: APIKeyHeader = Security(api_key_header)):
    print(query)
    linear_reader = LinearReader(api_key=api_key)
    return linear_reader.load_data(query=query)
