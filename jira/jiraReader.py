from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import llama_hub.jira as JiraReader

from jira import JIRA

app = FastAPI(openapi_url="/api/v1/openapi.json")

api_key_header = APIKeyHeader(name="api_token", auto_error=False)


class BasicAuth(BaseModel):
    email: str
    api_token: str
    server_url: str


class Oauth2(BaseModel):
    cloud_id: str
    api_token: str


class Document(BaseModel):
    text: str
    extra_info: dict


@app.post("/load_data", response_model=List[Document])
async def load_data(
    query: str,
    basic_auth: Optional[BasicAuth] = None,
    oauth: Optional[Oauth2] = None,
):
    try:
        jiraReader = JiraReader(basic_auth, oauth)
        return jiraReader.load_data(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
