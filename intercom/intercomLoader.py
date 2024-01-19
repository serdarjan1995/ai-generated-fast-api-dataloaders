from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List
import requests
from bs4 import BeautifulSoup

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
    articles = get_all_articles(api_key)
    results = []
    for article_data in articles:
        body = BeautifulSoup(article_data.body, "html.parser").get_text()
        extra_info = {
            "id": article_data.id,
            "title": article_data.title,
            "url": article_data.url,
            "updated_at": article_data.updated_at,
        }
        results.append(Document(text=body, extra_info=extra_info))
    return results


def get_all_articles(api_key: str) -> List[Article]:
    articles = []
    next_page = None
    while True:
        articles_batch, next_page = get_articles_page(api_key, next_page)
        articles.extend(articles_batch)
        if next_page is None:
            break
    return articles


def get_articles_page(api_key: str, next_page: str = None):
    headers = {
        "accept": "application/json",
        "Intercom-Version": "2.8",
        "authorization": f"Bearer {api_key}",
    }
    if next_page is None:
        url = "https://api.intercom.io/articles"
    else:
        url = next_page
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch articles from Intercom",
        )
    response_json = response.json()
    articles = [
        Article(**article_data) for article_data in response_json.get("data", [])
    ]
    next_page = response_json.get("pages", {}).get("next", None)
    return articles, next_page
