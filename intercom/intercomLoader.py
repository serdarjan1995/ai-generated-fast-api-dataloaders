from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List
import llama_hub.intercom as IntercomReader

API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


def get_api_key(api_key_header: str = Security(api_key_header)):
    return api_key_header


# app = FastAPI()
app = FastAPI(openapi_url="/api/v1/openapi.json")


class Document(BaseModel):
    text: str
    extra_info: dict


class Article(BaseModel):
    id: str
    title: str
    url: str
    updated_at: str
    body: str


@app.get(
    "/load_data",
    response_model=List[Document],
    summary="Load Data from Intercom",
    description="Fetch and parse help articles from Intercom using the Intercom API.",
)
def load_data(api_key: str = Security(get_api_key)):
    try:
        intercomReader = IntercomReader(api_key)
        return intercomReader.load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_all_articles(api_key: str) -> List[Article]:
    try:
        intercomReader = IntercomReader(api_key)
        return intercomReader.get_all_articles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_articles_page(api_key: str, next_page: str = None):
    try:
        intercomReader = IntercomReader(api_key)
        return intercomReader.get_articles_page(next_page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
