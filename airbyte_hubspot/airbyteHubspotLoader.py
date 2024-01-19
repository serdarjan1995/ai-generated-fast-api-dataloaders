from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi.security.api_key import APIKeyHeader

from base import AirbyteHubspotReader

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title='Airbyte Hubspot Loader')


def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header == "fake_api_key":
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


class HubspotConfig(BaseModel):
    start_date: str = Field(..., description="Date from which to start retrieving records in ISO format, e.g. 2020-10-20T00:00:00Z", example="2020-10-20T00:00:00Z")
    credentials: dict = Field(..., description="Credentials object containing the access token.")


@app.post('/load_data/', response_model=List)
def load_data(
    stream_name: str,
    config: HubspotConfig = Depends(),
    api_key: str = Depends(get_api_key)
):
    reader = AirbyteHubspotReader(config=config.dict(), record_handler=None)
    try:
        documents = reader.load_data(stream_name=stream_name)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/load_incremental/', response_model=List)
def load_incremental(
    stream_name: str,
    state: Optional[str] = None,
    config: HubspotConfig = Depends(),
    api_key: str = Depends(get_api_key)
):
    reader = AirbyteHubspotReader(config=config.dict(), record_handler=None)
    try:
        if state:
            documents = reader.load_data(stream_name=stream_name, state=state)
        else:
            documents = reader.load_data(stream_name=stream_name)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
