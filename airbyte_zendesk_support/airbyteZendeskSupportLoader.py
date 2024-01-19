from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, Any, Optional, List, Iterator
from llama_hub.airbyte_zendesk_support import AirbyteZendeskSupportReader
from fastapi.security.api_key import APIKeyHeader

app = FastAPI()

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=True)


def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header != 'expected_api_key':
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header


@app.post('/load_data/{stream_name}', summary='Load data from Zendesk Support')
def load_data(
    stream_name: str,
    config: Dict[str, Any],
    state: Optional[Dict[str, Any]] = None,
    apiKey: str = Depends(get_api_key)
) -> List[Dict[str, Any]]:
    reader = AirbyteZendeskSupportReader(config)
    documents = reader.load_data(stream_name=stream_name, state=state)
    return documents


@app.post('/lazy_load_data/{stream_name}', summary='Load data from Zendesk Support using lazy loading')
def lazy_load_data(
    stream_name: str,
    config: Dict[str, Any],
    apiKey: str = Depends(get_api_key)
) -> Iterator[Dict[str, Any]]:
    reader = AirbyteZendeskSupportReader(config)
    return reader.lazy_load_data(stream_name=stream_name)
