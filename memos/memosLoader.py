from typing import Dict, List, Optional
from fastapi import FastAPI, Body
from pydantic import BaseModel
import llama_hub.memos as MemosReader

app = FastAPI(openapi_url="/api/v1/openapi.json")


class Document(BaseModel):
    text: str
    extra_info: Dict


class RequestModel(BaseModel):
    host: str
    params: Optional[Dict] = None


def get_loader(host: str):
    return MemosReader(host)


@app.get("/load_data", response_model=List[Document])
async def load_data(request: RequestModel = Body(...)):
    loader = get_loader(request.host)
    return loader.load_data(request.params)
