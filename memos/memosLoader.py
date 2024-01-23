from typing import Dict, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
import llama_hub.memos as MemosReader

app = FastAPI(openapi_url="/api/v1/openapi.json")


class Document(BaseModel):
    text: str
    extra_info: Dict


def get_loader(host: str):
    return MemosReader(host)


@app.get("/load_data", response_model=List[Document])
async def load_data(
    host: str = Query(..., description="Host where memos is deployed"),
    params: Optional[Dict] = None,
):
    loader = get_loader(host)
    return loader.load_data(params)
