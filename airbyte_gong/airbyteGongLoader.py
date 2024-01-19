from fastapi import FastAPI, Body, Depends
from llama_index import Document
from pydantic import BaseModel
from llama_hub.airbyte_gong import AirbyteGongReader
from typing import Optional, List

class GongConfig(BaseModel):
    access_key: str
    access_key_secret: str
    start_date: Optional[str] = None

app = FastAPI()


@app.post('/load_data/',
           summary='Loads data from Gong.',
           description='Loads documents from Gong based on the provided stream name and optional state.')
def load_data(
    stream_name: str = Body(..., description='The name of the stream to load data from.'),
    state: Optional[str] = Body(None, description='The state to be used for incremental loading.'),
    config: GongConfig = Body(..., description='JSON dict containing GongConfig schema')
):

    reader = AirbyteGongReader(config=config.dict())
    return list(reader.load_data(stream_name=stream_name, state=state))

@app.post('/lazy_load_data/',
           summary='Lazily loads data from Gong.',
           description='Returns an iterator of documents from Gong without keeping all in memory.')
def lazy_load_data(
    stream_name: str = Body(..., description='The name of the stream to lazily load data from.'),
    config: GongConfig = Body(..., description='JSON dict containing GongConfig schema')
):
    reader = AirbyteGongReader(config=config.dict())
    return list(reader.lazy_load_data(stream_name=stream_name))
