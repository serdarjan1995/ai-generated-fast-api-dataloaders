from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

app = FastAPI()
security = HTTPBasic()

ATOM_PUB_ENTRY_URL = "{root_endpoint}/entry"


class Article(BaseModel):
    title: str
    content: str
    published: str
    url: str


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    return credentials.username


@app.post('/load_data/', response_model=List[Article])
def load_data(root_endpoint: str, username: str = Depends(get_current_username), password: str = Depends(security)):
    articles: List[Article] = []
    page_url = ATOM_PUB_ENTRY_URL.format(root_endpoint=root_endpoint)

    while True:
        res = get_articles(page_url, username, password)
        articles += res.get("articles")
        page_url = res.get("next_page")
        if page_url is None:
            break

    return articles


def get_articles(url: str, username: str, password: str) -> dict:
    articles: List[Article] = []
    next_page: Optional[str] = None

    res = requests.get(url, auth=(username, password))
    soup = BeautifulSoup(res.text, "xml")
    for entry in soup.find_all("entry"):
        if entry.find("app:control").find("app:draft").string == "yes":
            continue
        article = Article(
            title=entry.find("title").string,
            published=entry.find("published").string,
            url=entry.find("link", rel="alternate")["href"],
            content=BeautifulSoup(entry.find("content").string, "html.parser").get_text().strip()
            if entry.find("content").get("type") == "text/html"
            else entry.find("content").string.strip()
        )
        articles.append(article)

    next_link = soup.find("link", attrs={"rel": "next"})
    if next_link:
        next_page = next_link.get("href")

    return {"articles": articles, "next_page": next_page}
