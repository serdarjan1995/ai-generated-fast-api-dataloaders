from fastapi import FastAPI, HTTPException, Path, Query
from typing import Optional, List
import json
import requests
from pydantic import BaseModel

app = FastAPI()


class Document(BaseModel):
    text: str
    extra_info: dict


def get_all_articles(zendesk_subdomain: str, locale: str) -> List[Document]:
    articles = []
    next_page = None

    while True:
        response = get_articles_page(zendesk_subdomain, locale, next_page)
        articles.extend(response["articles"])
        next_page = response["next_page"]

        if next_page is None:
            break

    return articles


def get_articles_page(zendesk_subdomain: str, locale: str, next_page: Optional[str] = None):
    if next_page is None:
        url = f"https://{zendesk_subdomain}.zendesk.com/api/v2/help_center/{locale}/articles?per_page=100"
    else:
        url = next_page

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Error fetching articles.")

    response_json = json.loads(response.text)
    next_page = response_json.get("next_page", None)
    articles = response_json.get("articles", [])

    return {"articles": articles, "next_page": next_page}


def get_article_text(article):
    from bs4 import BeautifulSoup
    body = article["body"]
    if body is None:
        return None
    soup = BeautifulSoup(body, "html.parser")
    body = soup.get_text()
    return body


@app.get("/articles", summary="Get all articles from Zendesk", description="Fetch all articles from a given Zendesk subdomain and locale.")
async def read_articles(subdomain: str = Query(..., description="Zendesk subdomain"), locale: str = Query("en-us", description="Locale of the articles")) -> List[Document]:
    articles = get_all_articles(subdomain, locale)
    results = []
    for article in articles:
        body_text = get_article_text(article)
        if body_text is not None:
            extra_info = {
                "id": article["id"],
                "title": article["title"],
                "url": article["html_url"],
                "updated_at": article["updated_at"],
            }
            results.append(
                Document(
                    text=body_text,
                    extra_info=extra_info,
                )
            )
    return results
