from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
import requests
from typing import Optional, List

app = FastAPI(openapi_url="/api/v1/openapi.json")


class NodeWithScoreModel(BaseModel):
    node: dict
    score: Optional[float] = None


class ResponseModel(BaseModel):
    response: str
    source_nodes: List[NodeWithScoreModel]
    query: Optional[str] = None


class RequestModel(BaseModel):
    webhook_url: str
    response: ResponseModel = None


@app.post(
    "/pass-response-to-webhook/",
    summary="Pass response to Make.com webhook",
    description="Pass a response object to a specified Make.com webhook url.",
)
async def pass_response_to_webhook(
    item: RequestModel = Body(...),
):
    json_dict = {
        "response": item.response.response,
        "source_nodes": [node.dict() for node in item.response.source_nodes],
        "query": item.response.query,
    }
    r = requests.post(item.webhook_url, json=json_dict)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=str(e))
    return {"message": "Response passed to webhook successfully."}
