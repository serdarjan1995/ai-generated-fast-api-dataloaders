from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from joplin_api import JoplinApi

# app = FastAPI()
app = FastAPI(openapi_url="/api/v1/openapi.json")

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


class Document(BaseModel):
    text: str
    extra_info: dict


@app.get(
    "/load_folders/",
    summary="Load folders",
    description="Load folders from Joplin with the provided API key.",
)
def load_folders(api_key: str = Security(api_key_header)):
    try:
        joplin = JoplinApi(token=api_key)
        joplin.ping()
        return joplin.get_folders()
    except Exception as e:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.get(
    "/load_notes/",
    summary="Load notes",
    description="Load notes from Joplin with the provided API key.",
)
def load_folders(api_key: str = Security(api_key_header)):
    try:
        joplin = JoplinApi(token=api_key)
        joplin.ping()
        return joplin.get_notes()
    except Exception as e:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.get(
    "/load_tags/",
    summary="Load tags",
    description="Load tags from Joplin with the provided API key.",
)
def load_folders(api_key: str = Security(api_key_header)):
    try:
        joplin = JoplinApi(token=api_key)
        joplin.ping()
        return joplin.get_tags()
    except Exception as e:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
