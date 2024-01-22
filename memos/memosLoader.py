from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
import requests

app = FastAPI(openapi_url="/api/v1/openapi.json")


class Document(BaseModel):
    text: str
    extra_info: Dict


class MemosReader:
    def __init__(self, host: str):
        self._memoUrl = host.rstrip("/") + "/api/memo"

    def load_data(self, params: Optional[Dict] = None):
        if params is None:
            params = {}
        realUrl = self._memoUrl + ("/all" if not params else "")
        try:
            response = requests.get(realUrl, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=str(e))

        if "data" not in data:
            raise HTTPException(status_code=500, detail="Invalid Memo response")

        documents = [
            Document(
                text=memo["content"],
                extra_info={
                    "creator": memo["creator"],
                    "resource_list": memo["resourceList"],
                    id: memo["id"],
                },
            )
            for memo in data["data"]
        ]
        return documents


def get_loader(host: str):
    return MemosReader(host)


@app.get("/load_data", response_model=List[Document])
async def load_data(
    host: str = Query(..., description="Host where memos is deployed"),
    params: Optional[Dict] = None,
):
    loader = get_loader(host)
    return loader.load_data(params)
