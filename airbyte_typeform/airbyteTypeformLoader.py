from typing import Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from llama_hub.airbyte_typeform import AirbyteTypeformReader

api_key_header = APIKeyHeader(name='Authorization', auto_error=True)
app = FastAPI()

def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header != 'Bearer YOUR_SECRET_KEY':
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header

@app.post('/load_data/', summary='Load data from Typeform')
def load_data(
        stream_name: str,
        config: dict,
        state: Optional[dict] = None,
        api_key: str = Depends(get_api_key)
    ) -> List[Any]:
    reader = AirbyteTypeformReader(config=config)
    documents = reader.load_data(stream_name=stream_name, state=state)
    return documents

@app.post('/lazy_load_data/', summary='Lazy load data from Typeform')
def lazy_load_data(
        stream_name: str,
        config: dict,
        state: Optional[dict] = None,
        api_key: str = Depends(get_api_key)
    ) -> Any:
    reader = AirbyteTypeformReader(config=config)
    document_iterator = reader.lazy_load_data(stream_name=stream_name, state=state)
    for document in document_iterator:
        yield document
