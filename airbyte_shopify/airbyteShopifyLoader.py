from typing import Any, Optional
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from llama_hub.airbyte_shopify import AirbyteShopifyReader

app = FastAPI()

def get_api_key(
    api_key_header: str = Security(APIKeyHeader(name='X-API-KEY'))
):
    if api_key_header != "expected_api_key":
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header

@app.post('/load_data')
def load_data(
    stream_name: str,
    config: dict,
    state: Optional[dict] = None,
    key: str = Security(get_api_key)
):
    reader = AirbyteShopifyReader(config=config)
    if state:
        reader.last_state = state
    documents = reader.load_data(stream_name=stream_name)
    return {"documents": documents}

@app.post('/lazy_load_data')
def lazy_load_data(
    stream_name: str,
    config: dict,
    state: Optional[dict] = None,
    key: str = Security(get_api_key)
):
    reader = AirbyteShopifyReader(config=config)
    if state:
        reader.last_state = state
    doc_iter = reader.lazy_load_data(stream_name=stream_name)
    # here you can handle the iteration over doc_iter
    # and return documents one by one or in chunks
    # since this is a naive implementation we will convert it to a list
    documents = list(doc_iter)
    return {"documents": documents}
