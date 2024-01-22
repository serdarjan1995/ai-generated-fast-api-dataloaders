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


@app.post(
    "/pass-response-to-webhook/",
    summary="Pass response to Make.com webhook",
    description="Pass a response object to a specified Make.com webhook url.",
)
async def pass_response_to_webhook(
    webhook_url: str = Query(
        ..., description="Webhook URL to which the response will be sent"
    ),
    response: ResponseModel = Body(
        ..., description="Response object containing the response and source nodes"
    ),
    query: Optional[str] = Body(None, description="Optional query string"),
):
    json_dict = {
        "response": response.response,
        "source_nodes": [node.dict() for node in response.source_nodes],
        "query": response.query,
    }
    r = requests.post(webhook_url, json=json_dict)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=r.status_code, detail=str(e))
    return {"message": "Response passed to webhook successfully."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
