from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import os
from zulip_loader.base import ZulipReader

ZULIP_EMAIL = os.getenv('ZULIP_EMAIL')
ZULIP_DOMAIN = os.getenv('ZULIP_DOMAIN')

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == os.environ.get('ZULIP_TOKEN'):
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class Streams(BaseModel):
    stream_names: List[str]
    reverse_chronological: Optional[bool]

@app.post('/load_data/', summary='Load data from Zulip streams', description='Loads messages from Zulip streams.', response_model=List)
def load_data(streams: Streams, api_key: str = Depends(get_api_key)):
    reader = ZulipReader(ZULIP_EMAIL, ZULIP_DOMAIN)
    if not streams.stream_names:
        streams.stream_names = reader.get_all_streams()
    return reader.load_data(streams.stream_names, reverse_chronological=streams.reverse_chronological if streams.reverse_chronological is not None else True)
