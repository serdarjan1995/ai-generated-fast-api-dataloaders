from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Optional
from pydantic import BaseModel
from base import AirbyteSalesforceReader

app = FastAPI()

API_KEY = "your_api_key"
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


class SalesforceConfig(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    start_date: str
    is_sandbox: bool
    streams_criteria: List[dict]


class Document(BaseModel):
    doc_id: str
    text: str
    extra_info: dict


@app.post("/load_data/", response_model=List[Document])
def load_data(
    stream_name: str,
    config: SalesforceConfig,
    state: Optional[dict] = None,
    key: str = Depends(get_api_key)
):
    reader = AirbyteSalesforceReader(config.dict())
    return list(reader.load_data(stream_name=stream_name, state=state))


@app.post("/lazy_load_data/")
def lazy_load_data(
    stream_name: str,
    config: SalesforceConfig,
    state: Optional[dict] = None,
    key: str = Depends(get_api_key)
):
    reader = AirbyteSalesforceReader(config.dict())
    for document in reader.lazy_load_data(stream_name=stream_name, state=state):
        yield document
